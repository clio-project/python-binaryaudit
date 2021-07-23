# Group packages based on source RPM

import json
import subprocess

def groupPackages(dirPath):        
    ''' Groups packages based on source RPM and outputs to JSON file.
    
    Parameters:
        dirPath (str): The path to the input directory.  
    '''
    file = open("RPMList.txt", "r")
    dict = {}
    for line in file:
        line = line.replace("\n", "")
        proc = subprocess.Popen(["rpm", "-qpi", dirPath + line], stdout=subprocess.PIPE)
        grep = subprocess.Popen(["grep", "Source RPM"],
                                    stdin=proc.stdout,
                                    stdout=subprocess.PIPE)
        source = grep.stdout.read()
        source = source.replace("Source RPM  : ", "")
        source = source.replace("\n", "")
        dict.setdefault(source, []).append(line)
    file.close()

    with open("groupedPackages.json", "w") as outputFile:
        json.dump(dict, outputFile, indent=2)
