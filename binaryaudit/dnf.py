import json
import os
import rpmfile
import shutil
import subprocess
import time
import urllib.request

from binaryaudit import abicheck
from binaryaudit import run
from binaryaudit import util


def process_downloads(source_dir, new_json_file, old_json_file, output_dir, build_id, product_id, db_conn, cleanup=True):
    ''' Finds and downloads older versions of RPMs.

        Parameters:
            source_dir (str): The path to the input directory of RPMs
            new_json_file (str): The name of the JSON file containing the newer set of packages after so based filtering
            old_json_file (str): The name of the JSON file containing the older set of packages
            output_dir (str): The path to the output directory of abipkgdiff
            build_id (str): The build id
            product_id (str): The product id
            db_conn: The db connection

        Returns:
            overall_status (str): Returns "fail" if an incompatibility is found in at least 1 RPM, otherwise returns "pass"
    '''
    try:
        overall_status = "pass"
        conf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../conf")
        if not os.path.exists(source_dir + "old"):
            os.mkdir(source_dir + "old")
        old_rpm_dict = {}
        with open(new_json_file, "r") as file:
            data = json.load(file)
        for key, values in data.items():
            for value in values:
                with rpmfile.open(source_dir + value) as rpm:
                    name = rpm.headers.get("name")
                old_rpm_name = download(key, source_dir, name, old_rpm_dict)
            if old_rpm_name == "":
                continue
            with open(old_json_file, "w") as outputFile:
                json.dump(old_rpm_dict, outputFile, indent=2)
            ret_status = generate_abidiffs(key, source_dir, new_json_file, old_json_file, output_dir,
                                           conf_dir, build_id, product_id, db_conn, cleanup)
            util.note("Status: " + ret_status)
            if ret_status == "INCOMPATIBLE_CHANGE":
                overall_status = "fail"
    finally:
        if cleanup is True:
            try:
                shutil.rmtree(source_dir + "old")
                os.remove(new_json_file)
                os.remove(old_json_file)
                os.remove("output_file")
            except OSError:
                pass
        return overall_status


def download(key, source_dir, name, old_rpm_dict):
    ''' Finds and downloads older versions of RPMs.

        Parameters:
            key (str): The source name for the group of RPMs
            source_dir (str): The path to the input directory of RPMs
            name: The name of the RPM
            old_rpm_dict: The dictionary containing the older set of packages
    '''
    docker, docker_exit_code = run.run_command_docker(["/usr/bin/dnf", "repoquery", "--quiet", "--latest-limit=1", name],
                                                      None, subprocess.PIPE)
    old_rpm_name = docker.stdout.read().decode('utf-8')
    if old_rpm_name == "":
        return old_rpm_name
    old_rpm_name = old_rpm_name.replace("\r\n", "")
    docker_loc, docker_loc_exit_code = run.run_command_docker(["/usr/bin/dnf", "repoquery", "--quiet",
                                                              "--location", "--latest-limit=1", name], None, subprocess.PIPE)
    url = docker_loc.stdout.read().decode('utf-8')
    util.debug("url: {}".format(url))
    urllib.request.urlretrieve(url, source_dir + "old/" + old_rpm_name)
    old_rpm_dict.setdefault(key, []).append(old_rpm_name)
    return old_rpm_name


def generate_abidiffs(key, source_dir, new_json_file, old_json_file, output_dir,
                      conf_dir, build_id, product_id, db_conn, cleanup=True):
    ''' Runs abipkgdiff against the grouped packages.

        Parameters:
            key (str): The source name for the group of RPMs
            source_dir (str): The path to the input directory of RPMs
            new_json_file (str): The name of the JSON file containing the newer set of packages
            old_json_file (str): The name of the JSON file containing the older set of packages
            output_dir (str): The path to the output directory of abipkgdiff
            conf_dir (str): The absolute path to the conf directory
            build_id (str): The build id
            product_id (str): The product id
            db_conn: The db connection
            cleanup (bool): An option to remove temporary files and directories after running


        Returns:
            status (str): Returns "fail" if an incompatibility found, otherwise returns "pass"
    '''
    # new_... handles the newer set of packages
    # old_... handles the older set of packages
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    with open(new_json_file, "r") as new_file:
        new_data = json.load(new_file)
    with open(old_json_file, "r") as old_file:
        old_data = json.load(old_file)
    rpms_with_so, cmd_supporting_args = sortRPMs(key, source_dir, new_data, old_data)
    i = 0
    for rpm in rpms_with_so:
        if i % 2 == 0:
            command_list = ["abipkgdiff", "--suppressions", conf_dir + "/suppressions.conf"]
            old_main_rpm = rpm
        i += 1
        command_list.append(rpm)
        if i % 2 == 1:
            continue
        new_main_rpm = rpm
        for arg in cmd_supporting_args:
            command_list.append(arg)
        with open("output_file", "w") as output_file:
            start_time = time.time()
            abipkgdiff, abipkgdiff_exit_code = run.run_command(command_list, None, output_file)
            exec_time = time.time()-start_time
            with rpmfile.open(old_main_rpm) as rpm:
                name = rpm.headers.get('name').decode('utf-8')
                old_version = rpm.headers.get('version').decode('utf-8')
                old_release = rpm.headers.get('release').decode('utf-8')
            with rpmfile.open(new_main_rpm) as rpm:
                new_version = rpm.headers.get('version').decode('utf-8')
                new_release = rpm.headers.get('release').decode('utf-8')
            old_VR = old_version + "-" + old_release
            new_VR = new_version + "-" + new_release
            out = ""
            if abipkgdiff_exit_code != 0:
                util.note("Incompatibility found between " + name + "-" + old_VR + " and " + name + "-" + new_VR)
                fileName = name + "__" + old_VR + "__" + new_VR + ".abidiff"
                os.rename("output_file", output_dir + fileName)
                with open(output_dir + fileName) as f:
                    out = f.read()
        status = abicheck.diff_get_bit(abipkgdiff_exit_code)
        insert_db(db_conn, build_id, product_id, name, old_VR, new_VR, exec_time, status, out)

    if cleanup is True:
        for value in old_data[key]:
            os.remove(source_dir + "old/" + value)
    return status


def sortRPMs(key, source_dir, new_data, old_data):
    ''' Sorts the RPMs depnding on whether or not they have
        "debuginfo" or "devel" in their name.

        Parameters:
            key (str): The source name for the group of RPMs
            source_dir (str): The path to the input directory of RPMs
            new_data (dict): The dictionary containing the newer set of packages
            old_data (dict): The dictionary containing the older set of packages

    Returns:
            rpms_with_so (list): The list of RPMs not containing "debuginfo" or "devel" in their name
            cmd_supporting_args (list): The list of RPMs containing "debuginfo" or "devel" in their name
    '''
    rpms_with_so = []
    cmd_supporting_args = []
    count = -1
    for value in old_data[key]:
        count += 1
        if "-debuginfo-" in value:
            cmd_supporting_args.append("--d1")
            cmd_supporting_args.append(source_dir + "old/" + value)
            cmd_supporting_args.append("--d2")
            cmd_supporting_args.append(source_dir + new_data[key][count])
        elif "-devel-" in value:
            cmd_supporting_args.append("--devel1")
            cmd_supporting_args.append(source_dir + "old/" + value)
            cmd_supporting_args.append("--devel2")
            cmd_supporting_args.append(source_dir + new_data[key][count])
        else:
            rpms_with_so.append(source_dir + "old/" + value)
            rpms_with_so.append(source_dir + new_data[key][count])
    return rpms_with_so, cmd_supporting_args


def insert_db(db_conn, build_id, product_id, name, old_VR, new_VR, exec_time, status, out):
    try:
        if db_conn.is_db_connected:
            db_conn.insert_ba_transaction_details(build_id, product_id, name, old_VR, new_VR, exec_time, status, out)
            util.debug("Inserted into database: {}".format(name))
        else:
            util.debug("Not connected")
    except Exception:
        pass
