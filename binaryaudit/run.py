# Read RPMs in input directory

import subprocess

def runCommand(dirPath, cmd):
    ''' Runs commands and gets output.

    Parameters:
        dirPath (str): The path to the input directory.
        cmd (str): The command to be run.

    Returns:
        ret: The return code of subprocess.Popen().   
    '''
    if cmd == "ls":
        outputFile = open("RPMList.txt", "wb")
        ret = subprocess.Popen(["ls", dirPath], stdout=outputFile)
        ret.wait()
        outputFile.close()
        return ret
