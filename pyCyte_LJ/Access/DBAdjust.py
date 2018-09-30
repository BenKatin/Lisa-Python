# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 14:16:51 2017

@author: lchang
"""

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
import fnmatch
import pandas as pd
import numpy as np
import datetime
import warnings

"""
This widget is used in TxSwap Initial Calibration station (ACCESS-1619) to adjust database based on ejectsweeps.  The script looks into a file in C:\Temp named 'TransducerSwapInfo.txt' to get sql connection information and transducer name (to access the correct database).

The adjustment is based on the input value in the "T2T adjust" and "CF adjust" column in the csv file with name ending with "_dBAdjust.csv" within the ejectsweep folder of the selected platetype.  The "_dBAdjust.dsv" file is an output file from the ejecsweep processing script on pyCyte.

"""

class DBAdjust():
    def __init__(self):
        
        warnings.filterwarnings("ignore")
        self.ver = '1.0'
        self.db = []
        self.des = []
        self.dlog = []
        self.plateType = 'None'
        self.parameter = 'None'
        self.tableName = 'None'
        self.paramName = 'None'
        self.var = 'None'
        self.DB = 'None'
        self.outappend = 'None'
        self.CFThresh = 0.3
#        self.fig = None
        
        self.runGUI()
        self.root.mainloop()
        
    def runGUI(self):
                
        pady = 10
        padx = 100

        options = ['None','384PPL_DMSO2','384PPL_AQ_CP','384PPL_AQ_GP2','384PPL_AQ_BP2','384PPL_AQ_SP2', '384LDVS_DMSO', '384LDVS_AQ_B2','1536LDVS_DMSO']    
        tableoptions = ['CF','T2T']
        database, echo, sqlengine, destination, PTfolder, ESfolder = self.extractDBInformation()
#        self.getDB()
        
        self.root = tkinter.Tk()
        self.root.title('Select Platetype and Adjustment Parameter')
        self.root.geometry('{}x{}'.format(800, 500))
#        self.root.withdraw()  
        self.platevar = StringVar(self.root)
        self.platevar.set(options[0])
        
        self.tablevar = StringVar(self.root)
        self.tablevar.set(tableoptions[0])
        
        label0 = tkinter.Label(self.root, text = """Echo: """+ echo)
        label1 = tkinter.Label(self.root, text="""Connected to:  """+sqlengine.split('@')[-1])
        label2 = tkinter.Label(self.root, text="""Database Information :  """+database)
        label3 = tkinter.Label(self.root, text="""DBAdjust Version: """+self.ver)
        label0.grid(row = 1, columnspan=2, sticky='e')
        label1.grid(row = 1, columnspan=2, sticky='n' + 's' + 'e' + 'w')
        label2.grid(columnspan=2, sticky='n')
        label3.grid(columnspan=2, sticky='n')
        
        label4 = tkinter.Label(self.root, text="""PlateType""", padx = padx, pady = pady, fg = "blue")
        label4.grid(column = 1, sticky = 'n')
        
#        for indx, button in enumerate(
        for indx, opt in enumerate(options):
            rbutton1 = tkinter.Radiobutton(self.root, text = opt, variable = self.platevar, value = opt, padx=20)
            rbutton1.grid(column = 1, sticky = 'w')
        
        label5 = tkinter.Label(self.root, text="""Database Adjustment Parameter""", padx = padx,pady = pady, fg = "blue")
        label5.grid(column = 1, sticky = 'n')
        
        for indx, tableopt in enumerate(tableoptions):
            rbutton2 = tkinter.Radiobutton(self.root, text = tableopt, variable = self.tablevar, value = tableopt, padx=20)
            rbutton2.grid(column = 1, sticky = 'w')
        
        self.plateType = self.platevar.get()
        self.parameter = self.tablevar.get()
        button1 = tkinter.Button(self.root, text = 'Calculate Adjustment', command = self.createButton, pady=10)
        button1.grid(column = 1)
        
        # Quit Button
        buttonQuit = tkinter.Button(self.root,text='Quit',command=self.quitButtonClick, padx = 20, pady = 10)
        buttonQuit.grid(row=1, column = 1, sticky = 'w')
        
    
    def createButton(self):
        self.plateType = self.platevar.get()
        self.parameter = self.tablevar.get()
        print(self.plateType)
        print(self.parameter)
        
        if self.plateType == 'None':
            message = ['Plate Type not specified','Try again']
            messagebox.showinfo('Warning', '\n'.join(message))
        
        else :            
            if plt.fignum_exists(1):
                self.fig.clear()
                self.ax.clear()
            self.fig, self.ax = plt.subplots(figsize=(16, 16))
            self.fig.subplots_adjust(left=0.2, right = 0.9, bottom=0.30, top=0.86)
            
            self.calcDB()
            
            if self.parameter == 'CF':
                dxlog = self.dlog[self.dlog['Description']==self.dlog['Description'].iloc[0]]
                dxdb = self.db[self.db['Description'] == '1']
                if 'CP' in self.plateType:
                    self.ax.plot(dxlog['X'], dxlog[dxlog.columns[-1]],'o', label = 'Current')
                    self.ax.plot(dxdb['X'], dxdb[self.var], 'o', color='r', label = 'Adjustment')    
                else:
                    self.ax.plot(dxlog['conc'], dxlog[dxlog.columns[-1]],'o', label = 'Current')
                    self.ax.plot(dxdb['conc'], dxdb[self.var], 'o', color='r', label = 'Adjustment')
            elif self.parameter == 'T2T':
                if 'CP' in self.plateType:
                    self.ax.plot(self.dlog['X'], self.dlog[self.dlog.columns[-1]],'o', label = 'Current')
                    self.ax.plot(self.db['X'], self.db[self.var], 'o', color='r', label = 'Adjustment')
#                    self.ax.set_xlim(self.dlog['X'].values.min()-0.1,self.dlog['X'].values.max()+0.1)
                else:
                    self.ax.plot(self.dlog['conc'], self.dlog[self.dlog.columns[-1]],'o', label = 'Current')
                    self.ax.plot(self.db['conc'], self.db[self.var], 'o', color='r', label = 'Adjustment')
#                    self.ax.set_xlim(self.dlog['conc'].values.min()-50,self.dlog['conc'].values.max()+50)
#            self.ax.set_ylim(self.dlog[self.dlog.columns[-1]].values.min()-0.1,self.dlog[self.dlog.columns[-1]].values.max()+0.1)
            self.ax.legend(fontsize=10, loc='lower center', bbox_to_anchor=(0.5, -0.60))
            self.ax.set_xlabel('Impedance')
            self.ax.set_ylabel(self.parameter)
                
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
            self.canvas.get_tk_widget().configure(background='white',  highlightcolor='white', highlightbackground='white', width = 300, height = 280)
            self.canvas.get_tk_widget().grid(row = 4, rowspan= 11, column=2, sticky = W)
            self.fig.canvas.draw()
#            print(plt.get_fignums())
            
#            self.buildTable()
                        
            button2 = Button(self.root, text = 'Confirm', command = self.confirmationButton, pady=10)
            button2.grid(row = 16, column = 2)
            return
            
    def buildTable(self):
        tv = Treeview(self)
        tv['columns'] = ('concentration','T2T_script','T2T_user','CF_script','CF_user')
        tv.heading("concentration", text='Concentration', anchor='w')
        tv.column("concentration", anchor="w")
        tv.heading('T2T_script', text='T2T Adjust')
        tv.column('T2T_script', anchor='center', width=100)
        tv.heading('T2T_user', text='T2T User')
        tv.column('T2T_user', anchor='center', width=100)
        tv.heading('CF_script', text='CF Adjust')
        tv.column('CF_script', anchor='center', width=100)
        tv.heading('CF_user', text='CF User')
        tv.column('CF_user', anchor='center', width=100)
        
        tv.grid(sticky = (N,S,W,E))
        self.treeview = tv
        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)
                         
    def confirmationButton(self):
        plt.close('all')
        result = messagebox.askyesno(title = 'Confirm Database Adjustment', message='Clicking YES will change the database.  Are you sure?', icon='warning')
        if result == True:
            print('Attempting Database Adjustment...')
#            self.getDB(plateType = self.platevar.get(), parameter = self.tablevar.get())
            if (abs(self.des['CF adjust'].values) >= self.CFThresh).any() == True:
                self.remindMIP()
            else:
                self.updateDB()
                print('Database Adjustment done')
#            self.root.destroy()
            return
        else:
            self.root.destroy()
            print('No adjustment')
            return

    def extractDBInformation(self):
        infoLoc = 'C:\\temp'
        transducerInfoFile = pd.read_csv(infoLoc+'\\TransducerSwapInfo.txt', header=None)
        transducer = transducerInfoFile.iloc[0][0]
        database = transducer.split('_')[0]
        echo = transducerInfoFile.iloc[1][0]
        sqlengine = transducerInfoFile.iloc[2][0]
#        destroot = 'C:\\'+transducer+'\\Calibration_E1419'
        destroot = '\\\\seg\\transducer\\Transducers\\'+transducer+'\\Calibration_E1419'
        folderlist = fnmatch.filter(next(os.walk(destroot))[1], '*-*-*_*-*-*')
        folderlist.sort()
        destination = destroot+'\\'+folderlist[-1]+'\\Calibration'
#        destination = '\\\\seg\\transducer\\Transducers\\'+transducer+'\\Calibration_'+echo+'\\Data'
#        destination = 'C:\\Users\\lchang\\Documents\\Script_Test\\'+transducer+'\\Calibration_'+echo+'\\Data'
        PTfolder = destination+'\\'+self.plateType
        ESfolder = PTfolder+'\\Ejectsweep'
        return database, echo, sqlengine, destination, PTfolder, ESfolder
        
    def getDB (self):
#        self.plateType=self.platevar.get()
#        self.parameter=self.tablevar.get()
        print('Getting database information for << '+self.plateType+' >> for << '+self.parameter+' >> adjustment')
        if self.plateType == 'None':
            print('No Plate Type defined.  No adjustment made.')
            return
        if self.parameter == 'None':
            print('No Parameter defined.  No adjustment made.')
            return
        else:
            database, echo, sqlengine, destination, PTfolder, ESfolder = self.extractDBInformation()
            
#            Get Adjustment Information (ES results)
            os.chdir(ESfolder)
            dbafile = fnmatch.filter(os.listdir(),'*_dBAdjust.csv')[0]
            self.des = pd.read_csv(dbafile)
            
#            Get current database
            engine = sqlalchemy.create_engine(sqlengine)
            self.s = engine.connect()
            
            if self.parameter == 'CF': 
                self.tableName = 'LUT'
                self.paramName = 'Tonex_CF_MHz'
                self.var = 'Y'
            if self.parameter == 'T2T':
                self.tableName = 'LUT2D'
                self.paramName = 'Thresh2XferdB'
                self.var = 'Z'          
            self.DB = database+'.dbo.'+self.tableName              
            ret = 'SELECT *'+' FROM ' + self.DB + " WHERE PlateTypeName = '" + self.plateType + "' AND " + self.tableName + "Name = '" + self.paramName + "'"            
            self.db = pd.read_sql(ret, self.s)
        return
            
    def calcDB (self):
#        self.plateType=self.platevar.get()
#        self.parameter=self.tablevar.get()
        
        database, echo, sqlengine, destination, PTfolder, ESfolder = self.extractDBInformation()
        self.getDB()
        
        os.chdir(PTfolder)
        if self.parameter == 'CF':
            if os.path.isfile(self.plateType+'_CF_logbook.csv'):
                self.dlog = pd.read_csv('./'+self.plateType+'_CF_logbook.csv')
            else:
                self.db.to_csv(self.plateType+'_OriginalCF_backup.csv', index = False)
                self.dlog = self.db.copy()
            self.outappend = '_CF_logbook.csv'
            
        if self.parameter == 'T2T':
            if os.path.isfile(self.plateType+'_T2T_logbook.csv'):
                self.dlog = pd.read_csv('./'+self.plateType+'_T2T_logbook.csv')
            else:
                self.db.to_csv(self.plateType+'_OriginalT2T_backup.csv', index = False)
                self.dlog = self.db.copy()
            self.outappend = '_T2T_logbook.csv'
                    
        
        self.des['conc'] = np.nan 
        for c in range(0,len(self.des)):
            self.des['conc'].iloc[c] = self.des['concentration'].iloc[c].split('__')[0].replace(' ','')

        self.db['conc'] = np.nan        
        if 'DMSO' in self.plateType:
            for ii in range(0,len(self.db)):
                if self.db['X'].iloc[ii] == 1.63:
                    self.db['conc'].iloc[ii] = '100'
                elif self.db['X'].iloc[ii] == 1.67:
                    self.db['conc'].iloc[ii] = '95'
                elif self.db['X'].iloc[ii] == 1.71:
                    self.db['conc'].iloc[ii] = '90'
                elif self.db['X'].iloc[ii] == 1.75:
                    self.db['conc'].iloc[ii] = '85'
                elif self.db['X'].iloc[ii] == 1.78:
                    self.db['conc'].iloc[ii] = '80'
                elif self.db['X'].iloc[ii] == 1.81:
                    self.db['conc'].iloc[ii] = '75'
                elif self.db['X'].iloc[ii] == 1.83:
                    self.db['conc'].iloc[ii] = '70'
        elif 'BP2' in self.plateType:
            for ii in range(0,len(self.db)):
                if self.db['X'].iloc[ii] == 1.48:
                    self.db['conc'].iloc[ii] = '0'
                elif self.db['X'].iloc[ii] > 1.48 and self.db['X'].iloc[ii] < 1.77:
                    self.db['conc'].iloc[ii] = '10'
                elif self.db['X'].iloc[ii] >= 1.77 and self.db['X'].iloc[ii] <= 2.06:
                    self.db['conc'].iloc[ii] = '30'
        elif 'GP2' in self.plateType:
            for ii in range(0,len(self.db)):
                if self.db['X'].iloc[ii] == 1.48:
                    self.db['conc'].iloc[ii] = '20'
#                    0% glycerol:  Set to 20% Glycerol to get adjustments to this concentration
                elif self.db['X'].iloc[ii] > 1.48 and self.db['X'].iloc[ii] < 1.6:
                    self.db['conc'].iloc[ii] = '20'
#                    10% glycerol:  Set to 20% Glycerol to get adjustments to this concentration                
                elif self.db['X'].iloc[ii] >= 1.6 and self.db['X'].iloc[ii] < 1.78:
                    self.db['conc'].iloc[ii] = '20'
                elif self.db['X'].iloc[ii] >= 1.78 and self.db['X'].iloc[ii] < 1.96:
                    self.db['conc'].iloc[ii] = '40'
                elif self.db['X'].iloc[ii] >= 1.96 and self.db['X'].iloc[ii] <= 2.06:
                    self.db['conc'].iloc[ii] = '50'
        elif 'SP2' in self.plateType:
            for ii in range(0,len(self.db)):
                if self.db['X'].iloc[ii] > 1.45 and self.db['X'].iloc[ii] <= 1.49:
                    self.db['conc'].iloc[ii] = '14'  # Use the 14% CMC data for database adjustment
        elif '_AQ_B2' in self.plateType:
            for ii in range(0,len(self.db)):
                if self.parameter == 'T2T':
                    if self.db['Y'].iloc[ii] <= 0.69:
                        self.db['conc'].iloc[ii] = '2.75'
                    elif self.db['Y'].iloc[ii] == 1.00:
                        self.db['conc'].iloc[ii] = '4'
                    elif self.db['Y'].iloc[ii] == 1.48:
                        self.db['conc'].iloc[ii] = '6'
                    elif self.db['Y'].iloc[ii] == 1.67:
                        self.db['conc'].iloc[ii] = '7'
                    elif self.db['Y'].iloc[ii] == 1.85:
                        self.db['conc'].iloc[ii] = '8'
                    elif self.db['Y'].iloc[ii] == 2.05:
                        self.db['conc'].iloc[ii] = '9'
                    elif self.db['Y'].iloc[ii] == 2.25:
                        self.db['conc'].iloc[ii] = '10'
                    elif self.db['Y'].iloc[ii] >= 2.68:
                        self.db['conc'].iloc[ii] = '12'
                else:
                    if self.db['X'].iloc[ii] > 1.45 and self.db['X'].iloc[ii] <= 1.49:
                        self.db['conc'].iloc[ii] = '8'  # Use the 8uL data for database adjustment
        elif 'CP' in self.plateType:
            if self.parameter == 'CF':
                self.db['conc'] = 'AQ'
            else:
                for ii in range(0,len(self.db)):
                    if self.db['X'].iloc[ii] >= 1.4 and self.db['X'].iloc[ii] <= 1.58:
                        self.db['conc'].iloc[ii] = 'AQ'
                    elif self.db['X'].iloc[ii] > 1.58 and self.db['X'].iloc[ii] <= 1.94:
                        self.db['conc'].iloc[ii] = 'PEG'
                    elif self.db['X'].iloc[ii] > 2.02 and self.db['X'].iloc[ii] <= 2.544:
                        self.db['conc'].iloc[ii] = 'HEPES'
            
#        self.dlog['conc'] = self.db['conc']
        if not 'conc' in self.dlog:
            self.dlog.insert(0, 'conc', self.db['conc'])
        
        for i in range(0,len(self.db['X'])):
            if self.parameter == 'CF':
#                self.des['adjusted'+self.parameter] = np.nan
                if self.db['Description'].iloc[i] == '1':
                    y = self.db[self.var].loc[i]
                    if self.db['conc'].iloc[i] in np.array(self.des['conc']):
                        x = self.des[self.des['conc']==self.db['conc'].iloc[i]].index.tolist()[0]
                        CF = self.des['CF adjust'].loc[x]
                        self.db[self.var].loc[i] = CF+y
#                        self.des['adjusted'+self.parameter].loc[x]= CF+y
#                    else:
#                        self.db[self.var].iloc[i] = y
                if self.db['Description'].iloc[i] == '3':
                    x = self.db[self.db['X']==self.db['X'].iloc[i]].index.tolist()[0]
                    self.db[self.var].iloc[i] = .9*self.db[self.var].loc[x]
                
            if self.parameter == 'T2T':
                if self.db['conc'].iloc[i] in np.array(self.des['conc']):
                    x = self.des[self.des['conc']==self.db['conc'].iloc[i]].index.tolist()[0]
                    z = self.db[self.var].loc[i]
                    T2T = self.des['T2T adjust'].loc[x]
                    self.db[self.var].loc[i] = T2T+z

        if '_AQ_B2' in self.plateType and self.parameter == 'T2T':
            for i in range(0, len(self.db['X'])):
                if self.db['conc'].loc[i] == '2.75':
                    x = self.db.loc[self.db['conc']=='4'].index.tolist()[0]
                    a = self.db['Z'].loc[x] + 0.15
                    print(self.db['Z'].loc[x])
                    print(x)
                    print(a)
                    self.db['Z'].loc[i] = a
                else:
                    if not self.db['conc'].loc[i] in np.array(self.des['conc']):
                        self.db['Z'].loc[i] = self.db['Z'].loc[i-1]+(((self.db['Z'].loc[i+1]-self.db['Z'].loc[i-1])/(self.db['Y'].loc[i+1]-self.db['Y'].loc[i-1]))*(self.db['Y'].loc[i]-self.db['Y'].loc[i-1]))
        return        

    def updateDB(self):
        self.plateType=self.platevar.get()
        self.parameter=self.tablevar.get()
        self.calcDB()
        database, echo, sqlengine, destination, PTfolder, ESfolder = self.extractDBInformation()
        
        for i in range(0,len(self.db['X'])):
            if self.parameter == 'CF':
                exe = 'UPDATE '+ self.DB + ' SET Y = ' + str(self.db[self.var].iloc[i]) + " WHERE LUTNAME = '" + self.db['LUTName'].iloc[i] + "' AND Description = '"+self.db['Description'].iloc[i]+"' AND X = " + str(self.db['X'].iloc[i]) + " AND PlateTypeName = '" + self.db['PlateTypeName'].iloc[i]+"'"
                self.s.execute(exe)
                    
            if self.parameter == 'T2T':
                exe = 'UPDATE '+ self.DB + ' SET Z = ' + str(self.db[self.var].iloc[i]) + " WHERE LUT2DNAME = '" + self.db['LUT2DName'].iloc[i] +"' AND X = " + str(self.db['X'].iloc[i]) + " AND Y = " + str(self.db['Y'].iloc[i]) + " AND PlateTypeName = '" + self.db['PlateTypeName'].iloc[i]+"'"
#                print(exe)
                self.s.execute(exe)
                
        #db.to_sql(name=DB, con=engine, if_exists='replace', flavor='MySQL', index=False)      
        os.chdir(PTfolder)
        dateadjust = str(datetime.datetime.now()).split('.')[0].replace('-','').replace(':','').replace(' ','_')
        headers = list(self.dlog.columns)
        headers.append(dateadjust)
        self.dlog = pd.concat([self.dlog, self.db[self.var]],axis=1,ignore_index=True)
        self.dlog.columns = headers
        self.dlog.to_csv(self.plateType+self.outappend, index = False)
        self.remindRestart()
        return     
 
    def remindRestart(self):
    #   Reminder to users to restart server
#        self.root = tkinter.Tk()
        message = ['Changes were made to database '+self.DB, '','Please remember to RESTART the server']
        messagebox.showinfo('Reminder', '\n'.join(message))
        self.root.withdraw() 
        self.root.destroy()
        return

    def remindMIP(self):
        #   Reminder to users to redo MIP in EPC
#        self.root = tkinter.Tk()
#        self.root.withdraw() 
        message = ['Changes to Center Frequency is more than 0.3 MHz', '','YES:  Adjustment will be made.  Please re-do the Mound Imaging Workstep in EPC Protocol for this platetype', '', 'NO:  Widget will quit.  No changes were made to the database']
        result = messagebox.askyesno(title = 'WARNING', message = '\n'.join(message))
        
        if result == True:
            self.updateDB()
            print('Database Adjustment done')
            return
        else:
            self.root.withdraw()
            self.root.destroy()
            print('No adjustment')
            return

    def quitButtonClick(self):
        self.root.destroy()
        return

def main():
    DBAdjust()

if __name__ == "__main__":
    main()

#if __name__ == "__main__":
#   main(sys.argv[1:])
   