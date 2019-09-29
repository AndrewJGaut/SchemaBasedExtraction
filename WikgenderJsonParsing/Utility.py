
import json

def writeToJsonFile(data, outfile_name, prettify=False):
    with open(outfile_name, 'w') as outfile:
        if(prettify):
            json.dump(data, outfile, indent=4, sort_keys=True)
        else:
            json.dump(data, outfile)

def readFromJsonFile(infile_name):
    with open(infile_name, 'r') as infile:
        return json.load(infile)
    return ""


def getNamesFromFileToDict(filename):
    file = open(filename, 'r')
    namesDict = set()

    for line in file.readlines():
        namesDict.add(line.strip())

    return namesDict