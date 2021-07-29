from binaryaudit import util
import subprocess

def run_command(cmd, input, output, debug):
    ''' Runs commands and gets output.

    Parameters:
        cmd (array): The command to be run.
        input: The input for stdin of Popen.
        output: The output for stdout of Popen.
        debug: An option to print debug messages
    Returns:
        poen_output: The output of Popen.
        exit_code: The exit code of Popen.
    '''
    popen_output = subprocess.Popen(cmd, stdin=input, stdout=output)
    popen_output.wait()
    exit_code = popen_output.returncode
    if debug == "True":
        util.set_verbosity(True)
        util.debug("command: {}".format(cmd))
        util.debug("exit_code: {}".format(exit_code))
    return popen_output, exit_code
