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
    
    # Get Excel workbook data location on memory (this does not immediately utilize resources)
    wb = load_workbook(inputReport, read_only = True)
    ws = wb[wb.get_sheet_names()[0]] # The input data must be in the first sheet
    
    with codecs.open(outputPath, 'w', encoding='utf-8') as outfile, open(dirPath+'FailedQueryLog.txt', 'w') as errorfile:
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
        
        # Iterate over the input report, skipping the header line, put values
        # from the report into the output array if known, append variable length
        # fields (e.g. synonym fields)
        count = 0
        for row in ws.rows:
            # Initialize temporary output array to store output values for each row in report
            iterList = ['' for x in range(18)]
            if count == 0:
                count += 1
                continue
            else:
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
                        errorfile.write(row[0].value+' has no valid symbol.\n')
                        continue
                else:
                    symbol = row[6].value #Use first synonym from RED
            else:
                symbol = row[2].value #Use the main symbol from RED
            try:
                data, symbol = validateResponse(queryFetch('http://rest.genenames.org/fetch/symbol/', symbol), errorfile)
            except Exception:
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
                
## Query HGNC database with gene symbol
def queryFetch(prefix, symbol):
    headers = {'Accept': 'application/json'}
    r = requests.get(prefix+symbol, headers=headers)
    return(r)
    
# Check error status and if error, output to errorfile.  If valid
# reponse, retrieve the data as a nested dictionary.            
def validateResponse(responseObj, errorfile):
    if responseObj.status_code != 200:
        errorfile.write(responseObj.url.split('/')[-1]+' symbol returned error code: '+responseObj.status_code+', reason = '+responseObj.reason+'\n')
        print('error main')
    elif responseObj.status_code == 200:
        if responseObj.json()['response']['numFound'] == 0:
            symbol = responseObj.url.split('/')[-1]
            print('1 '+symbol)
            alias = queryFetch('http://rest.genenames.org/fetch/alias_symbol/', symbol)
            if alias.status_code !=200:
                errorfile.write(alias.url.split('/')[-1]+' symbol returned error code: '+alias.status_code+', reason = '+alias.reason+'\n')
                print('error alias')
            elif alias.json()['response']['numFound'] == 0:
                symbol = alias.url.split('/')[-1]
                print('2 '+symbol)
                errorfile.write(responseObj.url.split('/')[-1]+' symbol returned no records\n')
            else:
                symbol = alias.json()['response']['docs'][0]['symbol']
                print('3 '+symbol)
                data = queryFetch('http://rest.genenames.org/fetch/symbol/', symbol)
                return(data, symbol)
        else:
            symbol = responseObj.json()['response']['docs'][0]['symbol']
            print('4 '+symbol)
            return(responseObj, symbol)

## Track query progress via a wx progress dialog
def progressDialog(List, Dir):

    # Set variables for wx.ProgressDialog
    frame.count = 0
    frame.progressMax = len(List)
    frame.keepGoing = True
    frame.skip = False
    
    # Initialize wx.ProgressDialog
    frame.dialog = wx.ProgressDialog("Query Status", "Query completion:", frame.progressMax, style=wx.PD_APP_MODAL | wx.PD_CAN_ABORT | wx.PD_ELAPSED_TIME)
    
    # Loop over the gene list, check for errors in gene symbol, and query
    # each gene against the HUGO database.  Return json object and parse it
    # with dumpclean().  Update the progress bar.
    with open(Dir+"\GeneQueryResults.txt", 'w') as f:
        with open(Dir+"\RejectedQueryReport.txt", 'w') as g:
            for gene in List:
                r = requests.get(prefix+gene, headers=headers)
                if r.status_code == 200:
                    dumpClean(obj=r.json()['response']['docs'][0], outfile=f)
                    f.write("\n\n")
                else:
                    g.write("Error code: "+str(r.status_code)+" for gene: "+gene+"\n")
                frame.count += 1
                (frame.keepGoing, frame.skip) = frame.dialog.Update(frame.count, str(frame.count)+" of "+str(frame.progressMax))
    frame.dialog.Destroy()

