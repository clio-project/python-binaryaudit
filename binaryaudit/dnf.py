from binaryaudit import run
from binaryaudit import util

import json
import os
import rpmfile
import shutil
import subprocess
import urllib.request


def process_downloads(source_dir, new_json_file, old_json_file, output_dir, cleanup=True):
    ''' Finds and downloads older versions of RPMs.

        Parameters:
            source_dir (str): The path to the input directory of RPMs
            new_json_file (str): The name of the JSON file containing the newer set of packages after so based filtering
            old_json_file (str): The name of the JSON file containing the older set of packages
            output_dir (str): The path to the output directory of abipkgdiff
    '''
    try:
        conf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "conf")
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
            generate_abidiffs(key, source_dir, new_json_file, old_json_file, output_dir, conf_dir, cleanup)
    finally:
        if cleanup is True:
            try:
                shutil.rmtree(source_dir + "old")
                os.remove(new_json_file)
                os.remove(old_json_file)
                os.remove("output_file")
            except OSError:
                pass


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


def generate_abidiffs(key, source_dir, new_json_file, old_json_file, output_dir, conf_dir, cleanup=True):
    ''' Runs abipkgdiff against the grouped packages.

        Parameters:
            key (str): The source name for the group of RPMs
            source_dir (str): The path to the input directory of RPMs
            new_json_file (str): The name of the JSON file containing the newer set of packages
            old_json_file (str): The name of the JSON file containing the older set of packages
            output_dir (str): The path to the output directory of abipkgdiff
            conf_dir (str): The absolute path to the conf directory
            cleanup (bool): An option to remove temporary files and directories after running

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
            abipkgdiff, abipkgdiff_exit_code = run.run_command(command_list, None, output_file)
            if abipkgdiff_exit_code != 0:
                with rpmfile.open(old_main_rpm) as rpm:
                    name = rpm.headers.get('name').decode('utf-8')
                    old_version = rpm.headers.get('version').decode('utf-8')
                    old_release = rpm.headers.get('release').decode('utf-8')
                with rpmfile.open(new_main_rpm) as rpm:
                    new_version = rpm.headers.get('version').decode('utf-8')
                    new_release = rpm.headers.get('release').decode('utf-8')
                print("Incompatibility found between " + name + "-" + old_version + "-" + old_release
                      + " and " + name + "-" + new_version + "-" + new_release)
                fileName = name + "__" + old_version + "-" + old_release + "__" + new_version + "-" + new_release + ".abidiff"
                os.rename("output_file", output_dir + fileName)
    if cleanup is True:
        for value in old_data[key]:
            os.remove(source_dir + "old/" + value)


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