from xml.dom.minidom import parse
from os import path
import xml.dom.minidom
import csv
import glob
import os
import urllib
import sys
import tempfile

def getPharmData(outfile):
    urllib.urlretrieve("ftp://public.nlm.nih.gov/nlmdata/.dailymed/pharmacologic_class_indexing_spl_files.zip", outfile)
    
def extractPharmData(filePath):
    unixpath = filePath.replace('\\','/')
    nozip = unixpath.split('.')[0]
    with tempfile.NamedTemporaryFile() as temp:
        temp.write(r"#!/usr/bin/bash"+"\n"+"unzip "+unixpath+" -d "+nozip+";\n"+"unzip "+nozip+r"/\* -d "+nozip+";\n"+"rm "+nozip+r"/*.zip")
        temp.flush()
        bin_dir = temp.name.replace('\\','/')
        if os.path.isdir(r"c:\cygwin64") == True:
            os.system(r'c:\cygwin64\bin\bash --login -c '+bin_dir)
        elif os.path.isdir(r"C:\cygwin") == True:
            os.system(r'c:\cygwin\bin\bash --login -c '+bin_dir)

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
        newfilename = ''
        oldfilename = ''
        if sys.platform.startswith('win32'):
            newfilename = newfile.split('\\')[-1]
            oldfilename = oldfile.split('\\')[-1]
        elif sys.platform.startswith('linux'):
            newfilename = newfile.split('/')[-1]
            oldfilename = oldfile.split('/')[-1]
        elif sys.platform.startswith('darwin'):
            newfilename = newfile.split('/')[-1]
            oldfilename = oldfile.split('/')[-1]
        a = set(old)
        b = set(new)
        outdata = (a-b, b-a)
        out.write('Substance Name,Pharm Class,Version\r\n')
        out.write('\r\nEntries in '+str(oldfilename)+' but not in '+str(newfilename)+':,,\r\n')
        for line in outdata[0]:
            out.write(line)
        out.write('\r\nEntries in '+str(newfilename)+' but not in '+str(oldfilename)+':,,\r\n')
        for line in outdata[1]:
            out.write(line)