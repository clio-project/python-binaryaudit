from binaryaudit import run
from binaryaudit import util

import json
import rpmfile
import os
import subprocess
import urllib.request

def download(source_dir, new_json_file, old_json_file, debug):
    ''' Finds and downloads older versions of RPMs.

        Parameters:
            source_dir (str): The path to the input directory of RPMs
            json_file (str): The name of the JSON file containing the grouped packages after so based filtering.
            debug: An option to print debug messages
    '''
    os.mkdir(source_dir + "old")
    old_rpm_dict = {}
    with open(new_json_file, "r") as file:
        data = json.load(file)
    for key, values in data.items():
        for value in values:
            with rpmfile.open(source_dir + value) as rpm:
                name = rpm.headers.get("name")            
            docker, docker_exit_code = run.run_command(["sudo", "docker", "run", "-t", "--rm", "mariner:abidiff", "/usr/bin/dnf", "repoquery", "--quiet", "--latest-limit=1", name], None, subprocess.PIPE, debug)
            old_rpm_name = docker.stdout.read().decode('utf-8')
            if old_rpm_name == "":
                continue
            old_rpm_name = old_rpm_name.replace("\r\n", "")
            docker_loc, docker_loc_exit_code = run.run_command(["sudo", "docker", "run", "-t", "--rm", "mariner:abidiff", "/usr/bin/dnf", "repoquery", "--quiet", "--location", "--latest-limit=1", name], None, subprocess.PIPE, debug)
            url = docker_loc.stdout.read().decode('utf-8')
            if debug:
                util.set_verbosity(True)
                util.debug("url: {}".format(url))
            urllib.request.urlretrieve(url, source_dir + "/old/" + old_rpm_name)
            old_rpm_dict.setdefault(key, []).append(old_rpm_name)
        if old_rpm_name == "":
            continue
        with open(old_json_file, "w") as outputFile:
            json.dump(old_rpm_dict, outputFile, indent=2)
        generate_abidiffs(key, source_dir, new_json_file, old_json_file, debug)
    os.rmdir(source_dir + "old")
    os.remove(new_json_file)
    os.remove(old_json_file)

def generate_abidiffs(key, source_dir, new_json_file, old_json_file, debug):
    ''' Runs abipkgdiff against the grouped packages.

        Parameters:
            key (str): The source name for the group of RPMs
            source_dir (str): The path to the input directory of RPMs
            json_file (str): The name of the JSON file containing the grouped packages
            debug: An option to print debug messages
    '''
    # new_... handles the newer set of packages
    # old_... handles the older set of packages
    if not os.path.exists("output_abidiffs"):
        os.mkdir("output_abidiffs")
    with open(new_json_file, "r") as new_file:
        new_data = json.load(new_file)
    with open(old_json_file, "r") as old_file:
        old_data = json.load(old_file)
    cmd_supporting_args = []
    rpms_with_so = []
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
            old_main_rpm = source_dir + "old/" + value
            new_main_rpm = source_dir + new_data[key][count]
            rpms_with_so.append(source_dir + "old/" + value)
            rpms_with_so.append(source_dir + new_data[key][count])
    i = 0
    for rpm in rpms_with_so:
        if i%2 == 0:
            command_list = ["abipkgdiff"]
        i += 1
        command_list.append(rpm)
        if i%2 == 1:
            continue
        for arg in cmd_supporting_args:
            command_list.append(arg)
        with open("output_file", "w") as output_file:
            abipkgdiff, abipkgdiff_exit_code = run.run_command(command_list, None, output_file, debug)
            if abipkgdiff_exit_code != 0:
                with rpmfile.open(old_main_rpm) as rpm:
                    fileName = rpm.headers.get('name').decode('utf-8') + "__" + rpm.headers.get('version').decode('utf-8') + "-" + rpm.headers.get('release').decode('utf-8') + "__"
                with rpmfile.open(new_main_rpm) as rpm:
                    fileName += rpm.headers.get('version').decode('utf-8') + "-" + rpm.headers.get('release').decode('utf-8') + ".abidiff"
                os.rename("output_file", "output_abidiffs/" + fileName)
    for value in old_data[key]:
        os.remove(source_dir + "old/" + value)
    output_file.close()
