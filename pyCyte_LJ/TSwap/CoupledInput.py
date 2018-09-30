# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 22:49:08 2017

@author: avandenbroucke
"""

# -*- coding: ISO-8859-1 -*-
import sys

if not('.' in sys.path): sys.path.append('.')
#import midi24txt 


import pandas
import numpy as np
import scipy.stats
import matplotlib.pyplot as plt

import os
# thinking in tkinter http://www.ferg.org/thinking_in_tkinter/all_programs.html

class CoupledInput():
    def __init__(self,filename=None):
        self.db_a = -21      # Attenuation before RF Module [dB]
        self.db_rf = 33.5    # Amplification of RF Module [dB]
        self.verbose = False
        self.SwitchPointMin = 1.0
        self.SwitchPointMax = 3.0
        self.GainMin = 50.5
        self.GainMax = 55.0
        plt.rcParams['legend.numpoints'] = 1
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
        data_raw = pandas.read_csv(Amp_filename, delimiter=',', header=14)
        data_raw = data_raw.drop(data_raw.columns[:2], axis=1)
        self.hasfile = True 
        return data_raw
        
    def processData(self):
        if not self.hasfile:
            return
        self.Cf = sorted(set(self.raw_data['CF(MHz)']))
        
        data = {}
        
        for f in self.Cf:
            data[f] = self.raw_data.loc[self.raw_data['CF(MHz)'] == f]
   #         data[f].loc[:, 'Amp(V)'] = data[f].loc[:, 'Amp(V)'] #*10**(self.db_a/20)
   #         data[f].loc[:, 'Meas. Vpp'] = data[f].loc[:, 'Meas. Vpp'] #*10**(self.db_rf/20)
            data[f].sort_values('Amp(V)', axis=0,
                                ascending=True, inplace=True)
    
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
	
    def passFail(self, CF=12.0):
        self.LinearGain = 20*np.log10(self.results['G1'][self.results['CF'] == 12.0 ].values[0])
        self.Switchpoint = self.results['Sw'][self.results['CF'] == 12.0].values[0]
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
        self.passFail()
        if self.Pass == True:
            props = dict(boxstyle='round', facecolor='green', alpha=0.5)
            textstring = 'PASS'
        else:
            props = dict(boxstyle='round', facecolor='red', alpha=0.5)
            textstring = 'FAIL'
        ax1.text(0.05, 0.5, textstring, transform=ax1.transAxes, fontsize=18, verticalalignment='top', bbox=props)    
        plt.tight_layout()
        plt.subplots_adjust(top=0.85)
        if (self.outputfile != '' ):
            plt.savefig(self.outputfile)
        return        
 