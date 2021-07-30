from binaryaudit import run

import json
import re
import rpmfile
import os
import subprocess
import urllib.request

def download(source_dir, json_file, debug):
    ''' Finds and downloads older versions of RPMs.

        Parameters:
            source_dir (str): The path to the input directory of RPMs
            json_file (str): The name of the JSON file containing the grouped packages
            debug: An option to print debug messages
    '''
    os.mkdir(source_dir + "old")
    old_json_file = "old_" + json_file
    old_rpm_dict = {}
    file = open(json_file)
    data = json.load(file)
    file.close()
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
            urllib.request.urlretrieve(url, source_dir + "/old/" + old_rpm_name)
            old_rpm_dict.setdefault(key, []).append(old_rpm_name)
        if old_rpm_name == "":
            continue
        with open(old_json_file, "w") as outputFile:
            json.dump(old_rpm_dict, outputFile, indent=2)
        review_abidiffs(key, source_dir, json_file, debug)
    os.rmdir(source_dir + "old")

def review_abidiffs(key, source_dir, json_file, debug):
    ''' Runs abipkgdiff against the grouped packages.

        Parameters:
            key (str): The source name for the group of RPMs
            source_dir (str): The path to the input directory of RPMs
            json_file (str): The name of the JSON file containing the grouped packages
            debug: An option to print debug messages
    '''
    output_file = open("output_file", "w")
    new_file = open(json_file)
    new_data = json.load(new_file)
    new_file.close()
    old_file = open("old_" + json_file)
    old_data = json.load(old_file)
    old_file.close()
    command_list = ["abipkgdiff"]
    del command_list[1:]
    count = -1
    for values in old_data[key]:
        if count >= 0:
            curr = re.split(r'(\d+)', values)[0]
            prev = re.split(r'(\d+)', old_data[key][count])[0]
            if "debuginfo-" in curr:
                curr = curr.replace("debuginfo-", "")
            elif "devel-" in curr:
                curr = curr.replace("devel-", "")
            if "debuginfo-" in prev:
                prev = prev.replace("debuginfo-", "")
            elif "devel-" in prev:
                prev = prev.replace("devel-", "")
            if curr != prev:
                continue
        count += 1
        if "-debuginfo-" in values:
            command_list.append("--d1")
            command_list.append(source_dir + "old/" + values)
            command_list.append("--d2")
            command_list.append(source_dir + new_data[key][count])
        elif "-devel-" in values:
            command_list.append("--devel1")
            command_list.append(source_dir + "old/" + values)
            command_list.append("--devel2")
            command_list.append(source_dir + new_data[key][count])
        else:
            old_main_rpm = source_dir + "old/" + values
            new_main_rpm = source_dir + new_data[key][count]
            command_list.append(source_dir + "old/" + values)
            command_list.append(source_dir + new_data[key][count])
    if len(command_list) == 3 or len(command_list) == 7 or len(command_list) == 11:
        abipkgdiff, abipkgdiff_exit_code = run.run_command(command_list, None, output_file, debug)
        if abipkgdiff_exit_code != 0:
            with rpmfile.open(old_main_rpm) as rpm:
                fileName = rpm.headers.get('name').decode('utf-8') + "__" + rpm.headers.get('version').decode('utf-8') + "-" + rpm.headers.get('release').decode('utf-8') + "__"
            with rpmfile.open(new_main_rpm) as rpm:
                fileName += rpm.headers.get('version').decode('utf-8') + "-" + rpm.headers.get('release').decode('utf-8') + ".abidiff"
            os.rename("output_file", fileName)
    for i in range(0, count + 1):
        os.remove(source_dir + "old/" + old_data[key][0])
        del old_data[key][0]
    output_file.close()
    if  len(old_data[key]) != 0:
        print("again")
        open("old_" + json_file, "w").write(json.dumps(old_data, indent=2))
        review_abidiffs(key, source_dir, json_file, debug)
 
