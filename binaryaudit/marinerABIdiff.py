import RPM
import run

import sys

def getRPMList(dirPath):
    ret = run.runCommand(dirPath, "ls")
    print "Return code: ", ret.returncode

def groupRPMs(dirPath):
    RPM.groupPackages(dirPath)

def main():
    dirPath = sys.argv[1]
    getRPMList(dirPath)
    groupRPMs(dirPath)

if __name__ == "__main__":
    main()
