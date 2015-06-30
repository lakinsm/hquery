from xml.dom.minidom import parse
import xml.dom.minidom
import csv
import glob

def writeToCSV(files, outfilePath):
    with open(outfilePath, 'wb') as outfile:
        fieldnames = ['Drug Name', 'Pharm Class']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        filelist = glob.glob(files)
        
        for file in filelist:
                data = parse(file)
                drugs = data.getElementsByTagName("identifiedSubstance")
                name = drugs[1].getElementsByTagName("name")[0].childNodes[0].data
                ldata = drugs[1].getElementsByTagName("code")
                values = []
                for x in xrange(len(ldata)):
                    if 'displayName' in ldata[x].attributes.keys():
                        values.append(ldata[x].attributes['displayName'].value)
                for value in values:
                    writer.writerow({'Drug Name': name, 'Pharm Class': value})