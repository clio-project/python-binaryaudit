from binaryaudit import util
import subprocess

def run_command(cmd, input, output):
    ''' Runs commands and gets output.

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
