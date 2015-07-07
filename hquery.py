#-------------------------------------------------------------------------------
#
# Name:     hquery.pyw
# Purpose:  Query a list of genes against the HUGO database, return tab file
#           Other features include an interface to the NLM Pharmocologic index
#           See documentation for details
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
# This is a wxPython GUI

import os
import os.path
import wx
import webbrowser
from bin import drugPharmAssoc

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
    
    # Initialize temporary output array to store output values for each row in report
    iterList = [None for x in range(18)]
    
    with open(outputPath, 'wb') as outfile, open(dirPath+'FailedQueryLog.txt', 'w') as errorfile:
        
        # Iterate over the input report, skipping the header line, put values
        # from the report into the output array if known, append variable length
        # fields (e.g. synonym fields)
        count = 0
        for row in ws.rows:
            if count == 0:
                count += 1
                continue
            else:
                iterList[0] = row[0].value
                iterList[1] = row[1].value
                iterList[2] = row[2].value
                iterList[3] = row[3].value
                iterList[4] = row[4].value
                iterList[5] = row[5].value
                for cell in row[5:len(row)]:
                    iterList.append(cell.value)
            
            # Initialize the symbol to be queried, if it is not found in the
            # main symbol field, use the first synonym.  Fetch the data from HGNC.
            if row[2].value != "Not Provided" or row[2].value != "NULL":
                symbol = row[2].value
            elif row[6].value != "Not Provided" or row[6].value != "NULL":
                symbol = row[6].value
            elif len(row[7].value) < 12:
                symbol = row[7].value 
            data = queryFetch(symbol)
            
            # Check error status and if error, output to errorfile.  If valid
            # reponse, retrieve the data as a nested dictionary.
            if data.status_code != 200:
                errorfile.write(data.url.split('/')[-1]+' symbol returned error code: '+data.status_code+', reason = '+data.reason+'\n')
            elif data.status_code == 200:
                content = data.json()['response']['docs'][0]
                ## myst
            
            
                
## Query HGNC database with gene symbol
def queryFetch(symbol):
    prefix = 'http://rest.genenames.org/fetch/symbol/'
    headers = {'Accept': 'application/json'}
    r = requests.get(prefix+symbol, headers=headers)
    return(r)

## Dictionary parser for requests.json() object, returns data in a list 
## of strings
def dumpClean(obj, outfile):
    if type(obj) == dict:
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                outfile.write(str(k)+"\n")
                dumpClean(v, outfile)
            else:
                outfile.write('%s : %s' % (k, v)+"\n")
    elif type(obj) == list:
        for v in obj:
            if hasattr(v, '__iter__'):
                dumpClean(v, outfile)
            else:
                outfile.write("\t"+str(v)+"\n")
    else:
        outfile.write(+str(obj)+"\n")

## Ensure gene symbol or term is in a valid format
def validateGene(geneKey):
    temp = ''

## Use the requests package to query the HUGO gene database for each gene
## symbol.  This method has built-in gene symbol validation and calls back
## to the GUI to update the progress bar.  Outfiles are written to the same
## directory as the input files.
def hugoQuery(List, Dir):
    
    # HUGO API URL, return json object
    prefix = 'http://rest.genenames.org/fetch/symbol/'
    headers = {'Accept': 'application/json'}
    
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


### main GUI app class
class MainWindow(wx.Frame):

    ## Initialize the main frame
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(-1,-1))
        
        # Add status bar and menus
        self.CreateStatusBar()
        querymenu = wx.Menu()
        pharmmenu = wx.Menu()
        helpmenu = wx.Menu()
        
        
        # File menu options
        # The following selections belong to the Gene Query menu:
        menuOpen = querymenu.Append(wx.ID_OPEN, "&Load Query List", " Load a gene batch file for query")
        menuGit = querymenu.Append(wx.ID_ANY, "&Help", " See documentation for help with gene query")
        
        # The following selections belong to the Help menu:
        menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About", " Information about hquery")
        menuGit2 = helpmenu.Append(wx.ID_ANY, "&Help", " See documentation for help with hquery features")
        
        # The following selections belong to the Pharm Data menu:
        menuGetPharm = pharmmenu.Append(wx.ID_ANY, "&Get Pharm Data", " Pull Pharmocologic index data into the specified directory")
        menuPharmDiff = pharmmenu.Append(wx.ID_ANY, "&Pharm Diff", " Differentials between old and new index data")
        
        # Place selections into their categories and initialize the menu bar
        menuBar = wx.MenuBar()
        menuBar.Append(querymenu, "&Gene Query")
        menuBar.Append(pharmmenu, "&Pharm Data")
        menuBar.Append(helpmenu, "&Help")
        self.SetMenuBar(menuBar)
        
        # File menu events: the second parameter is the function call, the third
        # parameter is to which menu selection it belongs
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnGit, menuGit)
        self.Bind(wx.EVT_MENU, self.OnGit, menuGit2)
        self.Bind(wx.EVT_MENU, self.OnGetPharm, menuGetPharm)
        self.Bind(wx.EVT_MENU, self.OnPharmDiff, menuPharmDiff)
        self.Show(True)
        
    ## Method for loading gene query files
    def OnOpen(self, e):
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            with open(os.path.normpath(os.path.join(self.dirname+os.sep,self.filename)),'r') as f:
                geneList = f.read().decode("utf-8-sig").encode("utf-8").strip().split('\n')
                num_lines = len(geneList)
                if num_lines <= 5:
                    head_lines = geneList[0:num_lines]
                    responseText = self.filename+" loaded as gene file\nNumber of genes is "+str(num_lines)+"\n\n"+"First few genes in file:\n"+"\n".join(head_lines)+"\n\nProceed with Gene Query?"+"\n\n Files will be saved to this directory:"+self.dirname
                else:
                    head_lines = geneList[0:5]
                    responseText = self.filename+" loaded as gene file\nTotal genes: "+str(num_lines)+"\n\n"+"First few genes in file:\n"+"\n".join(head_lines)+"\n\nProceed with Gene Query?"+"\n\n Files will be saved to this directory:"+self.dirname
                dlg2 = wx.MessageDialog(self, responseText, "File Information", wx.YES_NO)
                if dlg2.ShowModal() == wx.ID_YES:
                    hugoQuery(geneList, self.dirname)
                dlg2.Destroy()
        dlg.Destroy()
        
    ## Method for link to GitHub repo
    def OnGit(self, e):
        webbrowser.open("https://github.com/lakinsm/hquery")
    
    ## Method for program information
    def OnAbout(self, e):
        dlg = wx.MessageDialog(self, "Author: Steven Lakin\nContact: Steven.Lakin@colostate.edu\n\nThis program was developed to batch query gene keys against the HUGO database.\n\nSee https://github.com/lakinsm/hquery for details and current information.", "About hquery", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
        
    ## Method for downloading new pharmocologic index spl data from the NLM
    ## ftp server.  Includes an optional call to Cygwin to extract the data.
    def OnGetPharm(self, e):
        self.downdir = ''
        dlg = wx.DirDialog(self, "Choose a directory", "", wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.downdir = dlg.GetPath()
        dlg.Destroy()
        
        if os.path.isfile(self.downdir+"\\pharmacologic_class_indexing_spl_files.zip") == True:
            if os.path.isdir(self.downdir+"\\pharmacologic_class_indexing_spl_files") == True:
                return()
            else:
                dlg4 = wx.MessageDialog(self, "Download Complete\n\nWould you like to extract the files using cygwin? (Windows only)", "Download Status", wx.YES_NO)
                if dlg4.ShowModal() == wx.ID_YES:
                    drugPharmAssoc.extractPharmData(self.downdir+"\\pharmacologic_class_indexing_spl_files.zip")
                    return()
        dlg2 = wx.MessageDialog(self, "Click OK to download data to "+self.downdir+"\\pharmacologic_class_indexing_spl_files.zip"+"\n\nIt may take a few minutes for the file to appear", "Download In Progress", wx.OK | wx.CANCEL)
        if dlg2.ShowModal() == wx.ID_OK:
            drugPharmAssoc.getPharmData(self.downdir+"\\pharmacologic_class_indexing_spl_files.zip")
        dlg2.Destroy()
        
        dlg3 = wx.MessageDialog(self, "Download Complete\n\nWould you like to extract the files using cygwin? (Windows only)", "Download Status", wx.YES_NO)
        if os.path.isfile(self.downdir+"\\pharmacologic_class_indexing_spl_files.zip") == True:
            if dlg3.ShowModal() == wx.ID_YES:
                drugPharmAssoc.extractPharmData(self.downdir+"\\pharmacologic_class_indexing_spl_files.zip")
        dlg3.Destroy()
        dlg4.Destroy()

    ## Method for selecting two files and comparing them for differential
    ## entries.  The method used is the equivalent of symmetric difference
    ## in set theory.  See the python documentation on sets for more information.
    def OnPharmDiff(self, e):
        self.dirname = ''
        self.filelist = []
        dlg = wx.FileDialog(self, "Choose a file", "", "", "*.*", wx.FD_MULTIPLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.filelist = dlg.GetPaths()
            self.dirname = dlg.GetDirectory()
            if os.path.isfile(self.filelist[0]) and os.path.isfile(self.filelist[1]):
                dlg2 = wx.MessageDialog(self, "Proceed with file differentiation?\n\nFiles will be written to:\n"+str(self.dirname)+r"\pharmDiffResults.csv", "Pharm Differential Analysis", wx.YES_NO)
                if dlg2.ShowModal() == wx.ID_YES:
                    drugPharmAssoc.pharmDiff(self.filelist[0], self.filelist[1], str(self.dirname)+r"\pharmDiffResults.csv")
        dlg.Destroy()
        
### Main ###
#app = wx.App(True, filename=r'C:\Users\lakinsm\Documents\PosterNIH\Term\HUGOQueryModule\errorlog.txt')
app = wx.App(False)
frame = MainWindow(None, 'Batch Query for HUGO Database')
app.MainLoop()
