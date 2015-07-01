from xml.dom.minidom import parse
from os import path
import xml.dom.minidom
import csv
import glob
import os
import urllib
import re
from itertools import izip_longest

def getPharmData(outfile):
    urllib.urlretrieve("ftp://public.nlm.nih.gov/nlmdata/.dailymed/pharmacologic_class_indexing_spl_files.zip", outfile)
    
def extractPharmData(filePath):
    bin_dir = path.dirname(__file__).replace('\\','/')+'/'
    print(bin_dir)
    os.system(r'c:\cygwin64\bin\bash --login -c '+bin_dir+r'getPharmData.sh')


def writeToCSV(files, outfilePath):
    with open(outfilePath, 'wb') as outfile:
        fieldnames = ['Drug Name', 'Pharm Class', 'Version']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        filelist = glob.glob(files)
        
        for file in filelist:
                data = parse(file)
                version = data.getElementsByTagName("versionNumber")[0].attributes['value'].value
                drugs = data.getElementsByTagName("identifiedSubstance")
                name = drugs[1].getElementsByTagName("name")[0].childNodes[0].data
                ldata = drugs[1].getElementsByTagName("code")
                values = []
                for x in xrange(len(ldata)):
                    if 'displayName' in ldata[x].attributes.keys():
                        values.append(ldata[x].attributes['displayName'].value)
                for value in values:
                    writer.writerow({'Drug Name': name, 'Pharm Class': value, 'Version': version})
                    
def pharmDiff(oldfile, newfile, outfile):
    with open(oldfile, 'rb') as old:
        with open(newfile, 'rb') as new:
            with open(outfile, 'wb') as out:
                for lineOld, lineNew in izip_longest(old, new):
                    breaksOld = [m.start() for m in re.finditer(',', lineOld)]
                    nameOld = lineOld[0:breaksOld[1]]
                    versionOld = lineOld[breaksOld[1]+1]
                    breaksNew = [m.start() for m in re.finditer(',', lineNew)]
                    nameNew = lineNew[0:breaksNew[1]]
                    versionNew = lineNew[breaksNew[1]+1]
                    if (nameOld == nameNew) and (versionOld != versionNew):
                        out.write(lineNew)