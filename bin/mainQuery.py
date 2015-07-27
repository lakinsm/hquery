#-------------------------------------------------------------------------------
#
# Name:     bin/mainQuery.py
# Purpose:  This module is the work horse of the hquery program. It receives
#           parsed data from xlsxparse, places that data into the correct fields
#           in the output file, and queries the remaining data from the
#           HGNC database.  Output is written to a tab-delimited text file.
#
# Author:   Steven Lakin (Steven.Lakin@colostate.edu or lakinsm@miamioh.edu)
#
# Created:  July 13th, 2015
# Copyright: National Institutes of Health BTRIS
#
# Documentation: https://github.com/lakinsm/hquery
#
#-------------------------------------------------------------------------------

import codecs
import os
import time,datetime

try:
    import requests
    from openpyxl import *
except ImportError:
    print('Please install the requests package: pip install requests')
    print('Please install the openpyxl package: pip install openpyxl')
    raise

## Main method for parsing the RED input report and querying the HGNC database.
## It must be formatted exactly as detailed in the documentation. This method
## will call all subsequent methods that are necessary for the query process.  
def mainQuery(inputReport, outputPath):
    dirPath = '\\'.join(outputPath.split('\\')[0:-1])+"\\"
    timestamp = getTime()
    
    # Remove any file extension that the user may have selected
    if '.' in outputPath:
        outputPath = ''.join(outputPath.split('.')[0:-1])+timestamp+'.tab'
    else:
        outputPath = outputPath+timestamp+'.tab'
    
    # Get Excel workbook data location on memory (this does not immediately utilize resources)
    wb = load_workbook(inputReport, read_only = True)
    ws = wb[wb.get_sheet_names()[0]] # The input data must be in the first sheet
    
    progressMax = len([1 for row in ws.rows])-1
    
    with codecs.open(outputPath, 'w', encoding='utf-8') as outfile, open(dirPath+'FailedQueryLog'+timestamp+'.tab', 'w') as errorfile:
        # Initialize static headers for outfile
        outfile.write(
        'Concept_Name\tConcept_ID\tGene_Nomenclature_Symbol\tGene_Chromosome_Location#1\tGene_Chromosome_Location#2\t'
        'Gene_Mapping_Location\tGene_Approved_Symbol_HGNC\tGene_Approved_Name_HGNC\tChromosome_Location_HGNC\tGene_Symbol_Synonyms_HGNC\t'
        'Gene_Prev_Symbol_Synonyms_HGNC\tGene_Name_Synonyms_HGNC\tGene_Family_IDs_HGNC\tGene_Family_Names_HGNC\t'
        'Gene_Locus_Group_HGNC\tGene_Locus_Type_HGNC\tEnzyme_ID_HGNC\tPubmed_IDs_HGNC\t'
        )
        
        # Fill in the remaining dynamic headers
        for x in range([len(row) for row in ws.rows][0]-6):
            outfile.write('Full_Synonym#'+str(x+1)+'\t')
        outfile.write('\n')
        
        # Initialize headers for errorfile:
        errorfile.write('Concept_Name\tError_Field\tError_Text\n')
        
        # Iterate over the input report, validate headers, put values
        # from the report into the output array if known, append dynamic
        # fields (e.g. synonym fields)
        count = 0
        for row in ws.rows:
            
            # Initialize temporary output list to store output values for each row in report
            # This ensures there is white space for empty fields
            iterList = ['' for x in range(18)]
            
            # Validate headers from the input file
            if count == 0:
                try:
                    validateHeader(row)
                    count += 1
                    continue
                except ValueError:
                    raise
            else:
                print('\nGene '+str(count)+' of '+str(progressMax)+'...')
                iterList[0] = row[0].value #Concept name
                iterList[1] = row[1].value #Concept ID
                iterList[2] = row[2].value #Gene nomenclature symbol
                iterList[3] = row[3].value #Gene chromosome location 1
                iterList[4] = row[4].value #Gene chromosome location 2
                iterList[5] = row[5].value #Gene mapping location
                for cell in row[6:len(row)]: #All synonym fields appended
                    iterList.append(cell.value)
                    
            
            # Initialize the symbol to be queried, if it is not found in the
            # main symbol field, use the first or second synonym.  
            # Fetch the data from HGNC.
            nulls = ['NULL', 'Not%20Provided', 'Not Provided', '-']
            if row[2].value in nulls:
                if len(row[6].value) > 12 or row[6].value in nulls:
                    if len(row[7].value) < 12 and row[7].value not in nulls:
                        symbol = row[7].value #Use second synonym from RED
                    else:
                        errorfile.write(row[0].value+'\t'+row[2].value+'\t'+' has no valid symbol.\n')
                        continue
                else:
                    symbol = row[6].value #Use first synonym from RED
            else:
                symbol = row[2].value #Use the main symbol from RED
                
            # Query the database and validate the response
            # Query errors are output to errorfile
            try:
                data, symbol = validateResponse(row[0].value, queryFetch('http://rest.genenames.org/fetch/symbol/', symbol), errorfile)
                count +=1
            except Exception: #The specific errors are handled by validateResponse
                count +=1
                continue
                    
            # Place retrieved data into iterList
            content = data.json()['response']['docs'][0]
            if 'symbol' in content.keys():
                iterList[6] = content['symbol']
            if 'name' in content.keys():
                iterList[7] = content['name']
            if 'location' in content.keys():
                iterList[8] = content['location']
            if 'alias_symbol' in content.keys():
                iterList[9] = '|'.join(x.encode('utf-8') for x in content['alias_symbol'])
            if 'prev_symbol' in content.keys():
                iterList[10] = '|'.join(x.encode('utf-8') for x in content['prev_symbol'])
            if 'alias_name' in content.keys():
                iterList[11] = '|'.join(x.encode('utf-8') for x in content['alias_name'])
            if 'gene_family_id' in content.keys():
                iterList[12] = '|'.join(str(x) for x in content['gene_family_id'])
            if 'gene_family' in content.keys():
                iterList[13] = '|'.join(x.encode('utf-8') for x in content['gene_family'])
            if 'locus_group' in content.keys():
                iterList[14] = content['locus_group']
            if 'locus_type' in content.keys():
                iterList[15] = content['locus_type']
            if 'enzyme_id' in content.keys():
                iterList[16] = '|'.join(x.encode('utf-8') for x in content['enzyme_id'])
            if 'pubmed_id' in content.keys():
                iterList[17] = '|'.join(str(x) for x in content['pubmed_id'])
            for index in range(len(iterList)):
                if iterList[index] == None:
                    iterList[index] = ''
            outfile.write(u'\t'.join([x.decode('utf-8') for x in iterList])+u'\n')
            del iterList
    return(outputPath, timestamp)

## Query HGNC database with gene symbol
def queryFetch(prefix, symbol):
    headers = {'Accept': 'application/json'}
    r = requests.get(prefix+symbol, headers=headers)
    return(r)
    
## Check error status and if error, output to errorfile.  If valid
## reponse, retrieve the data as a nested dictionary.            
def validateResponse(conceptName, responseObj, errorfile):
    if responseObj.status_code != 200:
        errorfile.write(conceptName+'\t'+responseObj.url.split('/')[-1]+'\t'+' symbol returned error code: '+responseObj.status_code+', reason = '+responseObj.reason+'\n')
        print('error main')
    elif responseObj.status_code == 200:
        if responseObj.json()['response']['numFound'] == 0:
            symbol = responseObj.url.split('/')[-1]
            print('Invalid Symbol '+symbol+', searching for alias...')
            alias = queryFetch('http://rest.genenames.org/fetch/alias_symbol/', symbol)
            if alias.status_code !=200:
                errorfile.write(conceptName+'\t'+alias.url.split('/')[-1]+'\t'+' symbol returned error code: '+alias.status_code+', reason = '+alias.reason+'\n')
                print('error alias')
            elif alias.json()['response']['numFound'] == 0:
                symbol = alias.url.split('/')[-1]
                print('Alias Symbol: '+symbol+' not found')
                errorfile.write(conceptName+'\t'+responseObj.url.split('/')[-1]+'\t'+' symbol returned no records\n')
            else:
                symbol = alias.json()['response']['docs'][0]['symbol']
                print('Alias Symbol: '+symbol+' found')
                data = queryFetch('http://rest.genenames.org/fetch/symbol/', symbol)
                return(data, symbol)
        else:
            symbol = responseObj.json()['response']['docs'][0]['symbol']
            print('Valid Symbol: '+symbol)
            return(responseObj, symbol)

## Verify that headers in the input excel report are appropriate for mainQuery
def validateHeader(row):
    if "Concept" and "Name" not in row[0].value:
        print('An error has occurred:\n\n')
        raise ValueError(row[0].value+' is an incorrect header.  "Concept" and "Name" must be present in this header')
    if "Concept" and "Code" not in row[1].value:
        print('An error has occurred:\n\n')
        raise ValueError(row[1].value+' is an incorrect header.  "Concept" and "Code" must be present in this header')
    if "Gene" and "Nomenclature" and "Symbol" not in row[2].value:
        print('An error has occurred:\n\n')
        raise ValueError(row[2].value+' is an incorrect header.  "Gene", "Nomenclature", and "Symbol" must be present in this header')
    if "Gene" and "Chromosome" and "Location" not in row[3].value:
        print('An error has occurred:\n\n')
        raise ValueError(row[3].value+' is an incorrect header.  "Gene", "Chromosome", and "Location" must be present in this header')
    if "Gene" and "Chromosome" and "Location" not in row[4].value:
        print('An error has occurred:\n\n')
        raise ValueError(row[4].value+' is an incorrect header.  "Gene", "Chromosome", and "Location" must be present in this header')
    if "Gene" and "Map" and "Location" not in row[5].value:
        print('An error has occurred:\n\n')
        raise ValueError(row[5].value+' is an incorrect header.  "Gene", "Map", and "Location" must be present in this header')
    for cell in row[6:len(row)]:
        if "Synonym" not in cell.value:
            print('An error has occurred:\n\n')
            raise ValueError(cell+' is an incorrect header.  "Synonym" must be present in this header')

def validatePivot(infile):
    # Get Excel workbook data location on memory (this does not immediately utilize resources)
    wb = load_workbook(infile, read_only = True)
    ws = wb[wb.get_sheet_names()[0]] # The input data must be in the first sheet
    headers = [x.value for x in [cell for cell in [row for row in ws.rows]][0]]
    if "Concept" and "Name" not in headers[0]:
        print('An error has occurred:\n\n')
        raise ValueError(headers[0]+' is an incorrect header.  "Concept" and "Name" must be present in this header')
    if "Concept" and "Code" not in headers[1]:
        print('An error has occurred:\n\n')
        raise ValueError(headers[1]+' is an incorrect header.  "Concept" and "Code" must be present in this header')
    if "Gene" and "Nomenclature" and "Symbol" not in headers[2]:
        print('An error has occurred:\n\n')
        raise ValueError(headers[2]+' is an incorrect header.  "Gene", "Nomenclature", and "Symbol" must be present in this header')
    if "Gene" and "Chromosome" and "Location" not in headers[3]:
        print('An error has occurred:\n\n')
        raise ValueError(headers[3]+' is an incorrect header.  "Gene", "Chromosome", and "Location" must be present in this header')
    if "Gene" and "Map" and "Location" not in headers[4]:
        print('An error has occurred:\n\n')
        raise ValueError(headers[5]+' is an incorrect header.  "Gene", "Map", and "Location" must be present in this header')
    if "Synonym" not in headers[5]:
        print('An error has occurred:\n\n')
        raise ValueError(headers[5]+' is an incorrect header.  "Synonym" must be present in this header')

## Expand the output of mainQuery
## Any cell whose values contain pipes " | " will be split and expanded into separate columns
def expandReport(infile, timestamp):
    path = '/'.join(infile.split('\\')[0:-1])
    inpath = infile.replace('\\', '/')
    os.system(r'Rscript scripts/expandReport.R '+inpath+' '+path+'/ExpandedQueryReport'+timestamp+'.tab')

## long to wide conversion of the raw RED report
def pivotReport(infile):
    path = '/'.join(infile.split('\\')[0:-1])
    inpath = infile.replace('\\', '/')
    timestamp = getTime()
    os.system(r'Rscript scripts/pivotReport.R '+inpath+' '+path+'/pivotedReport'+timestamp+'.xlsx')

## Get the timestamp from the machine
def getTime():
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('_%Y_%m_%d__%H_%M_%S')
    return(st)