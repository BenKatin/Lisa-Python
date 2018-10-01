# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 03:34:54 2018

@author: avandenbroucke
"""

import sys

if not('.' in sys.path): sys.path.append('.')
#import midi24txt 

import tkinter 
#from tkFileDialog import *
from tkinter import filedialog
import os
import pandas
from tkinter import messagebox
from pyCyte.PlateQC import barCodes
from pyCyte.PlateQC import genMaps
import datetime
import shutil

class TheGui:
    def __init__(self, parent):
        self.bc = barCodes.BarCodes()
        self.wdir = os.getcwd()
       
        # create all of the main containers
        self.top_frame = tkinter.Frame(parent,  width=640, height=200, pady=3)
        self.center_frame = tkinter.Frame(parent,  width=640, height=80, padx=3)
        self.btm_frame = tkinter.Frame(parent, bg='white', width=640, height=50, pady=3)

        # layout main containers
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        
        # put main containers on grid
        self.top_frame.grid(row=0, sticky="ew")
        self.center_frame.grid(row=1, sticky="ew")
        self.btm_frame.grid(row=2, sticky="ew")
  
        #------- Top Frame  ----------#
        # variables assigned in top frame
        
        self.supportedPlateTypes = sorted(list(self.bc.plateMap['Codes'].keys()))
        self.selectedPlateType = tkinter.StringVar()
        self.selectedPlateType.set('')
        self.lm1 = tkinter.Label(self.top_frame, width='10', text='PlateType')
        self.m1 = tkinter.OptionMenu(self.top_frame, self.selectedPlateType, *self.supportedPlateTypes)
        self.m1.config(width='20')
        
        self.supportedNWells = [384,6,96,1536]
        self.selectedNWells = tkinter.IntVar()
        self.selectedNWells.set(self.supportedNWells[0])
        self.lm2 = tkinter.Label(self.top_frame, width='10', text='# Wells')
        self.m2 = tkinter.OptionMenu(self.top_frame, self.selectedNWells, *self.supportedNWells)
        
        self.supportedGeo = ['PP','LDV','RES','HB','TR']
        self.selectedGeo = tkinter.StringVar()
        self.selectedGeo.set(self.supportedGeo[0])
        self.lm3 = tkinter.Label(self.top_frame, width='10', text='Geometry')
        self.m3 = tkinter.OptionMenu(self.top_frame, self.selectedGeo, *self.supportedGeo)
        
        self.supportedFillStyle = list(self.bc.fillStyle['Codes'].keys())
        self.selectedFillStyle = tkinter.StringVar()
        self.selectedFillStyle.set('UCP')
        self.lm4 = tkinter.Label(self.top_frame, width='10', text='Fill Style')
        self.m4 = tkinter.OptionMenu(self.top_frame, self.selectedFillStyle, *self.supportedFillStyle)
        
        self.supportedFluidType = sorted(list(self.bc.fluidType['Codes'].keys()))
        self.selectedFluidType = tkinter.StringVar()
        self.selectedFluidType.set('-')
        self.lm5 = tkinter.Label(self.top_frame, width='10', text='Fluid Type')
        self.m5 = tkinter.OptionMenu(self.top_frame, self.selectedFluidType, *self.supportedFluidType)
        
        self.supportedFluidConc = sorted(list(self.bc.fluidConc['Codes'].keys()))
        self.selectedFluidConc = tkinter.StringVar()
        self.selectedFluidConc.set('-')
        self.lm6 = tkinter.Label(self.top_frame, width='10', text='Fluid Conc')
        self.m6 = tkinter.OptionMenu(self.top_frame, self.selectedFluidConc, *self.supportedFluidConc)
        
        self.supportedVersions = sorted(list(self.bc.mapVersion['Codes'].keys()))
        self.selectedVersion = tkinter.StringVar()
        self.selectedVersion.set('2')
        self.lm7 = tkinter.Label(self.top_frame, width='10', text='Map Version')
        self.m7 = tkinter.OptionMenu(self.top_frame, self.selectedVersion, *self.supportedVersions)
        
        self.supportedFillVol = sorted(list(self.bc.fillVol['Codes'].keys()))
        self.selectedFillVol = tkinter.StringVar()
        self.selectedFillVol.set('-')
        self.lm8 = tkinter.Label(self.top_frame, width='10', text='Fill Volume')
        self.m8 = tkinter.OptionMenu(self.top_frame, self.selectedFillVol, *self.supportedFillVol)
        
        self.supportedFluidKeys = [ 'PBS', 'GPS']
        self.selectedFluidKey = tkinter.StringVar()
        self.selectedFluidKey.set('PBS')
        self.lm9 = tkinter.Label(self.top_frame, width='10', text='FluidKey')
        self.m9 = tkinter.OptionMenu(self.top_frame, self.selectedFluidKey, *self.supportedFluidKeys)
        
        self.fluidscale = tkinter.BooleanVar()
        self.fluidscale.set(False)
        self.c1 = tkinter.Checkbutton(self.top_frame, width='10', text='FluidScale', variable = self.fluidscale)
       
        self.ArenaPNLab = tkinter.Label(self.top_frame, width='8', text = 'Arena PN: ')
        self.ArenaPN = tkinter.Entry(self.top_frame,width='12' )
        self.ArenaPN.insert(0,'XXX-YYYYY')
        
       # self.c1.grid(row=1,column=0, sticky="ew")
        self.m1.grid(row=0,column=1,sticky="ew",padx="10")
        self.lm1.grid(row=0,column=0)
        self.m5.grid(row=1,column=1,sticky="ew",padx="10")
        self.lm5.grid(row=1,column=0)
        self.m3.grid(row=2,column=1,sticky="ew",padx="10")
        self.lm3.grid(row=2,column=0)
        self.m2.grid(row=3,column=1,sticky="ew",padx="10")
        self.lm2.grid(row=3,column=0)
        
        self.m4.grid(row=0,column=3,sticky="ew",padx="10")
        self.lm4.grid(row=0,column=2,padx="30")
        self.m7.grid(row=1,column=3,sticky="ew",padx="10")
        self.lm7.grid(row=1,column=2)
        self.m6.grid(row=3,column=3,sticky="ew",padx="10")
        self.lm6.grid(row=3,column=2)
        self.m8.grid(row=2,column=3,sticky="ew",padx="10")
        self.lm8.grid(row=2,column=2)
        
        self.m9.grid(row=5,column=3,sticky="ew",pady="15")
        self.lm9.grid(row=5,column=2)
        self.c1.grid(row=5,column=0,sticky="ew",pady="15" )
        
        self.ArenaPNLab.grid(row=4,column=0)
        self.ArenaPN.grid(row=4,column=1,columnspan=2, pady="5")
        
         #------- Center Frame  ----------#
        self.InputFileName = tkinter.StringVar() 
         
        self.lblIn1 = tkinter.Label(self.center_frame, text='Plate Map File:', anchor='w',width='15')      
        self.entIn1 = tkinter.Entry(self.center_frame, width='110', textvariable=self.InputFileName)
        self.btnIn1 = tkinter.Button(self.center_frame, width='8', text='Browse', command=self.btnInBrowseClick1)
        
        rowcnt = 0
        span = 1
        self.lblIn1.grid(row=rowcnt,column=0,padx=5,pady=5,sticky="w")
        self.btnIn1.grid(row=rowcnt,column=1,padx=5,sticky="e")
        rowcnt +=span
        self.entIn1.grid(row=rowcnt,column=0,columnspan=2,rowspan=span,padx=5,sticky="ew")
        
        #------- Bottom Frame  ----------#
        #variables assigned in Bottom Frame
      
        #widget bottom frame
        # Go Button
        self.btnGo = tkinter.Button(self.btm_frame, text='Generate', width='15', command=self.btnGoClick)
        # Quit Button
        self.btnQuit = tkinter.Button(self.btm_frame,text='Quit',width='14',command=self.btnQuitClick)
        # Status bar
        self.status = tkinter.Label(self.btm_frame, width='27',fg="white",bg="gray", text='Status: Waiting')
    
        
        self.btnGo.grid(row=0,column=0,padx=15,sticky="e")
        self.status.grid(row=0,column=1,padx=25,sticky="ew")
        self.btnQuit.grid(row=0,column=2,padx=15, sticky="e")
    
    def btnInBrowseClick1(self):             
        rFilepath = filedialog.askopenfilename(defaultextension='*', 
            initialdir=self.wdir, initialfile='', parent=self.center_frame, title='select a file') 
        self.InputFileName.set(rFilepath)
        self.wdir = os.path.dirname(rFilepath)
        print(' Filename : ' ,  self.entIn1.get())  
        try:
            self.mapdf = pandas.DataFrame.from_csv(self.InputFileName.get(), index_col=None)
        except:
            messagebox.showerror("Error", "Problem processing file " + self.InputFileName.get())
        
        # prepopualate number of wells
        nentries = len(self.mapdf)
        if nentries not in self.supportedNWells:
            messagebox.showerror('Error', 'Number of lines in file ' + self.InputFileName.get() + ' not in ' + self.supportedNWells)
            return
        self.selectedNWells.set(nentries)
            
        
        # pre populate Geo:
        if nentries < 96:
           self.selectedGeo.set('RES')
        elif nentries < 384:
           self.selectedGeo.set('TR')
        elif nentries < 1536:
           self.selectedGeo.set('PP')
        else:
           self.selectedGeo.set('LDV')
           
        #prepoulate Fluid:
        if not self.validField('mFluid',self.mapdf):
            return
        nfluids = len(self.mapdf['mFluid'].unique())
        if nfluids == 1:
            fluid = self.mapdf['mFluid'].unique()[0]
            if fluid in self.supportedFluidType:
                self.selectedFluidType.set(fluid)
        
        # prepopulate Volume and FillStyle
        if not self.validField('mVolume',self.mapdf):
            return
        nvolumes = len(self.mapdf['mVolume'].unique())
        if nvolumes == 1:
            vol = str(self.mapdf['mVolume'].unique()[0])
            if vol not in self.supportedFillVol:
                 messagebox.showwarning('Warning', 'Volume ' + vol + ' not in barcodes:  ' + self.supportedFillVol)
                 self.selectedFillVol.set('-')
            else:
                 self.selectedFillVol.set(vol)
                 self.selectedFillStyle.set('FF')
        elif nvolumes < 9 :
            self.selectedFillStyle.set('FT')
        else:
            self.selectedFillStyle.set('UCP')
            
        # prepopulate concentration:
        if not self.validField('mConc',self.mapdf):
            return
        nconcs = len(self.mapdf['mConc'].unique())
        print(' concs: ', self.mapdf['mConc'].unique())
        if nconcs == 1:
            conc = str(self.mapdf['mConc'].unique()[0])
            if conc not in self.supportedFluidConc:
                messagebox.showwarning('Warning', 'Concentration ' + conc + ' not in barcodes: ' + self.supportedFluidConc)
            else:
                self.selectedFluidConc.set(conc)
        else:
            self.selectedFluidConc.set('-')

        return                  
       
    def validField(self,field, frame):
        if field not in frame.columns:
            messagebox.showerror('Error', 'Can\'t find header ' + field + ' in the csv file, please check file ' + self.InputFileName.get())
            return False
        return True
                     
    def btnQuitClick(self):
        root.destroy()
        return
    
    def btnGoClick(self):
        
        if self.selectedPlateType.get() not in self.supportedPlateTypes:
            messagebox.showerror('Error','Please specify a valid PlateType. You specified: ' + self.selectedPlateType.get())
            return
        
        
        thisentry = genMaps.writeMap(self.mapdf, platetype = self.selectedPlateType.get(), nwells = self.selectedNWells.get(),
                                     geo = self.selectedGeo.get(), style = self.selectedFillStyle.get(), fluid = self.selectedFluidType.get(),
                                     vol = self.selectedFillVol.get(), fluidscale = self.fluidscale.get(), fluidkey = self.selectedFluidKey.get(),
                                     conc = self.selectedFluidConc.get(), version = self.selectedVersion.get(), ArenaPN = self.ArenaPN.get())
        print(thisentry)
        # Need to append thisentry to AllMaps.
        try:
            allmapsdf =  pandas.read_csv( os.path.dirname(__file__) + './PlateMaps/AllMaps.csv' )
        except:
            messagebox.showerror('Error', ' Problem opening AllMaps.csv !')
        
        if thisentry['BarCode'] in allmapsdf['BarCode'].values:
            messagebox.showwarning('Warning','You are overriding an already existing definition !')
            allmapsdf[allmapsdf['BarCode'] == thisentry['BarCode']] = thisentry
        else:    
            index = len(allmapsdf)
            allmapsdf.loc[index] = thisentry
        
        date = datetime.datetime.now().strftime('%Y%m%d')
        filename = os.path.dirname(__file__) + './PlateMaps/AllMaps.csv' 
        filename2 = os.path.dirname(__file__) + './PlateMaps/AllMaps' + '_' + date + '.csv'
          # back up just in case
        shutil.copy2(filename,filename2)
        allmapsdf.to_csv(filename, index=False)

root = tkinter.Tk()
root.title("addPlateMap")
#http://infohost.nmt.edu/tcc/help/pubs/tkinter/std-attrs.html#geometry
#http://infohost.nmt.edu/tcc/help/pubs/tkinter/toplevel.html
root.geometry("700x350+10+10")
gui = TheGui(root)
root.mainloop()        