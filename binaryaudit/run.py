from binaryaudit import conf
from binaryaudit import util
import subprocess


def run_command(cmd, input, output):
    ''' Runs command and gets output.

    Parameters:
        cmd (list): The command to be run.
        input: The input for stdin of Popen.
        output: The output for stdout of Popen.
    Returns:
        poen_output: The output of cmd
        exit_code: The exit code of cmd.
    '''
    popen_output = subprocess.Popen(cmd, stdin=input, stdout=output)
    popen_output.wait()
    exit_code = popen_output.returncode
    util.debug("command: {}".format(cmd))
    util.debug("exit_code: {}".format(exit_code))
    return popen_output, exit_code


def run_command_docker(cmd, input, output):
    ''' Runs command in docker container and gets output.
    Parameters:
        cmd (list): The command to be run.
        input: The input for stdin of Popen.
        output: The output for stdout of Popen.
    Returns:
        poen_output: The output of cmd
        exit_code: The exit code of cmd.
    '''
    docker_img = conf.get_config("Mariner", "docker_image")
    docker_cmd_list = ["sudo", "docker", "run", "-t", "--rm"]
    docker_cmd_list.append(docker_img)
    docker_cmd_list.extend(cmd)
    popen_output = subprocess.Popen(docker_cmd_list, stdin=input, stdout=output)
    popen_output.wait()
    exit_code = popen_output.returncode
    util.debug("command: {}".format(docker_cmd_list))
    util.debug("exit_code: {}".format(exit_code))
    return popen_output, exit_code
