#-------------------------------------------------------------------------------
#
# Name:     hquery.pyw
# Purpose:  Query a list of genes against the HUGO database, return tab file
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

import os
import wx
import webbrowser

try:
    import requests
except ImportError:
    print('Please install the requests package: pip install requests')
    raise
    
def dumpclean(obj, outfile):
    if type(obj) == dict:
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                outfile.write(str(k)+"\n")
                dumpclean(v, outfile)
            else:
                outfile.write('%s : %s' % (k, v))
    elif type(obj) == list:
        for v in obj:
            if hasattr(v, '__iter__'):
                dumpclean(v, outfile)
            else:
                outfile.write(str(v)+"\n")
    else:
        outfile.write(str(obj)+"\n")
    
def hugoQuery(List, Dir):
    print(Dir)
    prefix = 'http://rest.genenames.org/fetch/symbol/'
    headers = {'Accept': 'application/json'}
    
    frame.count = 0
    frame.progressMax = len(List)
    frame.keepGoing = True
    frame.skip = False
    
    frame.dialog = wx.ProgressDialog("Query Status", "Query completion:", frame.progressMax, style=wx.PD_APP_MODAL | wx.PD_CAN_ABORT | wx.PD_ELAPSED_TIME)
                    
    with open(Dir+"\GeneQueryResults.txt", 'w') as f:
        with open(Dir+"\QueryReport.txt", 'w') as g:
            for gene in List:
                r = requests.get(prefix+gene, headers=headers)
                if r.status_code is 200:
                    dumpclean(obj=r.json()['response']['docs'][0], outfile=f)
                    f.write("\n\n")
                else:
                    g.write(str(r.status_code)+": "+gene+"\n")
                frame.count += 1
                (frame.keepGoing, frame.skip) = frame.dialog.Update(frame.count, str(frame.count)+" of "+str(frame.progressMax))
    frame.dialog.Destroy()

class MainWindow(wx.Frame):

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(-1,-1))
        #panel = wx.Panel(self)
        self.CreateStatusBar()
        
        filemenu = wx.Menu()
        
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Load File", " Load a gene batch file")
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About", " Information about hquery")
        menuGit = filemenu.Append(wx.ID_ANY, "&GitHub Repository", " See up-to-date information and source code on GitHub")
        menuExit = filemenu.Append(wx.ID_EXIT, "&Exit", " Terminate the Program")
        
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File")
        self.SetMenuBar(menuBar)
        
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnGit, menuGit)
        
        self.Show(True)
        
    def OnOpen(self, e):
        """ Open a file """
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
    
    def OnGit(self, e):
        webbrowser.open("https://github.com/lakinsm/hquery")
        
    def OnAbout(self, e):
        dlg = wx.MessageDialog(self, "Author: Steven Lakin\nContact: Steven.Lakin@colostate.edu\n\nThis program was developed to batch query gene keys against the HUGO database.\n\nSee https://github.com/lakinsm/hquery for details and current information.", "About hquery", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
    
    def OnExit(self, e):
        self.Close(True)
        

app = wx.App(False)
frame = MainWindow(None, 'Batch Query for HUGO Database')
app.MainLoop()
