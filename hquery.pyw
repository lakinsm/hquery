#-------------------------------------------------------------------------------
#
# Name:     hquery.pyw
# Purpose:  Query a list of genes against the HGNC database, return tab file
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
from bin import mainQuery
from bin import xlsxparse

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
        menuOpen = querymenu.Append(wx.ID_ANY, "&Load Query List", " Load a gene batch file for query")
        menuPivot = querymenu.Append(wx.ID_ANY, "&Load Report for Pivot", " Load an unpivoted report for file pivot")
        #menuGit2 = querymenu.Append(wx.ID_ANY, "&Help", " See documentation for help with gene query")
        
        # The following selections belong to the Help menu:
        menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About", " Information about hquery")
        menuGit = helpmenu.Append(wx.ID_ANY, "&Help", " See documentation for help with hquery features")
        
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
        self.Bind(wx.EVT_MENU, self.OnPivot, menuPivot)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnGit, menuGit)
        #self.Bind(wx.EVT_MENU, self.OnGit, menuGit2)
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
            #### Put mainQuery interface here ####
        
    ## Method for link to GitHub repo
    def OnGit(self, e):
        webbrowser.open("https://github.com/lakinsm/hquery")
    
    ## Method for program information
    def OnAbout(self, e):
        dlg = wx.MessageDialog(self, "Version: 0.1.1\n\nAuthor: Steven Lakin\nContact: Steven.Lakin@colostate.edu\n\nThis program is an interface to the HGNC gene database and NLM pharmocologic index.\n\nSee https://github.com/lakinsm/hquery for details and current information.", "About hquery", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
    
    def OnPivot(self, e):
        dlg = wx.FileDialog(self, "Choose a file", self.pivotdirname, "", "*.*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.pivotfilename = dlg.GetFilename()
            self.pivotdirname = dlg.GetDirectory()
            #### Put xlsxparse interface for pivot here ####
        
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
frame = MainWindow(None, 'BTRIS Extension for HGNC and NLM Data v0.1.1')
app.MainLoop()
