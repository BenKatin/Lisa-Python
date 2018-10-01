# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 22:49:08 2017

Version of 10/30/2017
@author: avandenbroucke
"""

# -*- coding: ISO-8859-1 -*-
import sys

if not('.' in sys.path): sys.path.append('.')
#import midi24txt 

import tkinter 
#from tkFileDialog import *
from tkinter import filedialog
import pandas
import numpy as np
import scipy.stats
import matplotlib.pyplot as plt
import os
# thinking in tkinter http://www.ferg.org/thinking_in_tkinter/all_programs.html

class TheGui:
    def __init__(self, parent):
        #------- frmSetup ----------#
        self.frmSetup = tkinter.Frame(parent, bd=5)
        self.frmSetup.pack()
        
        
        self.varRadio = tkinter.IntVar()
        
        self.dbvals=[30.5,33.5]
        self.r1 = tkinter.Radiobutton(self.frmSetup, text="RF Module Attenuation: 30.5dB",
            variable=self.varRadio, value=0, command=self.selRadio)
        self.r1.pack(anchor='w')

        self.r2 = tkinter.Radiobutton(self.frmSetup, text="RF Module Attenuation: 33.5dB", 
            variable=self.varRadio, value=1, command=self.selRadio)
        self.r2.pack(anchor='w')
        #------- frmSetup ----------#

        sep = tkinter.Frame(parent, width=1, bd=5, bg='black')
        sep.pack(fill='x', expand=1)
         
        #------- frmIn ----------#
        # http://effbot.org/tkinterbook/tkinter-widget-styling.htm
        self.frmIn = tkinter.Frame(parent, bd=5)         
        self.frmIn.pack()

        self.lblIn = tkinter.Label(self.frmIn, text='File name', width=20)
        self.lblIn.pack(side='left') 

        self.inFileName = tkinter.StringVar() # http://effbot.org/tkinterbook/entry.htm
        self.entIn = tkinter.Entry(self.frmIn, width=20, textvariable=self.inFileName)
        self.entIn.pack(side='left')
        

        self.btnIn = tkinter.Button(self.frmIn, text='Browse', command=self.btnInBrowseClick)
        self.btnIn.pack(side='left') 
        #------- frmIn ----------#
        
        
        
        
        sep = tkinter.Frame(parent, width=1, bd=5, bg='black')
        sep.pack(fill='x', expand=1)
        
        #------- frmButtons ----------#
        self.frmOut = tkinter.Frame(parent, bd=5)
        self.frmOut.pack()
        
        self.btnGo = tkinter.Button(self.frmOut, 
            text='Calculate', command=self.btnGoClick)
        self.btnGo.pack() 
  
        self.btnQuit = tkinter.Button(self.frmOut,text='Quit',command=self.btnQuitClick)
        self.btnQuit.pack()
        
        sep = tkinter.Frame(parent, width=1, bd=5, bg='black')
        sep.pack(fill='x', expand=1)
         
        self.frmResult = tkinter.Frame(parent, bd=5)
        self.frmResult.pack()
        
        self.status = tkinter.Label(self.frmResult, anchor="w",fg="white",bg="gray", text='Status: Unknown')
        self.status.pack() # label.grid(column=0,row=1,columnspan=2,sticky='EW')
        
        
    #------- handle commands ----------#
    def selRadio(self):
     #   self.lblIn.config(text = self.inChoices[self.varRadio.get()] 
     #       + ' Input File Path')
     #   self.lblOut.config(text = self.inChoices[(self.varRadio.get()+1)%2] 
     #       + ' Output File Path')
        print(str(self.varRadio.get()))
   
     
    def btnInBrowseClick(self):             
        rFilepath = filedialog.askopenfilename(defaultextension='*', 
            initialdir='.', initialfile='', parent=self.frmIn, title='select a file') 
        self.inFileName.set(rFilepath)
        print(' Filename : ' ,  self.entIn.get())
    
   
    
    def btnGoClick(self):  
        inputTextFileName = str(self.inFileName.get())
        print('inputfile: ', inputTextFileName)
        ci = CoupledInput(filename=inputTextFileName)
        ci.db_rf = self.dbvals[self.varRadio.get()]
        ci.db_a = -21
        ci.processData()
        print(ci.results)
        ci.passFail()
        print(' Gain: ', ci.gain_pass, ' SW: ', ci.switchpoint_pass)
        stat = 'Gain: ' + '{:.1f}'.format(ci.LinearGain) + ' SwitchPoint: ' + '{:.2f}'.format(ci.Switchpoint) + ' V'
        if (ci.Pass):
            txt = 'PASS:: ' + stat
            self.status.config(text=txt)
            self.status.config(bg='green')
        else:
            txt = 'FAIL:: ' + stat
            self.status.config(text=txt)
            self.status.config(bg='red')
        ci.plotResult()
            
    def btnQuitClick(self):
        root.destroy()
        
class CoupledInput():
    def __init__(self,filename=None):
        self.db_a = -21      # Attenuation before RF Module [dB]
        self.db_rf = 33.5    # Amplification of RF Module [dB]
        self.verbose = False
        self.SwitchPointMin = 1.0
        self.SwitchPointMax = 3.0
        self.GainMin = 50.5
        self.GainMax = 55.0
        self.outputfile = ''
        if (filename):
           self.raw_data = self.readfile(filename)
           self.path = os.path.dirname(filename)
           basename = os.path.basename(filename)
           outfilename = os.path.splitext(basename)[0] + '.png'
           self.outputfile = os.path.join(self.path,outfilename)
        return   
    # %% Import, parse, and correct RFHealthCheck file
    def readfile(self,Amp_filename):
        data_raw = pandas.read_csv(Amp_filename, delimiter=',', header=17, skip_blank_lines=False)
        data_raw = data_raw.drop(data_raw.columns[:2], axis=1)
        print(data_raw.dropna())
        self.hasfile = True 
        return data_raw.dropna()
        
    def processData(self):
        if not self.hasfile:
            return
        self.Cf = sorted(set(self.raw_data['CF(MHz)']))
        print(' CF: ' , self.Cf)
        data = {}
        
        for f in self.Cf:
            data[f] = self.raw_data.loc[self.raw_data['CF(MHz)'] == f]
   #         data[f].loc[:, 'Amp(V)'] = data[f].loc[:, 'Amp(V)'] #*10**(self.db_a/20)
   #         data[f].loc[:, 'Meas. Vpp'] = data[f].loc[:, 'Meas. Vpp'] #*10**(self.db_rf/20)
   #         data[f].sort('Amp(V)', axis=0,
   #                             ascending=True, inplace=True)
    
    # %% Fit double line piecewise function to each dataset
    
        sp = {}
        fit_result = {}
        fit_result['SSE'] = []
        for f in self.Cf:
            vin = sorted(set(data[f]['Amp(V)']))
            vout = []
            for v in vin:
                vout.append(data[f]['Meas. Vpp'].loc[data[f]['Amp(V)'] == v].mean())
            sp[f] = self.FindSplit(vin, vout, targetR2val=0.9992)
    
    # %% Determine gains and switchpoints as functions of frequency
    
        allresults = []
        for f in self.Cf:
            result = {}
            result['CF'] = f
            result['G1'], result['G2'], result['Sw'] = self.findSlopesAndTurnOver(vin, vout, split=sp[f])
            allresults.append(result)
        
        self.results = pandas.DataFrame(allresults)    
        return
            
   #         v0 = data[f]['Amp(V)'][data[f]['Meas. Vpp'] <= sp[f]]
   #         v1 = data[f]['Amp(V)'][data[f]['Meas. Vpp'] > sp[f]]
   #         vout0 = data[f]['Meas. Vpp'][data[f]['Meas. Vpp'] <= sp[f]]
   #         vout1 = data[f]['Meas. Vpp'][data[f]['Meas. Vpp'] > sp[f]]
        
   #         fit_result['SSE'].append(sum((opt_fit[0]*v0+opt_fit[1] - vout0)**2) +
    #                                 sum((opt_fit[2]*v1+opt_fit[3] - vout1)**2))    
    
            
            
    def FindSplit(self, xval, yval, targetR2val = 0.999):
        for i in range(len(xval)-3, 3, -1):
            slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(xval[0:i], yval[0:i])
            if (self.verbose):
                print(' npoints: ', i, ' r_value : ', r_value, ' slope: ', slope, ' intercept: ', intercept, ' x: ', xval[i] )
            if  ( r_value > targetR2val):
                return i-1
        return -1
    
    def findSlopesAndTurnOver(self, xval, yval, split=6):
        gaincor = np.power(10, (-self.db_a+self.db_rf)/20)
        slope_h, intercept_h, r_value_h, p_value_h, std_err_h = scipy.stats.linregress(xval[0:split], yval[0:split])
        slope_l, intercept_l, r_value_l, p_value_l, std_err_l = scipy.stats.linregress(xval[split:], yval[split:])
        switchpoint =  ( intercept_l - intercept_h) / ( slope_h - slope_l)
        return slope_h*gaincor, slope_l*gaincor, switchpoint
	
    def passFail(self, CF=10.0):
        self.LinearGain = 20*np.log10(self.results['G1'][self.results['CF'] == 10.0 ].values[0])
        self.Switchpoint = self.results['Sw'][self.results['CF'] == 10.0].values[0]
        if ( self.Switchpoint > self.SwitchPointMin ) and ( self.Switchpoint < self.SwitchPointMax ):
            self.switchpoint_pass = True
        else:
            self.switchpoint_pass = False
        if ( self.LinearGain > self.GainMin) and ( self.LinearGain < self.GainMax ):
            self.gain_pass = True
        else:
            self.gain_pass = False
        if ( self.gain_pass ) and ( self.switchpoint_pass):
            self.Pass = True
        else:
            self.Pass = False
        return    

    # %% Plot gains and switchpoint as function of frequency
    def plotResult(self, ax1 = None):
        Cf = np.asarray(self.results['CF'].values)
        G1 = np.asarray(self.results['G1'].values)
        G2 = np.asarray(self.results['G2'].values)
        SW = np.asarray(self.results['Sw'].values)
        if not ax1:
            fig, ax1 = plt.subplots()
        l1 = ax1.plot(Cf, 20*np.log10(G1), 'bd', label='Unsatgain')
        l2 = ax1.plot(Cf, 20*np.log10(G2), 'rs', label='Satslope')
        ax1.set_xticks(Cf)
        ax1.set_xlim(Cf.min()-0.5,Cf.max()+0.5)
        ax1.set_yticks(np.arange(np.floor(ax1.get_yticks()[0]),
                                 np.ceil(ax1.get_yticks()[-1])+1))
        ax2 = ax1.twinx()
        l3 = ax2.plot(Cf, SW, 'g^', label='Switchpoint')
        ax2.set_yticks(np.linspace(ax2.get_yticks()[0], ax2.get_yticks()[-1],
                                   len(ax1.get_yticks())))
        ax2.grid(None)
        ax1.set_xlabel('Frequency (MHz)')
        ax1.set_ylabel('Slope (dB)')
        ax2.set_ylabel('Tabor Switchpoint (V)')
        lns = l1 + l2 + l3
        lab = [l.get_label() for l in lns]
        plt.figlegend(handles=lns, labels=lab, loc='upper center',
                      frameon=True, ncol=3)
        plt.tight_layout()
        plt.subplots_adjust(top=0.85)
        if (self.outputfile != '' ):
            plt.savefig(self.outputfile)
        return        
  
root = tkinter.Tk()
root.title("Analyse Amplifier Eligibility")
#http://infohost.nmt.edu/tcc/help/pubs/tkinter/std-attrs.html#geometry
#http://infohost.nmt.edu/tcc/help/pubs/tkinter/toplevel.html
root.geometry("350x200+10+10")
gui = TheGui(root)
root.mainloop()