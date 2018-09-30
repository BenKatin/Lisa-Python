# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 00:32:46 2017

@author: avandenbroucke
"""

##---(Tue Mar  7 22:59:22 2017)---
import os 
#os.listdir()
import h5py
import pandas
import numpy as np
import matplotlib.pyplot as plt
#from mmSpy import MedManSpy as ms


class classificationAna():
    gg_bbvpp = np.array([ 2.4918,  2.4278,  2.4384,  2.3434,  2.2418,  2.3278,  2.3027,
        2.223 ,  2.3199,  2.4322,  2.4107,  2.4309,  2.4323,  2.3886,
        2.4107,  2.3152,  2.2105,  2.2901,  2.2776,  2.1901,  2.2481,
        2.3479,  2.3231,  2.3496])        
    sea_bbvpp = np.array([ 2.29395,  2.2473 ,  2.2167 ,  2.17915,  2.1488 ,  2.1224 ,
        2.08635,  2.06745,  2.0589 ,  2.04795,  2.04715,  2.0682 ,
        2.0432 ,  2.0386 ,  2.0433 ,  2.0457 ,  2.04715,  2.0675 ,
        2.0932 ,  2.1122 ,  2.12625,  2.1557 ,  2.17995,  2.21605])
    sea_bbvpp =  np.array([ 2.08634307,  2.13452019,  2.198439  ,  2.16365276,  2.19831375,
        2.20299926,  2.17620953,  2.18545943,  2.17049162,  2.16741642,
        2.16434992,  2.17620953,  2.08282009,  2.12463047,  2.16375915,
        2.18289649,  2.18170573,  2.17353673,  2.16399745,  2.1899636 ,
        2.15824289,  2.12044095,  2.12826581,  2.14613163])
    sea_bbvpp = np.array([1.01129, 1.0089, 1.012487, 1.01262, 1.011213, 1.00598, 
        0.99859, 0.99469, 0.989789, 0.98283, 0.98585, 
        0.99722, 0.99445, 0.98051,  0.984, 0.98977, 
        0.99311, 0.99955, 1.00554, 1.0073, 1.00823, 
        1.01219,  1.00643, 1.00747])    
    gg_tofdelta = np.array([ 0.59863636,  0.59860606,  0.60184848,  0.59936364,  0.5930303 ,
        0.58581818,  0.58686364,  0.59513636,  0.60231818,  0.60115152,
        0.60318182,  0.60298485,  0.6029697 ,  0.60416667,  0.60233333,
        0.60456061,  0.59768182,  0.59022727,  0.58780303,  0.59483333,
        0.60119697,  0.60315152,  0.59963636,  0.59786364])
    sea_tofdelta = np.array([ 0.6098,  0.6242,  0.6293,  0.6316,  0.6331,  0.6345,  0.6359,
        0.6366,  0.6379,  0.638 ,  0.637 ,  0.637 ,  0.6342,  0.6364,
        0.6368,  0.637 ,  0.636 ,  0.6348,  0.6337,  0.6322,  0.6308,
        0.6282,  0.6229,  0.6104])
    
    
    def __init__(self, filename=None):
        if (filename):
            self.hfile = h5py.File(filename)
            A =  self.hfile['/Classification/PlateClassification/ClassificationAnalysis']
            colnames = [ dt[0] for dt in A.dtype.descr if dt[0] !='']
            data = []
            for row in A[tuple(colnames)]:
                myRow = [f.decode('utf-8') if isinstance(f, bytes) else round(f, 3) if isinstance(f, float) else f for f in row.tolist()]
                data.append(myRow)
 
            Adf = pandas.DataFrame(data)
            Adf.columns = colnames
            self.ClasMeas = Adf 
            self.ClasMeas['BottomThick'] = self.ClasMeas['TBTOF'] - self.ClasMeas['BBTOF']
        self.ncols = 12    
        self.bbvpp_kernels = {}
        self.bbvpp_kernels['gg_bbvpp'] = self.gg_bbvpp
        self.bbvpp_kernels['sea_bbvpp'] = self.sea_bbvpp
        self.tof_kernels = {}
        self.tof_kernels['gg_tofdelta'] = self.gg_tofdelta
        self.tof_kernels['sea_tofdelta'] = self.sea_tofdelta
        self.meas_rows = ['RowH','RowI']
        self.tof_corr = {}
        
        return 

    def CalcCorr(self,field='BBVpp'):
        Ms = self.ClasMeas[[field,'Row','Col']].pivot(columns='Col',index='Row')
        self.BBVpp = {}
        for i,k in enumerate(self.meas_rows):
            self.BBVpp[k] = Ms.iloc[i].values
        self.BBVpp['Mean'] = Ms.mean().values
        cortable = {}
        for k in ( self.meas_rows + ['Mean']):
            corcoef = []
            for l in self.bbvpp_kernels.keys():
                corcoef.append( np.corrcoef(self.BBVpp[k][:self.ncols], self.bbvpp_kernels[l][:self.ncols])[0,1])
            cortable[k] = corcoef    
        tab = pandas.DataFrame(cortable).T   
#        print(tab)
        tab.columns = self.bbvpp_kernels.keys()
        MsTOF = self.ClasMeas[['BottomThick','Row','Col']].pivot(columns='Col',index='Row')
        self.TOF = {}
        for i,k in enumerate(self.meas_rows):
            self.TOF[k] = MsTOF.iloc[i].values
        self.TOF['Mean'] = MsTOF.mean().values
        cortable = {}
        for k in ( self.meas_rows + ['Mean']):
            corcoef = []
            for l in self.tof_kernels.keys():
                corcoef.append( np.corrcoef(self.TOF[k][:self.ncols],  self.tof_kernels[l][:self.ncols] )[0,1])
            cortable[k] = corcoef    
        tabTOF = pandas.DataFrame(cortable).T    
        tabTOF.columns = self.tof_kernels.keys()
        joined = tab.join(tabTOF)
        allkeys= list(self.tof_kernels.keys()) + list(self.bbvpp_kernels.keys())
        nkeys = len(allkeys)//2
        for k in range(0,nkeys):
            joined[allkeys[k].split('_')[0]] = (joined[allkeys[k]] + joined[allkeys[k+2]])/2.
        return joined
        
    def plotCorr(self, field='BBVpp'):
        data = self.CalcCorr(field)
        
        fig, ax = plt.subplots(nrows=1,ncols=2,figsize=(15,4))
        for j, kind in enumerate(['TB','BB']):
            if kind == 'BB' :
                kernels = self.bbvpp_kernels
                vals  = self.BBVpp
                donorm = True
            else:
                kernels = self.tof_kernels
                vals = self.TOF
                donorm = False
            for i,k in enumerate(self.meas_rows):
                ax[j].plot(self.norm(vals[k],donorm),linestyle='-',marker='o',label=k)
            ax[j].plot(self.norm(vals['Mean'],donorm),label='Mean')   
            ax[j].set_title(kind)
            for l in sorted(kernels.keys()):
                val = str(data[l]['Mean'].round(2))
                lab = l.split('_')[0] + ': ' + val
                ax[j].plot(self.norm(kernels[l][:self.ncols],donorm),label=lab)
            box = ax[j].get_position()
            ax[j].set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis
            ax[j].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        fig.suptitle(self.hfile.filename)    
        return
        
    def norm(self, array, donorm=True):
        if (donorm):
            return array/np.mean(array)
        else:
            return array
        
    def plotWell(self,well='H1',ax=None):
       wav = self.getWav(well)
       EchoAlgoSettings = self.hfile['Classification/EchoAlgorithmSettings/EchoAlgorithmSettings']
       SurveyAna = self.hfile['/Classification/PlateClassification/ClassificationAnalysis']
       colString = self.getColumnNames(SurveyAna)
       SurveyAnadata = SurveyAna[colString]
       feats = [ r for r in SurveyAnadata if r['Well'].decode('utf-8') == well]
       self.plotWav(wav,feats[0],float(EchoAlgoSettings['StartTofUs'])+0.5,ax=ax)
       return 
   
    def getWav(self,well='A1'):
        wav = self.hfile['/Classification/PlateClassification/' + well]
        wavL = [ float(r) for r in wav[0] ]
        return wavL
    
    def plotWav(self,wavL, SurveyFeatures, StartTOF=0.0, lengthus=6,ax=None):
        x = np.arange(0,(len(wavL)-1)/500, step=1/500)
        x += StartTOF
        maxindex = 6*500;
        if not ax:
            ax = plt.subplot(111)
        ax.plot(x[:maxindex],wavL[:maxindex])
        ax.set_xlabel('Time (us)')
        ax.set_ylabel('Vpp')
        ax.set_xlim(StartTOF,StartTOF+lengthus)
        ax.axvline( SurveyFeatures["TBTOF"],color='hotpink',linewidth=2);
        ax.axvline( SurveyFeatures["BBTOF"],color='darkgray',linewidth=2);
        ax.axvline( SurveyFeatures["SRTOF"],color='hotpink',linewidth=2);
        return 
        
    def getColumnNames(self,dataset):
        return tuple([dt[0] for dt in dataset.dtype.descr if dt[0]!='']) 
    
    def setFEpar(self):
        self.EchoAlgoSettings = self.hfile['Classification/EchoAlgorithmSettings/EchoAlgorithmSettings']
        RefWav = self.hfile['Classification/EchoAlgorithmSettings/ReferenceWav']
        RefWavL = [ float(r) for r in RefWav ]
        self.FE = ms.FeatureExtraction() 
        self.FE.SetTransducerFreqMHz(10)
        self.FE.SetKernel(RefWavL)
        self.FE.SetBottomThicknessRange(int(self.EchoAlgoSettings['MinBotThkToFNs'][0]),int(self.EchoAlgoSettings['MaxBotThkToF_Ns'][0]))
        self.FE.SetHilbertMinBBMagnitude(float(self.EchoAlgoSettings['HilbertMinBBPeakMag'][0]))
        self.FE.SetHilbertMinPeakMag(float(self.EchoAlgoSettings['HilbertMinPeakMag'][0]))
        self.FE.SetMaxTB2BBRatio(float(self.EchoAlgoSettings['MaxTB2BBRatio'][0]))
        self.FE.SetMaxTB2SRRatio(float(self.EchoAlgoSettings['MaxTB2SRRatio'][0]))
        self.FE.SetMinTB2BBRatio(float(self.EchoAlgoSettings['MinTB2BBRatio'][0]))
        self.FE.SetSRVppThreshold(float(self.EchoAlgoSettings['SRThreshold'][0]))   
        return
        
    def loadTofCorr(self, xlfile, plate='sea', SurveyTOF=0.92):
        FL  = self.hfile.attrs['TransducerFocalLengthUs']
        tofc = pandas.read_excel(xlfile)
        TOFY = tofc['Y'].values
        TOFX = tofc['X'].values
        label = 'BBVppCorr' + plate
        self.ClasMeas[label] = self.ClasMeas['BBVpp'] * np.interp( SurveyTOF, TOFX, TOFY)/ np.interp( (self.ClasMeas['BBTOF'] / FL ) , TOFX, TOFY )
        return
    
    def plotRow(self, row='H'):
        fig,ax = plt.subplots(figsize=(12,8),nrows = 3, ncols = 4)
        irow = 0
        icol = 0
        for i in range(1,13):
            self.plotWell(well=row+str(i),ax=ax[irow][icol])
            icol += 1
            if icol == 4:
                irow += 1
                icol = 0
        return        
        
    def readKernels(self, kernels=['384PPG','384PPL']):
        groupname = '/Classification/PlateClassificationSettings/AnalysisSettings/ClassificationKernels/'
        candidates = self.hfile[groupname]
        for k in kernels:
            if 'PPG' in k:
                plate = 'gg'
            else:
                plate = 'sea'
            for t in ['BBVpp','TBBBToF']:
                cand = k + '_' + t
                if cand in candidates:
                    k1 = self.hfile[groupname + cand ]
                    if 'Vpp' in t :                    
                        var = plate + '_' + 'bbvpp'
                        self.bbvpp_kernels[var] = np.asarray(k1) 
                    else:
                        var = plate + '_' + 'tofdelta'
                        self.tof_kernels[var] = np.asarray(k1)
                else:
                   print('No kernel candidate ', cand, ' found in file. Candidates are:')
                   for g in candidates:
                       print( g )
        return            
 
#        
#Ms
#Ms.iloc(0)
#Ms.iloc[0]
#Ms.iloc[0].values
#
#Adf['BBVpp']
#Adf.pivot(columns=['Row'],values='BBVpp')
#Adf.pivot(columns=['Row'],values=['BBVpp'])
#Adf
#Adf.dtype
#Adf.dtypes
#Adf.pivot(values=['BBVpp'])
#Adf.pivot(values=['BBVpp'], columns=['Row'])
#Adf['BBVpp','Row'].pivot(values=['BBVpp'], columns=['Row'])
#Adf['BBVpp','Row']
#Adf
#Adf[['BBVpp','Row']]
#Adf[['BBVpp','Row']].pivot(columns='Row')
#Adf[['BBVpp','Row','Col']].pivot(columns='Row',index='Col')
#Adf[['BBVpp','Row','Col']].pivot(columns='Col',index='Row')
#Adf[['BBVpp','Row','Col']].pivot(columns='Col',index='Row').Mean
#Adf[['BBVpp','Row','Col']].pivot(columns='Col',index='Row').Mean()
#Adf[['BBVpp','Row','Col']].pivot(columns='Col',index='Row').mean
#Adf[['BBVpp','Row','Col']].pivot(columns='Col',index='Row').mean()
#Adf[['BBVpp','Row','Col']].pivot(columns='Col',index='Row').mean().values
#meas = Adf[['BBVpp','Row','Col']].pivot(columns='Col',index='Row').mean().values
#
#
#np.corrcoef(mean,gg_bbvpp[:12])
#np.corrcoef(meas,gg_bbvpp[:12])
#plt.plot(meas);plt.ploat(gg_bbvpp[:12])
#import matplotlib.pyplot as plt
#plt.plot(meas);plt.ploat(gg_bbvpp[:12])
#plt.plot(meas);plt.plot(gg_bbvpp[:12])
#plt.plot(meas);plt.plot(sea_bbvpp[:12])
#Ms = Adf[['BBVpp','Row','Col']].pivot(columns='Col',index='Row')
#Ms
#Ms.iloc(0)
#Ms.iloc[0]
#Ms.iloc[0].values
#plt.plot(Ms.iloc[0].values);plt.plot(Ms.iloc[1].values)
#sea = sea_bbvpp[:12] 
#np.corrcoef(sea,Ms.iloc[0].values)
#np.corrcoef(sea,Ms.iloc[1].values)
#h1 =  f['/Classification/PlateClassification/H1']
#h1
#pandas.DataFrame(h1)
#h1 =  f['/Classification/PlateClassification/H1'][0]
#h1
#plt.plot(h1)
#data = {}
#for i in range(1,12):
#    well = 'H' + str(i)
#    w = f['Classification/PlateClassification/' + well][0]
#    data[well] = w   
#    
#plt.plot(data['H1'])
#plt.plot(data['H1']);plt.plot(data['H2'])
#plt.plot(data['H1'][:1500]);plt.plot(data['H2'][:1500])
#plt.plot(data['H1'][:1500]);plt.plot(data['H2'][:1500]);plt.plot(data['H3'][:1500]);plt.plot(data['H4'][:1500])
#0.2/35
#plt.plot(data['H4'][:1500])
#plt.plot(data['H4'][:1500]); plt.plot(data['H5'][:1500]);
#plt.plot(data['H2'][:1500]); plt.plot(data['H3'][:1500]);