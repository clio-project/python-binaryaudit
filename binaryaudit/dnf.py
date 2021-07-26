
# Download older versions of RPMs from remote repo

from binaryaudit import run

import json
import subprocess
import urllib.request

def download(source_dir, json_file):
    d_logger=create_logger("abidiff_download")
    mkdir, mkdir_exit_code = run.run_command(["mkdir", source_dir + "old"], None, None)
    old_json_file = "old_" + json_file
    old_rpm_dict = {}
    file = open(json_file)
    data = json.load(file)
    file.close()
    for key, values in data.items():
        for value in values:
            proc, proc_exit_code = run.run_command(["rpm", "-qpi", source_dir + value], None, subprocess.PIPE)
            d_logger.debug("Output = {}, exit code = {}".format(proc,proc_exit_code))
            grep, grep_exit_code = run.run_command(["grep", "Name"], proc.stdout, subprocess.PIPE)
            name = grep.stdout.read()
            name = name.replace(b"Name        : ", b"")
            name = name.replace(b"\n", b"")
            docker, docker_exit_code = run.run_command(["sudo", "docker", "run", "-t", "--rm", "mariner:abidiff", "/usr/bin/dnf", "repoquery", "--quiet", "--latest-limit=1", name], None, subprocess.PIPE)
            old_rpm_name = docker.stdout.read().decode('utf-8')
            if old_rpm_name == "":
                continue
            old_rpm_name = old_rpm_name.replace("\r\n", "")
            docker_loc, docker_loc_exit_code = run.run_command(["sudo", "docker", "run", "-t", "--rm", "mariner:abidiff", "/usr/bin/dnf", "repoquery", "--quiet", "--location", "--latest-limit=1", name], None, subprocess.PIPE)
            url = docker_loc.stdout.read().decode('utf-8')
            urllib.request.urlretrieve(url, source_dir + "/old/" + old_rpm_name)
            old_rpm_dict.setdefault(key, []).append(old_rpm_name)
    with open(old_json_file, "w") as outputFile:
        json.dump(old_rpm_dict, outputFile, indent=2)

