# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 11:10:46 2017

@author: avandenbroucke

see also https://stackoverflow.com/questions/34276663/tkinter-gui-layout-using-frames-and-grid
"""

import sys

if not('.' in sys.path): sys.path.append('.')
#import midi24txt 

import tkinter 
#from tkFileDialog import *
from tkinter import filedialog
from tkinter import messagebox
import pandas
import numpy as np
import scipy.stats
import time
import datetime
import matplotlib.pyplot as plt
import os
if __package__ is None or __package__ == '':
    from pyCyte_EXP.DropCV import ReaderDat
else:
    from ..DropCV import ReaderDat

#from PIL import ImageTk, Image
# thinking in tkinter http://www.ferg.org/thinking_in_tkinter/all_programs.html

class TheGui:
    def __init__(self, parent):
        self.ReaderDat = ReaderDat.ReaderDat()
        self.wdir = os.getcwd()
       
        # create all of the main containers
        self.top_frame = tkinter.Frame(parent,  width=340, height=150, pady=3)
        self.center_frame = tkinter.Frame(parent,  width=340, height=300, padx=3)
        self.btm_frame = tkinter.Frame(parent, bg='white', width=340, height=145, pady=3)

        # layout main containers
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        
        # put main containers on grid
        self.top_frame.grid(row=0, sticky="ew")
        self.center_frame.grid(row=1, sticky="ew")
        self.btm_frame.grid(row=2, sticky="ew")
  
        #------- Top Frame  ----------#
        # variables assigned in top frame
        self.useInternalStd = tkinter.BooleanVar()
        self.supportedReaders = self.ReaderDat.getSupportedReaders();
        self.selectedReader = tkinter.StringVar()
        self.selectedReader.set( self.supportedReaders[0] )
        self.supportedLUTs = self.getSupportedLUTs()
        print(self.supportedLUTs)
        self.selectedLUT = tkinter.StringVar()
        self.selectedLUT.set( self.supportedLUTs[0])
        self.MODES = [ ("FinalTest","FT"), ("CCT","CCT") ]
        self.operationMode = tkinter.StringVar()
        self.operationMode.set("FT")
        #widgets top frame
               #InternalStandardCheckBox
        self.c1 = tkinter.Checkbutton(self.top_frame, width='20', text="Use InternalStandard", variable=self.useInternalStd,  command=self.selc1)
        #Reader label and OptionMenu
        self.lm1 = tkinter.Label(self.top_frame, width='10', text='Reader:')        
        self.m1 = tkinter.OptionMenu(self.top_frame, self.selectedReader, *self.supportedReaders,  command=self.setLUT)
        #LUT label and OptionMenu
        self.lm2 = tkinter.Label(self.top_frame, width='10',text='LUT:')
        self.m2 = tkinter.OptionMenu(self.top_frame,  self.selectedLUT, *self.supportedLUTs,  command=self.printLUT)

         # modes radiobutton:
        i=0     
        for text, mode in self.MODES:
            self.b1 = tkinter.Radiobutton(self.top_frame, text=text, width='10', variable=self.operationMode, value=mode , indicatoron = 0 )
            self.b1.grid(row=i, column=3, padx="15", sticky="w")   
            i += 1
        self.c1.grid(row=1,column=0, sticky="ew")
        self.m1.grid(row=0,column=2,sticky="ew")
        self.lm1.grid(row=0,column=1)
        self.m2.grid(row=1,column=2,sticky="ew")
        self.lm2.grid(row=1,column=1)
     
        #------- Center Frame  ----------#
        #variables assigned in Center Frame
        self.MatechFileName1 = tkinter.StringVar() # http://effbot.org/tkinterbook/entry.htm
        self.MatechFileName2 = tkinter.StringVar()
        self.ReaderFileList = []
        self.OutPutFolder = tkinter.StringVar() # http://effbot.org/tkinterbook/entry.htm
        self.OutPutFolder.set(self.wdir)
        
        #widget center frame
        #Matech File 1
        self.lblIn1 = tkinter.Label(self.center_frame, text='Matech File 1:', anchor='w',width='15')      
        self.entIn1 = tkinter.Entry(self.center_frame, width='72', textvariable=self.MatechFileName1)
        self.btnIn1 = tkinter.Button(self.center_frame, width='8', text='Browse', command=self.btnInBrowseClick1)
        #Matech File 2
        self.lblIn2 = tkinter.Label(self.center_frame, text='Matech File 2:', anchor='w',width='15')
        self.entIn2 = tkinter.Entry(self.center_frame,  width='45', textvariable=self.MatechFileName2)
        self.btnIn2 = tkinter.Button(self.center_frame,  width='8', text='Browse', command=self.btnInBrowseClick2)
        #Reader File list
        self.lblInRF = tkinter.Label(self.center_frame, text='Reader Files:', anchor='w',width='15')
        self.btnInLF = tkinter.Button(self.center_frame,width='8', text='Load Files', command=self.btnSelectFiles)
        self.frmfilebox = tkinter.Listbox(self.center_frame, width=20, height=10)
        self.frmfilebox.insert(tkinter.END, *self.ReaderFileList)
        #Output Folder
        self.lblOut1 = tkinter.Label(self.center_frame, text='Output folder:', anchor='w',width='15')       
        self.entOut1 = tkinter.Entry(self.center_frame, width='45', textvariable=self.OutPutFolder)
        self.btnOut1 = tkinter.Button(self.center_frame, width='8',text='Browse', command=self.btnSelectOutputFolder1)
    
        rowcnt = 0
        span = 1
        self.lblIn1.grid(row=rowcnt,column=0,padx=5,pady=5,sticky="w")
        self.btnIn1.grid(row=rowcnt,column=1,padx=5,sticky="e")
        rowcnt +=span
        self.entIn1.grid(row=rowcnt,column=0,columnspan=2,rowspan=span,padx=5,sticky="ew")
        
        rowcnt += span
        self.lblIn2.grid(row=rowcnt,column=0,padx=5,pady=5,sticky="w")
        self.btnIn2.grid(row=rowcnt,column=1, padx=5, sticky="e")
    
        rowcnt +=span 
        self.entIn2.grid(row=rowcnt,column=0,columnspan=2,rowspan=span,padx=5,sticky="ew")
        
        rowcnt +=span 
        self.lblInRF.grid(row=rowcnt,column=0,padx=5,pady=5,sticky="w")
        self.btnInLF.grid(row=rowcnt,column=1,padx=5,sticky="e")
        
        rowcnt +=span
        span = 10
        self.frmfilebox.grid(row=rowcnt,column=0, rowspan=span,padx=5,columnspan=2,sticky="wens")
 
        rowcnt +=span 
        self.lblOut1.grid(row=rowcnt,column=0,padx=5,pady=5,sticky="w")
        self.btnOut1.grid(row=rowcnt,column=1,padx=5,sticky="e")
        
        rowcnt +=span
        self.entOut1.grid(row=rowcnt,column=0,columnspan=2,padx=5,sticky="ew")
  
        #------- Bottom Frame  ----------#
        #variables assigned in Bottom Frame
      
        #widget bottom frame
        # Go Button
        self.btnGo = tkinter.Button(self.btm_frame, text='Calculate', width='15', command=self.btnGoClick)
        # Quit Button
        self.btnQuit = tkinter.Button(self.btm_frame,text='Quit',width='14',command=self.btnQuitClick)
        # Status bar
        self.status = tkinter.Label(self.btm_frame, width='27',fg="white",bg="gray", text='Status: Waiting')
    
        self.btnGo.grid(row=0,column=0,padx=5,sticky="w")
        self.status.grid(row=0,column=1,padx=5,sticky="ew")
        self.btnQuit.grid(row=0,column=2,padx=5)
        
        
    #------- handle commands ----------#
    def selc1(self):
     #   self.lblIn.config(text = self.inChoices[self.varRadio.get()] 
     #       + ' Input File Path')
     #   self.lblOut.config(text = self.inChoices[(self.varRadio.get()+1)%2] 
     #       + ' Output File Path')
        self.setLUT(None)
        if (self.useInternalStd.get()) == True :
            self.entIn1.config(state='disabled')
            self.entIn2.config(state='disabled')
        else:
            self.entIn2.config(state='normal')
            self.entIn1.config(state='normal')
        print(' selc1 :: Internaldtd = ', str(self.useInternalStd.get()))
        
     
    def btnInBrowseClick1(self):             
        rFilepath = filedialog.askopenfilename(defaultextension='*', 
            initialdir=self.wdir, initialfile='', parent=self.center_frame, title='select a file') 
        self.MatechFileName1.set(rFilepath)
        self.wdir = os.path.dirname(rFilepath)
        print(' Filename : ' ,  self.entIn1.get())
        
    def btnInBrowseClick2(self):             
        rFilepath = filedialog.askopenfilename(defaultextension='*', 
            initialdir=self.wdir, initialfile='', parent=self.center_frame, title='select a file') 
        self.MatechFileName2.set(rFilepath)
        self.wdir = os.path.dirname(rFilepath)
        print(' Filename : ' ,  self.entIn2.get(), ' FilePath : ', rFilepath)    
    
    def btnSelectOutputFolder1(self):             
        rOutputFolder = filedialog.askopenfilename(defaultextension='*', 
            initialdir=self.wdir, initialfile='', parent=self.center_frame, title='select a folder') 
        self.OutPutFolder.set(rOutputFolder)
        
        
    def getSupportedLUTs(self):
        return list(self.ReaderDat.getCalibrations(reader = str(self.selectedReader.get()), UseInternalStd = self.useInternalStd.get()).keys())
        
        
    def setLUT(self, event):
        self.supportedLUTs = self.getSupportedLUTs()
        print(' setLUT :: supportedLUTS = ', self.supportedLUTs )
        menu = self.m2['menu']
        menu.delete(0,'end')
        for lut in self.supportedLUTs:
            menu.add_command(label=lut,command=tkinter._setit(self.selectedLUT, lut))
        print(' setLUT :: READER = ', self.selectedReader.get())
        
    def printLUT(self, event):
        print(self.selectedLUT.get())    
    
    def btnSelectFiles(self):
        self.ReaderFileList = filedialog.askopenfilenames(title='please select files you want to process',initialdir=self.wdir)    
        if len(self.ReaderFileList) > 0 :
            self.wdir = os.path.dirname(self.ReaderFileList[0])
        self.OutPutFolder.set(self.wdir)    
        self.frmfilebox.delete(0,tkinter.END)
        self.frmfilebox.insert(tkinter.END, *self.ReaderFileList)
        
    def btnGoClick(self):  
        if len(self.ReaderFileList) == 0:
            messagebox.showerror("Error", "Please specify some reader files to parse")
            return
        self.ReaderDat.setStdCurve(lutdate=self.selectedLUT.get(),reader=self.selectedReader.get(),UseInternalStd=self.useInternalStd.get())
        if not(self.useInternalStd):
            if not os.path.exists(self.MatechFileName1.get()):
                messagebox.showerror("Error", "Matech File 1 does not exist")
                return
            if not os.path.exists(self.MatechFileName2.get()):
                messagebox.showerror("Error","Matech File 2 does not exist")
                return
            self.ReaderDat.setPMTCorr(f1=self.MatechFileName1.get(),f2=self.MatechFileName2.get())
            
        prefix =  datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S')   
        outfilename = prefix + '_ReaderDat'
        fulloutfilename = self.OutPutFolder.get() + './' + outfilename    
        ncols = 4
        nrows = (len(self.ReaderFileList)+(ncols-1))//ncols
        if (nrows == 1 ):
            nrows += 1 
        fig, ax = plt.subplots(figsize=(18*ncols,10*nrows),nrows=nrows,ncols=ncols);
        row = 0
        col = 0
        allstats = []   

   
        self.status.config(text='Busy')
        self.status.config(bg='red') 
        self.status.update()
        
        for readerfile in self.ReaderFileList:    
            raw = self.ReaderDat.processReaderFile(readerfile)
            cal = self.ReaderDat.applyCalCurve(raw)
            stats = self.ReaderDat.getPrintStats(cal)
            statdict = stats._asdict()
            statdict['File'] = os.path.basename(readerfile)
           # plastic, echosn, fluid = parser(file)
            statdict['Plastic'] = 'Unknown'
            statdict['Fluid'] = 'Unknown'
            statdict['EchoSN'] = 'E5XX'
            allstats.append(statdict)
        #print( ' row .. ', row, ' col ..', col)
            self.ReaderDat.plotReaderDat(cal,stats, ax=ax[row][col], title=os.path.basename(readerfile))
            if col < (ncols-1) :
                col +=1
            else:
                col = 0
                row +=1
        plt.savefig(fulloutfilename + '.png')
        AllStats = pandas.DataFrame(allstats)
        CC = ['File','EchoSN','Plastic', 'Fluid','Mean','RawCV','CV','Empties','Outlier','Reliability','PMTCorr']
        AllStats = AllStats[CC]
        AllStats.to_csv(fulloutfilename +'_Summary.csv', index=False)  
        
   #     toplevel = tkinter.Toplevel()
   #     toplevel.title('pyDrovCV - Results')
   #     img = tkinter.PhotoImage(file = (fulloutfilename + '.png'))
        # in inches
  #      fwidth = 18*ncols
   #     fheight = 10*nrows
   ##     dpi = 48
     #   panelw = 1440
     #   panelh = 500
    #    scalew = round( fwidth*dpi/panelw )
    #    scaleh = round( fheight*dpi/panelh )
   #     print('scaleh: ', scaleh, 'scalew: ', scalew)
  #      mimg = img.subsample(scalew, scaleh)
  #      print(' fwidth: ', fwidth, ' fheight: ', fheight)
 #       panel = tkinter.Label(toplevel, image=mimg, height = panelh, width=panelw)
#        panel.image = mimg
#        panel.pack(expand="yes",fill="both")
      
         
        self.status.config(text='Done')
        self.status.config(bg='green') 
        
        
    def btnQuitClick(self):
        root.destroy()
        

root = tkinter.Tk()
root.title("pyDropCV")
#http://infohost.nmt.edu/tcc/help/pubs/tkinter/std-attrs.html#geometry
#http://infohost.nmt.edu/tcc/help/pubs/tkinter/toplevel.html
root.geometry("450x500+10+10")
gui = TheGui(root)
root.mainloop()