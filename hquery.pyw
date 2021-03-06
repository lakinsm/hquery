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
import sys
from bin import drugPharmAssoc
from bin import mainQuery

class RedirectText(object):
    def __init__(self,aWxTextCtrl):
        self.out=aWxTextCtrl
    
    def write(self,string):
        self.out.WriteText(string)

### main GUI app class
class MainWindow(wx.Frame):

    ## Initialize the main frame
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800,400))
        
        panel = wx.Panel(self, wx.ID_ANY)
        log = wx.TextCtrl(panel, wx.ID_ANY, size=(800,400), style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(log, 1, wx.ALL|wx.EXPAND, 5)
        panel.SetSizer(sizer)
        
        redir = RedirectText(log)
        sys.stdout = redir
        sys.stderr = redir
        
        # Add status bar and menus
        self.CreateStatusBar()
        querymenu = wx.Menu()
        pharmmenu = wx.Menu()
        helpmenu = wx.Menu()
        
        
        # File menu options
        # The following selections belong to the Gene Query menu:
        menuOpen = querymenu.Append(wx.ID_ANY, "&Load Query List", " Load a gene batch file for query")
        menuPivot = querymenu.Append(wx.ID_ANY, "&Load Report for Pivot", " Load an unpivoted report for file pivot")
        
        # The following selections belong to the Help menu:
        menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About", " Information about hquery")
        menuGit = helpmenu.Append(wx.ID_ANY, "&Help", " See documentation for help with hquery features")
        
        # The following selections belong to the Pharm Data menu:
        menuGetPharm = pharmmenu.Append(wx.ID_ANY, "&Get Pharm Data", " Pull Pharmocologic index data into the specified directory")
        menuExtractClass = pharmmenu.Append(wx.ID_ANY, "&Extract Substance Classes", " Extract Substance Class data from XML files into .csv")
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
        self.Bind(wx.EVT_MENU, self.OnGetPharm, menuGetPharm)
        self.Bind(wx.EVT_MENU, self.OnExtractClass, menuExtractClass)
        self.Bind(wx.EVT_MENU, self.OnPharmDiff, menuPharmDiff)
        self.Show(True)
        
    ## Method for loading gene query files
    def OnOpen(self, e):
        self.queryinfile = ''
        self.queryoutfile = ''
        dlg = wx.FileDialog(self, "Choose a file", self.queryinfile, "", "*.*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.queryinfile = dlg.GetPath()
            dlg2 = wx.FileDialog(self, "Save as", "", "", "*.*", wx.FD_SAVE)
            if dlg2.ShowModal() == wx.ID_OK:
                self.queryoutfile = dlg2.GetPath()
                print('Beginning query to HGNC database...\n\n')
                try:
                    tabFile, timestamp = mainQuery.mainQuery(self.queryinfile, self.queryoutfile)
                    print('\nQuery complete.  Expanding report...\n\n')
                    mainQuery.expandReport(tabFile, timestamp)
                    print('Report expanded and files written\n\n')
                except ValueError:
                    raise
            dlg2.Destroy()
        dlg.Destroy()
        
    ## Method for link to GitHub repo
    def OnGit(self, e):
        webbrowser.open("https://github.com/lakinsm/hquery")
    
    ## Method for program information
    def OnAbout(self, e):
        dlg = wx.MessageDialog(self, "Version: 0.1.1\n\nAuthor: Steven Lakin\nContact: Steven.Lakin@colostate.edu\n\nThis program is an interface to the HGNC gene database and NLM pharmocologic index.\n\nSee https://github.com/lakinsm/hquery for details and current information.", "About hquery", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
    
    def OnPivot(self, e):
        dlg = wx.FileDialog(self, "Choose a file", "", "", "*.xlsx", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.pivotpath = dlg.GetPath()
            print('Beginning file pivot...\n\n')
            try:
                mainQuery.validatePivot(self.pivotpath)
                mainQuery.pivotReport(self.pivotpath)
                print('File pivot complete\n\n')
            except Exception:
                raise
            
        
    ## Method for downloading new pharmocologic index spl data from the NLM
    ## ftp server.  Includes an optional call to Cygwin to extract the data.
    def OnGetPharm(self, e):
        self.downdir = '\\pharmacologic_class_indexing_spl_files'+mainQuery.getTime()
        dlg = wx.DirDialog(self, "Choose a directory", "", wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.downdir = dlg.GetPath()+self.downdir
            if os.path.isfile(self.downdir+".zip") == True:
                if os.path.isdir(self.downdir) == True:
                    return()
                else:
                    if os.path.isdir(r"c:\cygwin64") == True or os.path.isdir(r"C:\cygwin") == True:
                        dlg4 = wx.MessageDialog(self, "Download Complete\n\nWould you like to extract the files using cygwin? (Windows only)", "Download Status", wx.YES_NO)
                        if dlg4.ShowModal() == wx.ID_YES:
                            drugPharmAssoc.extractPharmData(self.downdir+".zip")
                            dlg4.Destroy()
                            return()
                        else:
                            dlg4.Destroy()
                            return()
                    else:
                        dlg4 = wx.MessageDialog(self, "Download Complete", "Download Status", wx.OK)
                        dlg4.ShowModal()
                        dlg4.Destroy()
                        return()
            dlg2 = wx.MessageDialog(self, "Click OK to download data to "+self.downdir+".zip"+"\n\nIt may take a few minutes for the file to appear", "Download In Progress", wx.OK | wx.CANCEL)
            if dlg2.ShowModal() == wx.ID_OK:
                print('Beginning download of pharmocologic index files...\n\n')
                drugPharmAssoc.getPharmData(self.downdir+".zip")
                print('Download complete\n\n')
            dlg2.Destroy()
            
            if os.path.isdir(r"c:\cygwin64") == True or os.path.isdir(r"C:\cygwin") == True:
                dlg3 = wx.MessageDialog(self, "Download Complete\n\nWould you like to extract the files using cygwin? (Windows only)", "Download Status", wx.YES_NO)
                if os.path.isfile(self.downdir+".zip") == True:
                    if dlg3.ShowModal() == wx.ID_YES:
                        drugPharmAssoc.extractPharmData(self.downdir+".zip")
                dlg3.Destroy()
            else:
                dlg3 = wx.MessageDialog(self, "Download Complete", "Download Status", wx.OK)
                dlg3.ShowModal()
                dlg3.Destroy()
             
        dlg.Destroy()
    
    ## Extract pharmocologic index data from the raw XML files
    def OnExtractClass(self, e):
        self.outfilename = ''
        self.indirname = ''
        dlg = wx.DirDialog(self, "Choose the XML file Directory", "", wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.indirname = dlg.GetPath()
            self.initloc = '\\'.join(self.indirname.split('\\')[0:-1])
            dlg2 = wx.FileDialog(self, "Save as", self.initloc, "", "*.*", wx.FD_SAVE)
            if dlg2.ShowModal() == wx.ID_OK:
                self.outfilename = dlg2.GetPath()
                xmlpath = self.indirname.replace('\\', '/')+'/*'
                drugPharmAssoc.writeToCSV(xmlpath, self.outfilename)
            dlg2.Destroy()
        dlg.Destroy()

    ## Method for selecting two files and comparing them for differential
    ## entries.  The method used is the equivalent of symmetric difference
    ## in set theory.  See the python documentation on sets for more information.
    def OnPharmDiff(self, e):
        timestamp = mainQuery.getTime()
        self.dirname = ''
        self.filelist = []
        dlg = wx.FileDialog(self, "Choose a file", "", "", "*.*", wx.FD_MULTIPLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.filelist = dlg.GetPaths()
            self.dirname = dlg.GetDirectory()
            if os.path.isfile(self.filelist[0]) and os.path.isfile(self.filelist[1]):
                dlg2 = wx.MessageDialog(self, "Proceed with file differentiation?\n\nFiles will be written to:\n"+str(self.dirname)+r"\pharmDiffResults"+timestamp+".csv", "Pharm Differential Analysis", wx.YES_NO)
                if dlg2.ShowModal() == wx.ID_YES:
                    drugPharmAssoc.pharmDiff(self.filelist[0], self.filelist[1], str(self.dirname)+r"\pharmDiffResults"+timestamp+".csv")
                dlg2.Destroy()
        dlg.Destroy()
        
### Main ###
#app = wx.App(True, filename=r'C:\Users\lakinsm\Documents\PosterNIH\Term\HUGOQueryModule\errorlog.txt')
if __name__ == "__main__":
    app = wx.App(False)
    frame = MainWindow(None, 'hquery - A BTRIS Extension for HGNC and NLM Data v0.1.1')
    app.MainLoop()
