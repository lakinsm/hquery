from xml.dom.minidom import parse
from os import path
import xml.dom.minidom
import csv
import glob
import os
import urllib

def getPharmData(outfile):
    urllib.urlretrieve("ftp://public.nlm.nih.gov/nlmdata/.dailymed/pharmacologic_class_indexing_spl_files.zip", outfile)
    
def extractPharmData(filePath):
    bin_dir = path.dirname(__file__).replace('\\','/')+'/'
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
                    writer.writerow({'Substance Name': name, 'Pharm Class': value, 'Version': version})
                    
def pharmDiff(oldfile, newfile, outfile):
    with open(oldfile, 'rb') as old, open(newfile, 'rb') as new, open(outfile, 'wb') as out:
        a = set(old)
        b = set(new)
        outdata = (a-b, b-a)
        out.write('Substance Name,Pharm Class,Version\r\n')
        out.write('\r\nEntries in Old File but not in New File:,,\r\n')
        for line in outdata[0]:
            out.write(line)
        out.write('\r\nEntries in New File but not in Old File:,,\r\n')
        for line in outdata[1]:
            out.write(line)