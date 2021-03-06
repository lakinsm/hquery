#-------------------------------------------------------------------------------
#
# Name:     bin/drugpharmassoc.py
# Module:   drugPharmAssoc
# Purpose:  This is a native module for the hquery wxPython GUI. This module
#           provides functionality for interfacing with the NLM
#           pharmocologic spl index files on the NLM ftp server.  It also
#           allows for fast differential comparison of old data to new data.
#
# Author:   Steven Lakin (Steven.Lakin@colostate.edu or lakinsm@miamioh.edu)
#
# Created:  June 29th, 2015
# Copyright: National Institutes of Health BTRIS
#
# Documentation: https://github.com/lakinsm/hquery
#
#-------------------------------------------------------------------------------

# Note: this module requires Python 3

from xml.dom.minidom import parse
from os import path
import xml.dom.minidom
import csv
import glob
import os
import urllib
import sys
import tempfile

## This method pulls the pharmocologic index files from the NLM ftp.  Change
## this method if the URL for the file download changes.  To do this, simply
## replace the URL below with the new URL.  It must be exact.
def getPharmData(outfile):
    urllib.urlretrieve("ftp://public.nlm.nih.gov/nlmdata/.dailymed/pharmacologic_class_indexing_spl_files.zip", outfile)

## This method extracts the downloaded data from the getPharmData method.
## Files are extracted to the same location with the same file name (minus
## the zip extension).
def extractPharmData(filePath):
    unixpath = filePath.replace('\\','/')
    nozip = unixpath.split('.')[0]
    print('Beginning file extraction...\n\n')
    with tempfile.NamedTemporaryFile() as temp:
        temp.write(r"#!/usr/bin/bash"+"\n"+"unzip "+unixpath+" -d "+nozip+";\n"+"unzip "+nozip+r"/\* -d "+nozip+";\n"+"rm "+nozip+r"/*.zip")
        temp.flush()
        bin_dir = temp.name.replace('\\','/')
        if os.path.isdir(r"c:\cygwin64") == True:
            os.system(r'c:\cygwin64\bin\bash --login -c '+bin_dir)
        elif os.path.isdir(r"C:\cygwin") == True:
            os.system(r'c:\cygwin\bin\bash --login -c '+bin_dir)
    print('File extraction complete\n\n')

## This method generates a comma-delimited (csv) file that contains the
## substance name, substance class, and the version number from the NLM
## pharmocologic index files.  It will only work on the xml formatted files from
## the NLM ftp downloaded in the getPharmData output.  Input to this method is
## the directory path of the xml files and the desired output path for the csv.
def writeToCSV(files, outfilePath):
    if '.' in outfilePath:
        outfilePath = ''.join(outfilePath.split('.')[0:-1])
    print('Beginning data extraction..\n\n.')
    with open(outfilePath+'.csv', 'wb') as outfile:
        fieldnames = ['Substance Name', 'Pharm Class', 'Version']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        filelist = glob.glob(files)
        
        for file in filelist:
                data = parse(file)
                version = data.getElementsByTagName("versionNumber")[0].attributes['value'].value
                drugs = data.getElementsByTagName("identifiedSubstance")
                try:
                    name = drugs[1].getElementsByTagName("name")[0].childNodes[0].data
                    ldata = drugs[1].getElementsByTagName("code")
                    values = []
                    for x in xrange(len(ldata)):
                        if 'displayName' in ldata[x].attributes.keys():
                            values.append(ldata[x].attributes['displayName'].value)
                    for value in values:
                        writer.writerow({'Substance Name': name, 'Pharm Class': value, 'Version': version})
                except Exception as e:
                    if 'list index' in str(e):
                        print(file.split('/')[-1].split('\\')[-1]+' contained no drug data')
                    else:
                        print(e)
                    continue
    print('\nData extraction complete')
                    
## This method accepts two comma delimited files as input and compares them.
## It will only work for the file format output by the writeToCSV function.
def pharmDiff(oldfile, newfile, outfile):
    print('Beginning file diff...\n')
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
    print('Diff complete\n')
