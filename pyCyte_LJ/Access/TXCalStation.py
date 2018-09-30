# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 14:16:51 2017

@author: lchang
"""
from ..NNCalibrate import NNSwapAdjust as NN
#import pyCyte.TSwap.TxDB as TxDB
from ..ToolBox import SimpleTools as st

import tkinter
from tkinter import *
from tkinter import messagebox
#from tkinter.ttk import *

import matplotlib
matplotlib.use('TKAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import os
import sqlalchemy
import pyodbc
import fnmatch
import pandas as pd
import numpy as np
import datetime
import warnings
import validate
import sys
import time
import subprocess
import winreg

"""
This widget is used in TxSwap Initial Calibration station (ACCESS-1619) to set up calibration sessions and clean up after.  
"""

class TXCalSetup():
    def __init__(self):
        
        warnings.filterwarnings("ignore")
        self.ver = '1.0'
        self.db = []
        self.des = []
        self.dlog = []
        self.TX = ''
        self.MC = ''
        self.LUT = '082017'
        self.reader = 'BMG-1619'
        self.Echo = 'E1419' #hard-coded
        self.sqlengine = 'E5XX-1419\\LABCYTE'
        self.filesqlengine = 'mssql+pyodbc://sa:password@E5XX-1419_ODBC' #hard-coded for E1419
#        self.sqlengine = 'mssql+pyodbc://Playground_LC'
#        self.sqlengine = 'LCHANG-NUC\\LABCYTE'
#        self.wdir = r'\\seg\transducer\Master_Templates\Golden_Databases'
        self.wdir = 'C:\\Temp'
        self.activeDatabase = self.readRegistry()
        
        self.fields = ['Echo: '+self.Echo, 'Connected to: '+self.sqlengine.split('@')[-1], 'Transducer SN', 'MatchingCircuit SN', 'LUT','Reader']
        self.nonedit = ['Echo: '+self.Echo, 'Connected to: '+self.sqlengine.split('@')[-1]]
        
        self.reader_options = ('BMG-1619', 'BMG-1310')
        self.LUT_options = ('082017','032017','022018')
        
        self.runGUI()
        self.root.mainloop()
        
    def runGUI(self):
                
        pady = 10
        padx = 100
        bdwidth = 5
        
        self.root = tkinter.Tk()
        self.root.title('Setup Transducer Calibration')
        self.root.geometry('{}x{}'.format(1100, 800))
        self.root.columnconfigure(0, {'minsize': 500})
        self.root.columnconfigure(1, {'minsize': 600})
        
        self.topframe = tkinter.Frame(self.root)
        self.topframe.grid(row = 1, column = 0, columnspan=1, sticky = 'n')
        
        self.mainframe = tkinter.Frame(self.root, relief='raised', borderwidth = bdwidth, pady = pady)
        self.mainframe.grid(row = 6, column = 0, rowspan = 5, columnspan=1, sticky = 'n')
        
        self.mainframe2 = tkinter.Frame(self.root, relief='raised', borderwidth = bdwidth, pady = pady)
        self.mainframe2.grid(row = 6, column = 1, rowspan = 3, columnspan=1, sticky = 'n')
        
        self.mainframe3 = tkinter.Frame(self.root, relief='raised', borderwidth = bdwidth, pady = pady+5)
        self.mainframe3.grid(row = 9, column = 1, rowspan = 8, columnspan=1, sticky = 'n')

        self.bottomframe = tkinter.Frame(self.root)
        self.bottomframe.grid(row = 15, column =0, columnspan = 1, sticky = 's')        
        
        self.readerSelect = tkinter.StringVar(self.root)
        self.readerSelect.set(self.reader_options[0])
        self.LUTSelect = tkinter.StringVar(self.root)
        self.LUTSelect.set(self.LUT_options[0])
        self.TXSelect = tkinter.StringVar()
        self.TXSelect.set('')
        self.MCSelect = tkinter.StringVar()
        self.MCSelect.set('')
        self.GoldDBpath = tkinter.StringVar()
        self.GoldDBpath.set('')
#        self.statusInd = tkinter.StringVar()
        self.statusInd = ''
        self.statusInd2 = ''
        self.statusInd3 = ''
        self.indicatortext = '(7-digit limit)'
        
        label0 = tkinter.Label(self.topframe, text = "Echo: "+ self.Echo)
        label1 = tkinter.Label(self.topframe, text="Connected to:  "+self.sqlengine.split('@')[-1])
        label2 = tkinter.Label(self.topframe, text="TXCalibrationSetup Ver. "+self.ver)
        label2.grid(sticky='n')
        label0.grid(sticky='n')
        label1.grid(sticky='n')
                
        label4 = tkinter.Label(self.mainframe, text="Transducer SN", padx = padx, pady = pady-5, fg = "blue")
        label4.grid(column = 0, sticky = 'n')
        self.TXSelect.trace('w', lambda nm, idx, mode, var=self.TXSelect: validate_int(var))
        self.ent1 = tkinter.Entry(self.mainframe, textvariable = self.TXSelect)
        self.ent1.grid(column = 0, sticky = 'n')
        label4a = tkinter.Label(self.mainframe, text=self.indicatortext, font = ('italic', 8), pady=5)
        label4a.grid(column = 0, sticky = 'n')
        
        label5 = tkinter.Label(self.mainframe, text="Matching Circuit SN", padx = padx, pady = pady, fg = "blue")
        label5.grid(column = 0, sticky = 'n')
        self.MCSelect.trace('w', lambda nm, idx, mode, var=self.MCSelect: validate_int(var))
        self.ent2 = tkinter.Entry(self.mainframe, textvariable = self.MCSelect)
        self.ent2.grid(column = 0, sticky = 'n')
        label5a = tkinter.Label(self.mainframe, text=self.indicatortext, font = ('italic', 8), pady=5)
        label5a.grid(column = 0, sticky = 'n')
        
        label6 = tkinter.Label(self.mainframe, text="DMSO LUT", padx = padx, pady = pady, fg = "blue")
        label6.grid(column = 0, sticky = 'n')
        
        self.optmenu1 = tkinter.OptionMenu(self.mainframe, self.LUTSelect, *self.LUT_options)
        self.optmenu1.grid(column = 0, sticky = 'n')
               
        label7 = tkinter.Label(self.mainframe, text="Reader", padx = padx,pady = pady, fg = "blue")
        label7.grid(column = 0, sticky = 'n')
        
        self.optmenu2 = tkinter.OptionMenu(self.mainframe, self.readerSelect, *self.reader_options)
        self.optmenu2.grid(column = 0, sticky = 'n')
        
        self.label8 = tkinter.Label(self.bottomframe, text=self.statusInd, font = 'Courier 10 bold', pady=pady, fg = 'red')
        self.label8.grid(column = 0, sticky = 'n')
          
        self.button1 = tkinter.Button(self.mainframe, text = 'Start New Calibration', command = self.createButton, pady=pady, fg = 'white', bg = 'blue', borderwidth = 10)
        self.button1.grid(column = 0, pady=pady)
        self.button1a = tkinter.Button(self.mainframe, text = 'Update registry', command = self.writeRegistry, pady=pady)
        self.button1a.grid(column = 0, pady=pady)
        self.button1a.config(state='disabled')
        
        label3 = tkinter.Label(self.bottomframe, text="Restore Database to ", padx = padx, pady = pady, fg = "blue")
        label3.grid(column = 0, sticky = 'n')
        self.label3a = tkinter.Label(self.bottomframe,text=self.activeDatabase, font = 'Courier 10 bold', fg = 'black' )
        self.label3a.grid(column=0, sticky ='n')
        self.ent0 = tkinter.Entry(self.bottomframe, width=75, textvariable=self.GoldDBpath)
        self.ent0.grid(column = 0, sticky = 'n', padx=15)
        self.button0 = tkinter.Button(self.bottomframe, text='Load Golden Database', command=self.browseButtonClick)
        self.button0.grid(column = 0, sticky ='e')
        
        self.button2 = tkinter.Button(self.bottomframe, text='Restore Database', command=self.restoreDBButtonClick)
        self.button2.grid(column = 0, sticky = 'n')
        self.button2.config(state='normal')
        self.button3 = tkinter.Button(self.bottomframe, text = 'Update TX SN to Database', command = self.updateSNButton, pady=10)
        self.button3.grid(column = 0)
        self.button3.config(state='normal')
    
        buttonQuit = tkinter.Button(self.root,text='Quit',command=self.quitButtonClick, padx = 20, pady = 10)
        buttonQuit.grid(column = 1, row = 0, rowspan = 4, sticky = 'ne')

        def validate_int(var):
            new_value = var.get()
            if len(new_value) <= 7:
                try:
                    new_value == '' or int(new_value)
                    validate.old_value = new_value
                except:
                     var.set(validate.old_value)    
                     validate.old_value = new_value[0:-1]
            else:
                var.set(validate.old_value)    
                validate.old_value = new_value[0:7]
        
        self.label12a = tkinter.Label(self.mainframe2, text='Active database: '+self.activeDatabase, font = 'Courier 10 bold')     
        self.label12a.grid(column = 1, sticky = 'n')
        self.button7 = tkinter.Button(self.mainframe2, text = 'Enable Neural Nework', command = self.NNEnable, pady=pady,  fg = 'white', bg = 'black', borderwidth = 10)
        self.button7.grid(column = 1, sticky = 'n')
        label11 = tkinter.Label(self.mainframe2, text="NOTE: Run the Neural Network only after EPC calibration", padx = padx, pady = pady, fg = 'blue')
        label11.grid(row=2, column = 1, sticky = 'n')
        self.button6 = tkinter.Button(self.mainframe2, text = 'Calculate Adjustments', command = self.NNButtonClicked)
        self.button6.grid(column = 1)
        self.button6.config(state='disabled')
        self.label12 = tkinter.Label(self.mainframe2, text=self.statusInd3, font = 'Courier 10 bold', pady=pady, fg = 'red')
        self.label12.grid(column = 1, sticky = 'n')

        
        self.label10a = tkinter.Label(self.mainframe3, text='Active database: '+self.activeDatabase, font = 'Courier 10 bold')     
        self.label10a.grid(column = 1, sticky = 'n')        
        label10 = tkinter.Label(self.mainframe3, text="Click here to wrap up calibration", padx = padx, pady = pady, fg = 'blue')
        label10.grid(row =7, column = 1, sticky = 'n')
        self.button4 = tkinter.Button(self.mainframe3, text = 'Wrap Up Calibration', command = self.calDoneButtonClicked, pady=pady,  fg = 'white', bg = 'blue', borderwidth = 10)
        self.button4.grid(column = 1, pady = pady)
        self.label9 = tkinter.Label(self.mainframe3, text=self.statusInd2, font = 'Courier 10 bold', pady=pady, fg = 'red')
        self.label9.grid(column = 1, sticky = 'n')
        self.button5 = tkinter.Button(self.mainframe3, text = 'Turn ON Classification', command = self.turnOnClass)
        self.button5.grid(column = 1, pady = pady)
        self.button5.config(state='disabled')
        self.button8 = tkinter.Button(self.mainframe3, text = 'Create Swissard Package', command = self.createSwissClicked)
        self.button8.grid(column = 1, pady = pady)
        self.button8.config(state='disabled')
        self.button7 = tkinter.Button(self.mainframe3, text = 'Upload to Bonita (lighthouse)', command = self.BonitaClicked)
        self.button7.grid(column = 1, pady = pady)
        self.button7.config(state='disabled')
   
    def checkValidDB(self):
        if len(self.GoldDB) > 1:
            self.button2.config(state='normal')
        
    def createSwissClicked(self):
        self.button8.config(state='disabled')
#        cipherPath = r'\\Lighthouse\Cipher\cipher.exe' 
        cipherPath = 'D:\\Labcyte\\Cipher'
        location = 'C:\\Labcyte\\SwissardPackages\\'
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        foldername = 'SwissardPackage__'+self.transducer+'__'+timestamp
        self.fullpath = os.path.join(location, foldername)
        self.databasefile = os.path.join(self.fullpath,self.transducer+'.bak')

        
        try:
            x=subprocess.run([cipherPath, '-p', 'c1ph3r', '-e', '-s', self.sqlengine, '-n', self.transducer], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
            if x.returncode == 0:
                print("\t"+x.stdout.decode("utf-8"))
            else:
                print("\tError code: " + str(x.returncode))
                print("\t"+x.stderr.decode("utf-8"))
        
            sys.stdout.flush()
            if not os.path.exists(self.fullpath):
                os.makedirs(self.fullpath)
            
            try:
                self.backupDatabase(self.transducer, self.databasefile)
                self.statusInd3 = 'Database Backed Up to '+location
                self.updateText()
                
                try:
                    os.chdir(location)
                    st.zipfolder(folder=self.fullpath)
                    self.statusInd3 = 'Swissard package (zipped) created in '+location
                    self.updateText()
                    self.button8.config(state='disabled')
                    self.button7.config(state='normal')
                except:
                    self.statusInd3 = 'Swissard package unsuccessful'
                    self.updateText()
                    self.button8.config(state='normal')
            except:
                self.statusInd3 = 'Database not backed up.  Unable to create Swissard package'
                self.updateText()
                self.button8.config(state='normal')
        except:
            self.statusInd3 = 'Database not encrypted.  Unable to proceed'
            self.updateText()
            self.button8.config(state='normal')
    
    def backupDatabase(self,dbName, backupPath):
        print('Backing up database...', end='')   
        self.cursor.execute("BACKUP DATABASE "+ dbName + " TO DISK = '"+ backupPath +"'")
        print('Back up done')
    
    def BonitaClicked(self):
        a = TxDB.TxDB()
        dbver = self.dbversion['ParameterValue'][0]
        dbfile = os.path.join(self.fullpath,self.transducer+'.bak')
        try:
            a.addTransducerDB(dbfile, self.transducer, self.MC, self.Echo, 'Calibration', 'Opt', str(dbver))
        except:
            self.statusInd2 = 'ERROR: Not uploaded to Bonita'
            self.updateText()
    
    def NNButtonClicked(self):
        transducerInfoFile = self.readTXInfoFile()
        self.transducer = transducerInfoFile.iloc[0][0].split('_')[0]
        result = messagebox.askyesno(title = 'Confirm Database Change ' + self.transducer, message='Clicking YES will change the database.  Are you sure?', icon='warning')
        if result == True:
                destroot = '\\\\seg\\transducer\\Transducers\\'+transducerInfoFile.iloc[0][0]+'\\Calibration_E1419'
    
                #   Looks for the latest Swissard generated folder:
                if 'Calibration' in destroot:
                    folderlist = fnmatch.filter(next(os.walk(destroot))[1], '*-*-*_*-*-*')
                    folderlist.sort()
                    destination = destroot+'\\'+folderlist[-1]
                    plotPath = os.path.join(destination,'NN_Diagnostics')
                    if not os.path.exists(plotPath):
                        os.makedirs(plotPath)
                try:
                    NN.NNAnalyze(dbServer=self.sqlengine, DBName = self.transducer, savePlotPath = plotPath)
                    self.statusInd3 = 'Neural Network successful on '+self.transducer
                    self.updateText()
                except:
                    self.statusInd3 = 'Unsuccessful on '+self.transducer
                    self.updateText()
                    sys.exit([1])
        else:
            self.statusInd3 = 'No Changes Were Made.'
            self.updateText()
    
    def calDoneButtonClicked(self):
        self.connectDB()
        transducerInfoFile = self.readTXInfoFile()
        self.transducer = transducerInfoFile.iloc[0][0].split('_')[0]
        self.MC = transducerInfoFile.iloc[0][0].split('_')[-1]
        self.DB = '['+self.transducer+'].[dbo].[Transducer]'  
        try:        
            exe0 = 'SELECT * from '+ self.DB
            exe = 'SELECT [ParameterValue] FROM ['+self.transducer+"].[dbo].[Parameter] WHERE ParameterName = 'DatabaseRevision'"
            self.dbversion = pd.read_sql(exe, self.cnxn)
            self.cursor.execute(exe0)
            self.statusInd2 = 'Wrapping up calibration for '+self.transducer
            self.updateText()
            self.button5.config(state='normal')
            
        except:
            self.statusInd2 = 'Invalid Database'
            self.updateText()
            message = ['Invalid Database']
            messagebox.showinfo('Warning: Database '+self.transducer+' not found.  Unable to proceed.  Please check if database is encrypted', '\n'.join(message))    
        
    def NNEnable(self):
        self.button6.config(state='normal')
        self.button7.config(state='disabled')
        self.statusInd3 = 'Neural Network enabled'
        self.updateText()
        
    def turnOnClass(self):
        exe = 'UPDATE ['+ self.transducer + "].[dbo].[Parameter] SET ParameterValue = 'True' WHERE ParameterName = 'DoClassification'"
        try:
            self.cursor.execute(exe)
            self.button3.config(state='disabled')
            self.statusInd2 = 'Classification turned on for '+self.transducer
            self.updateText()
            self.button5.config(state='disabled')
            self.button8.config(state='normal')
        except:
            pass

    def updateText(self):
         # make first change
#        oldText = self.label8.cget("text")        
        self.root.update_idletasks()
        newText = self.statusInd
        newText2 = self.statusInd2
        newText3 = self.statusInd3        
        self.label8.configure(text=newText)
        self.label9.configure(text=newText2)
        self.label12.config(text=newText3)
#        time.sleep(1)

    def restoreDBButtonClick(self):
        self.connectDB()
        self.transducer = self.activeDatabase
        self.GoldDB = os.path.abspath(self.GoldDBpath.get())
        if len(self.GoldDB) > 1:
            confirm = messagebox.askyesno(title = 'Confirm Restore', message = 'Restore golden database to '+self.transducer)
            if confirm == True:
                try:
                    exe1 = "RESTORE FILELISTONLY FROM DISK = N'"+self.GoldDB+"'"
                    self.filelist = pd.read_sql(exe1, self.cnxn)
                    try:        
                        exe0 = 'SELECT * from '+ self.DB
                        self.cursor.execute(exe0)
                        result = messagebox.askyesno(title = 'Database Exist!', message = self.transducer+' EXIST!  Do you want to overwrite this database?', icon='warning')
                        if result == True:
                            self.restoreDB()         
                    except:
                        print('trying to restore')
                        self.restoreDB()
                        print('yes, restoring')
                except:
                     message = ['Invalid Golden Database file']
                     messagebox.showinfo('Warning: Please check that the correct .bak file is selected', '\n'.join(message))
            else:
                messagebox.showinfo('Database not restored')
        else:
            message = ['Invalid Golden Database file']
            messagebox.showinfo('Warning: Please check that the correct .bak file is selected', '\n'.join(message))    
        


    def browseButtonClick(self):             
        rFilepath = tkinter.filedialog.askopenfilename(defaultextension='.bak', 
            initialdir=self.wdir, initialfile='', parent=self.root, title='Select the database backup file') 
        self.GoldDBpath.set(rFilepath)
        self.wdir = os.path.dirname(rFilepath)
        
    def createFolders(self):
        destination = '\\\\seg\\transducer\\Transducers\\'+self.TXCalInfo+'\\Calibration_'+self.Echo
        if not os.path.exists(destination):
            os.makedirs(destination)
        else:
            message = ['Folder already exists.  Please check that this is a new calibration.','No changes were made to the folder']
            messagebox.showinfo('Warning: Folder exist on \\seg\transducer\Transducers', '\n'.join(message))
            self.statusInd = "No modifications were made to the r'\\seg folder"
            self.updateText()
        return    
    
    def readRegistry(self):
        defaultRegPath = 'SOFTWARE\Labcyte\Echo\Server\DATA_ACCESS'
        defaultRegKey = 'Database'
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, defaultRegPath)
        dbName = winreg.QueryValueEx(k, defaultRegKey)[0]
        print('Selected database ' + dbName + ' based on registry settings.')
        return dbName
        
        
    def writeRegistry(self):
        defaultRegPath = 'SOFTWARE\Labcyte\Echo\Server\DATA_ACCESS'
#        defaultRegKey = self.transducer
        try:
#            echo = winreg.ConnectRegistry('E5XX-1419', winreg.HKEY_LOCAL_MACHINE)
#            k = echo.OpenKey(echo, defaultRegPath,0, winreg.KEY_ALL_ACCESS)
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, defaultRegPath)
            winreg.SetValueEx(k, 'Database',0, winreg.REG_SZ,self.transducer)
            winreg.CloseKey(k)
            self.statusInd = 'Registry updated with '+self.transducer
            self.updateText()
        except:
            self.statusInd = 'Registry not changed.  Please manually update registry with '+self.transducer
            self.updateText()
        self.activeDatabase = self.readRegistry()
        self.root.update_idletasks()
            
    def readTXInfoFile(self):
#        fileloc = 'C:\\Temp'
        fileloc = 'Z:\\temp' # from E1419 computer
        self.TXInfofile = fileloc+'\\TransducerSwapInfo.txt'
        transducerInfoFile = pd.read_csv(self.TXInfofile, header=None)
        return transducerInfoFile
        
        
    def createTXInfoFile(self):        
        df = []
        df.append(self.TXCalInfo)
        df.append(self.Echo)
        df.append(self.filesqlengine)
        df.append(self.reader)
        df.append(self.LUT)
        dff = pd.DataFrame(df)
        
        transducerInfoFile = self.readTXInfoFile()
        transducer = transducerInfoFile.iloc[0][0]
        if transducer != self.TXCalInfo:
            self.writeTXInfoFile(dff)
        else:
            result = messagebox.askyesno(title = 'Overwrite TX Info file in C:\Temp in Tempo Computer?', message='Transducer information already exists.  Clicking YES will overwite the info file.  Are you sure?', icon='warning')
            if result == True:
                self.writeTXInfoFile(dff)
            else:
                self.statusInd = 'No modifications were made to the TX Info file'
                self.updateText()
        return    
    
    def writeTXInfoFile(self, dff):
        dff.to_csv(self.TXInfofile, index=False, header=False)
        self.ent1.config(state='disabled')
        self.ent2.config(state='disabled')
        self.optmenu1.config(state='disabled')
        self.optmenu2.config(state='disabled')
        self.statusInd = 'New calibration information file created'
        self.updateText()
            
        
    def createButton(self):
        self.TX = self.TXSelect.get()
        self.MC = self.MCSelect.get()
        self.LUT = self.LUTSelect.get()
        self.reader = self.readerSelect.get()
        self.transducer = 'TX'+self.TX
        self.TXCalInfo = self.transducer+'_MC'+self.MC
        self.DB = self.transducer+'.dbo.Transducer'   
        
        print([self.TX, self.MC, self.LUT, self.reader])
                
        if len(str(self.TX)) == 0 or len(str(self.TX)) < 7:
            message = ['Transducer SN incorrect - 7 digits required','Try again']
            messagebox.showinfo('Error', '\n'.join(message))
        if len(str(self.MC)) == 0 or len(str(self.MC)) < 7:
            message = ['Matching Circuit SN incorrect - 7 digits required','Try again']
            messagebox.showinfo('Error', '\n'.join(message))
        else:
            self.createFolders()
            self.createTXInfoFile()
            self.button1a.config(state='normal')
#            self.writeRegistry()
#            self.button1.config(state='disabled')
#            self.button2.config(state='normal')
            
        return
                       
    def connectDB(self):
#        engine = sqlalchemy.create_engine(self.sqlengine)
#        self.s = engine.connect()
#        self.cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+self.sqlengine+';Trusted_Connection=yes;')
        self.cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=E5XX-1419\LABCYTE;Trusted_Connection=yes;') #HARD CODED for 1419
        self.cnxn.autocommit = True
        self.cursor = self.cnxn.cursor()
        print('Connected to DB')
        
    def restoreDB(self):
               
        f1 = 'C:\Temp/'+self.transducer+'.mdf'
        f2 = 'C:\Temp/'+self.transducer+'_Log.ldf'
        print(f1, f2)
        exe2 = "RESTORE DATABASE ["+self.transducer+"] FROM DISK = N'"+self.GoldDB+"'WITH MOVE N'"+self.filelist['LogicalName'].iloc[0]+"' TO N'"+f1+"', MOVE N'MEDMANdb_Log' TO N'"+f2+"', REPLACE" 

        self.newDB = self.cursor.execute(exe2)
        print('newDB')
        while self.cursor.nextset():
            pass
        
        self.button2.config(state='disabled')
        self.ent0.config(state='disabled')
        self.button0.config(state='disabled')
        self.statusInd = self.transducer+' - database successfully restored'
        self.updateText()
        self.button3.config(state='normal')
                
        
    def updateSNButton(self):
        self.DB = self.activeDatabase+'.dbo.Transducer'  
        self.TX = self.activeDatabase.replace('TX','')
        result = messagebox.askyesno(title = 'Confirm Updating TX SN into Database ' + self.DB, message='Clicking YES will change the database.  Are you sure?', icon='warning')
        if result == True:
            print('Updating TX Serial Number ...')
            self.connectDB()
            exe = 'UPDATE '+ self.DB + " SET SerialNumber = '"+str(self.TX)+"' WHERE TransducerName = 'Transducer10MHz'"
            try:
#                self.s.execute(exe)
                self.cursor.execute(exe)
                self.button3.config(state='disabled')
                self.statusInd = 'Transducer SN updated to '+self.DB
                self.updateText()
            except:
                 message = ['Database '+self.transducer+' does not exist.  TX SN not updated']
                 messagebox.showinfo('Error', '\n'.join(message))
            return
        else:
#            self.root.destroy()
            print('No adjustment made')
            return

    def quitButtonClick(self):
        self.root.destroy()
        return

def main():
    TXCalSetup()

if __name__ == "__main__":
    main()

#if __name__ == "__main__":
#   main(sys.argv[1:])
   