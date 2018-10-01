# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 22:06:25 2016

@author: avandenbroucke


Example:
alld = []
for file in finemiph5dmso_pp[1]:
    print(' ------- ', file, ' ------- ')
    ff = FineMIP.FineMipAna(file)
    ff.maxdB=10.0
    ff.setTargetFreqRange(8.0,11)
    ac = ff.plotAllWells('TPF-8.0-11.0_10.0dBMax-T0-XX.pdf', False)
    print(' Mean :: ',  ac[2].mean(), ' Std :: ',ac[2].std())
    alld.append([ file.split('\\')[-2], ac[2].mean(), ac[2].std()])
    ff.closeFile()
    
    
ff = FineMIP.FineMipAna(finemiph5dmso_pp[0])
midat = ff.getMIPframe('A10-A10'); sel= ff.getValidMIP(midat);a = ff.plotNS(np.log(sel['NullSpace']),sel['PowerdB'],wellcombo)    
    

"""

from ..SigPro.MI_ana import MI_ana
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas
from PlateTransfer import PlateTransfer
from TransferWaveform import TransferWaveform
from PlateSurvey import PlateSurvey
from scipy import stats

class FineMipAna(MI_ana):
    
     def __init__(self, filename=None):
        MI_ana.__init__(self,filename)
        if filename:
            self.path = os.path.dirname(filename)  
            if not self.path :
                self.path = './'
            self.pt = PlateTransfer(self.h5file,'')
            self.transfergroups = self.pt.getAllWellGroups()
            self.miwav = TransferWaveform(self.h5file,'')
            if ( self.pt.firstWellGroupWithPrintData ):
                self.printdat, self.nonConvergedCombos = self.getPrintDat()
            else:
                self.printdat = None
            self.psurvey = PlateSurvey(self.h5file)
            self.psurvey.setDataset('/PlateSurvey/SurveyAnalysis')
            self.surveydat = self.getSurveyDat()
        self.MASK = 0xA0
        self.minNullSpaceMHz = 0
        self.maxNullSpaceMHz = 10
        self.maxdB = 10
        self.MIPOWER_Over_Power = 2
        self.MIPOWER_Normal_Power = 1
        self.maxOverPowerCounts = 2
        self.Acoef = -0.57
        self.Bcoef = -0.83
        self.PlateType = 'Default_plate'
        self.Concentration = '100'
        self.makeplots = True
     
        return
     
     def closeFile(self):
        self.h5file.close()
        return
     
     def getSurveyDat(self):
         cols = self.psurvey.createColumns()
         mySAnaData = self.psurvey.getAnalysisData()
         header = self.psurvey.columns
         cheader= [ f['name'] for f in header ]
         platesurveydat = pandas.DataFrame(mySAnaData, columns=cheader)
         return platesurveydat
     
     def getPrintDat(self):
         header = self.pt.createPrintDataColumns()
         cheader= [ f['name'] for f in header ]
         ptdata = self.pt.getPrintData()
         printdat = pandas.DataFrame(ptdata['data'], columns=cheader)
         return printdat, ptdata['emptyWellCombos']
     
     def plotAllWells(self,filename='allMISolutions.pdf', reprocess=False, tier=0, nwells=384, path=None):
        if not path:
            path = self.path
        row1536 = list(map(chr, range(97, 97+26))) 
        row1536b = [ 'A' + x for x  in list(map(chr, range(97, 97+6))) ]
        row1536.append(row1536b)
        row384 = list(map(chr, range(97, 97+16)))  
        row96 = list(map(chr, range(97, 97+8))) 
        alldata = []
        if (nwells == 384):
            row = row384
            cols = 24
            pagesperrow = 1
        elif (nwells == 96):
            row = row96
            cols = 12
            pagesperrow = 1
        else:
            row = row1536
            cols = 24
            pagesperrow = 2
        with PdfPages(path + '/' + filename) as pdf:
            for r in row:
                for i in range(0,pagesperrow):
                    alld = self.plotNSbyRow(r.upper(),tier, reprocess, cols,1+cols*i)
                    alldata += alld
                    pdf.savefig()
                    plt.clf()
        return pandas.DataFrame(alldata)
     
     def plotOP(self, wellcombo='A1-A1', ax=None, reprocess=False, tier=0):
        if (reprocess):
           midat = self.reprocessMIP(wellcombo,tier)
        else:
           midat = self.getMIPframe(wellcombo,tier) 
        if ( len(midat.index) == 0):
            if (self.makeplots) :
                return ax, []
            else:
                return []
        if (not self.makeplots ) :
            return midat
        genFig = False
        if ax == 'None':    
            fig = plt.figure()
            ax = fig.add_subplot(111) 
            genFig = True 
            
        midat['Vrms2'] = midat['Vrms']*10 ;
        midat['OverPower']*= 20; 
        midat['PeakSeparation'] *= 3;
        midat[['Iter.','PowerdB','NullSpace','PeakSeparation','RingAmplitude','Vrms2','OverPower']].plot(x='PowerdB',y=['RingAmplitude','Vrms2','OverPower','PeakSeparation'],ax=ax,title=wellcombo)    
        
        if (genFig):
            plt.show()  
            return midat
        else:    
            return ax, midat
            
     def plotOPbyRow(self,thisrow='A',tier=0,reprocess=False,cols=24,start=1):
       
        plotsperfigrow = 6
        nrows = cols//plotsperfigrow      
        row = 0
        col = 0
        alldat = {}
        if (self.makeplots):
            fig, ax = plt.subplots(nrows=nrows,ncols=plotsperfigrow, figsize=(16,16))
            plt.ioff()
        for i in range(start,start+cols):
            wellcombo = [ x for x in self.transfergroups if (thisrow + str(i) + '-') in x ]
            if len(wellcombo) != 0 :
                
       #         if ( len(midat.index) == 0):
       #             if  ( col >= ( plotsperfigrow -1 ) ):
       #                 col = 0
       #                 row += 1
       #             else:
       #                 col += 1 
       #             continue
                #sel = self.getValidMIP(midat)
 #               print(' --- sel size :: ' , sel.shape[0], ' --- ')
                if (self.makeplots):
                    ax[row][col], midat = self.plotOP(wellcombo=wellcombo[0],ax=ax[row][col],reprocess=reprocess,tier=tier)
                else:
                    midat = self.plotOP(wellcombo=wellcombo[0],reprocess=reprocess,tier=tier)
                #midat['Vrms2'] = midat['Vrms']*10 ;
                #midat['OverPower']*= 20; 
                #midat[['Iter.','PowerdB','NullSpace','PeakSeparation','RingAmplitude','Vrms2','OverPower']].plot(x='PowerdB',y=['RingAmplitude','Vrms2','OverPower'],ax=ax[row][col])
                if (len(midat) > 0):
                    alldat[wellcombo[0]] = midat
               
            if  ( col >= ( plotsperfigrow -1 ) ):
                col = 0
                row += 1
            else:
                col += 1 
           # if ( len(acoef) > 1) :    
           #     alldat += [wellcombo[0].split('-') + [ acoef[0] ] ]
           # else :
            #    alldat += [wellcombo[0].split('-') + [ 0 ] ]
        if (self.makeplots) :
            plt.tight_layout()
        return alldat
        
     def plotNSbyRow(self,thisrow='A',tier=0,reprocess=False,cols=24,start=1):
        plotsperfigrow = 4
        nrows = cols//plotsperfigrow
        fig, ax = plt.subplots(nrows=nrows,ncols=plotsperfigrow, figsize=(12,12))
        row = 0
        col = 0
        alldat = []
        plt.ioff()
        for i in range(start,start+cols):
            wellcombo = [ x for x in self.transfergroups if (thisrow + str(i) + '-') in x ]
            if len(wellcombo) != 0 :
                if (reprocess):
                    midat = self.reprocessMIP(wellcombo[0],tier)
                else:
                    midat = self.getMIPframe(wellcombo[0],tier)
                if ( len(midat.index) == 0):
                    if  ( col >= ( plotsperfigrow -1 ) ):
                        col = 0
                        row += 1
                    else:
                        col += 1 
                    continue
                sel = self.getValidMIP(midat)
 #               print(' --- sel size :: ' , sel.shape[0], ' --- ')
                acoef, axx = self.plotNS(np.log(sel['NullSpace']),sel['PowerdB'],wellcombo[0],ax[row][col])
            if  ( col >= ( plotsperfigrow -1 ) ):
                col = 0
                row += 1
            else:
                col += 1 
            if ( len(acoef) > 1) :    
                alldat += [wellcombo[0].split('-') + [ acoef[0] ] ]
            else :
                alldat += [wellcombo[0].split('-') + [ 0 ] ]
        plt.tight_layout()
        return alldat
     
     def plotNS(self,ns,db,wellcombo='XX-YY',ax='None'):
        validres = False
        if ( len (db) > 1 ):
            res = stats.theilslopes(db, ns, 0.90)
            lsq_res = stats.linregress(ns, db)
            validres = True
        else:
            res = []
            lsq_res = []
        #Plot the results. The Theil-Sen regression line is shown in red, with the dashed red lines illustrating the confidence interval of the slope (note that the dashed red lines are not the confidence interval of the regression as the confidence interval of the intercept is not included). The green line shows the least-squares fit for comparison.
        genFig = False
        if ax == 'None':    
            fig = plt.figure()
            ax = fig.add_subplot(111) 
            genFig = True
            
        ax.plot(ns, db, 'bo')
        if (validres):
            ax.plot(ns, res[1] + res[0] * ns, 'r-')
            ax.plot(ns, lsq_res[1] + lsq_res[0] * ns, 'g-')
        ax.set_xlabel('ln(ns)')
        ax.set_ylabel('dB Power')
        
        # confidence interval of slopes
        # ax.plot(ns, res[1] + res[2] * ns, 'r--')
        #ax.plot(ns, res[1] + res[3] * ns, 'r--')
        
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax.text(0.55, 0.9, wellcombo, transform=ax.transAxes, fontsize=14, verticalalignment='top', bbox=props)
        if (genFig):
            plt.show()  
            return res
        else:    
            return res, ax     
     
     def getValidMIP(self,mipdataframe):
        if self.maxNullSpaceMHz < 0 :
            print(' ---- Error ---  Please specify maxnullspace >= 0')
            return
    #    selection = mipdataframe[mipdataframe['NullSpace']>minnullspace]
        selection =  mipdataframe[(mipdataframe['PowerMatrix'].apply(lambda x: (x & self.MASK) == self.MASK) ) & (mipdataframe['NullSpace'] > self.minNullSpaceMHz) & (mipdataframe['NullSpace'] < self.maxNullSpaceMHz ) & (mipdataframe['PowerdB'] < self.maxdB)]
        return selection
        
     def getMIPframe(self,wellcombo='A1-A1',tier=0):
        dataframepath = '/Transfer/' + wellcombo + '/RTMIP-T' + str(tier) + '/MIPAnalysis'
        if dataframepath in self.h5file:
            hh = self.pt.createMipAnalysisColumns(dataframepath)
            hhd = self.pt.getMipAnalysis(dataframepath)
            chh = [ f['name'] for f in hh ]
            mipdataframe = pandas.DataFrame(hhd,columns=chh)
            mipdataframe['PowerMatrix'] = mipdataframe['PowerMatrix'].apply(lambda x: int(x, 16))
            mipdict = mipdataframe.to_dict(orient='records')
            for i in range(0, len(mipdict)):
                mipdict[i] = self.overPowerAna(mipdict[i])
            mipdataframe = pandas.DataFrame(mipdict)
            return mipdataframe
        else:
            return pandas.DataFrame()    
     
     def overPowerAna(self, miana):
         op = self.isOverPower(miana)
         if op > 0 :
            miana['OverPower'] = 1
            miana['OverPowerFlag'] = op
         else:
            miana['OverPower'] = 0
            miana['OverPowerFlag'] = 0
         return miana
            
     def setTargetFreqRange(self,targfreqstartMHz,targfreqstopMHz):     
         self.MI.mi_param.TargetFreqStartMhz = targfreqstartMHz
         self.MI.mi_param.TargetFreqStopMhz  = targfreqstopMHz 
         return
         
     
     def reprocessMIP(self, wellcombo='A1-A1',tier=0):
        miframe = self.getMIPframe(wellcombo,tier)
        dataframepath = '/Transfer/' + wellcombo + '/RTMIP-T' + str(tier) + '/PowerSweep'
 #       print(' dataframepath = ', dataframepath)
        if not dataframepath in self.h5file:
            return pandas.DataFrame()
        niterations = self.miwav.getNumberOfIterationsForTier(dataframepath,0)
#        print(' nit: ', niterations)
        AllMIAnalysis = []
        for i in range(0,niterations):
            wav = self.miwav.getWaveform(dataframepath,i,0)
            wavL = [ float(r) for r in wav ]
            MIAnalysisdata = self.MI.MoundImageAnalysis(wavL)
            MIAnalysisdata = self.overPowerAna(MIAnalysisdata)
            AllMIAnalysis.append(MIAnalysisdata)  
        MIReanalysisDF = pandas.DataFrame(AllMIAnalysis)    
        for key in ['Powervolt','PowerdB','Ping','Iter.']    :
            MIReanalysisDF[key] = miframe[key]    
        return MIReanalysisDF    
        
     def reprocessAll(self, recalculate=True):
        reprocessedprintdat = [] #pandas.DataFrame(columns=self.printdat.columns)
        relevantindices = [ 'LeftNull', 'MaxRawPeakHeight', 'MaxRawPeakPosition', 'MoundWidth', 'NullPeak', 'NullSpace',  'PowerMatrix', 'Preamble', 'RightNull', 'RingDecay',  'Powervolt', 'PowerdB']
        additionalindices = ['PeakFactor', 'RingAmplitude', 'RingFrequency' ]
        #for index, row in self.printdat.iterrows():
        if ( not isinstance(self.printdat,pandas.DataFrame ) ):
            print(' no converged wells found in file ', self.h5file.filename )
            print(' need code-update to handle this case. ')
            print(' method FineMipAna::reprocessAll' )
            return
        for Wellcombo in self.transfergroups:    
            Tier = 0
            misolution = pandas.DataFrame()
 #           while ( ( not misolution.empty) or ( Tier < 3 )):
             #   Src = row['SW']
             #   Dest = row['DW']
             #   Wellcombo = Src + '-' + Dest
            if (recalculate):
                # non-optimal solution for recalculation FIXME :: 
                Tier =  self.pt.getTierFromSolutionPath(self.pt.getSolutionPath(Wellcombo))
  #              print( ' Tier :: ' , Tier)
                if int(Tier) < 0 :
                    continue
                miframe = self.reprocessMIP(Wellcombo,Tier)
                if 'FFTWidth' in miframe.columns:
                    miframe['PeakSeparation']= miframe['FFTWidth']
            else:
                Tier =  self.pt.getTierFromSolutionPath(self.pt.getSolutionPath(Wellcombo))
                miframe = self.getMIPframe(Wellcombo,Tier)
            misolution = self.getMISolution(miframe)
#                Tier += 1
                    
            SW = Wellcombo.split('-')[0]
            DW = Wellcombo.split('-')[1]
            row = self.printdat[ ( self.printdat['SW'] == SW) & (self.printdat['DW'] == DW )]
            if (row.empty):
                # suppress error message:
                row.is_copy = False
                # create empty row
                row.loc[0] = 0
                # fill src , dest wells
                row.loc[0,'SW']=SW
                row.loc[0,'DW']=DW
                # fill some attributes from survey if available - if no survey just continue
                rsurvey = self.surveydat[ (self.surveydat['W'] == SW ) ]
                if (rsurvey.empty):
                    continue
                rrsurvey = rsurvey.iloc[0]
                row.loc[0,'Out. Compos.'] = rrsurvey['ConcentrationPct']
                row.loc[0,'FluidThicknessMM'] = rrsurvey['FillHeightMM']
            thisrow = row.iloc[0]  
            # suppress error message:
            thisrow.is_copy = False
            if (not misolution.empty):
                for col in relevantindices:
                    thisrow[col] = misolution[col]
                thisrow['NumOfIterations'] = misolution['Iter.']
                thisrow['PeakSeparation'] = misolution['PeakSeparation']
                if (recalculate):
                    for col in additionalindices:
                        thisrow[col] = misolution[col]
                subejectampvpp = misolution['Powervolt']
                dBEnergy = - ( np.log(misolution['NullSpace'])*self.Acoef + self.Bcoef )
                thisrow['D2AVpp'] = subejectampvpp * np.power(10,dBEnergy/20)
                reprocessedprintdat.append(thisrow)
            else:
                print(' ---- more code required to process wellcombo ', Wellcombo, ' ----- ', ' Recalculate = ', recalculate)
            # need to go to next Tier if not overpowered
        #         
        return  pandas.DataFrame(reprocessedprintdat)     

 
       
     def getMISolution(self,midataframe):
         targetNull = self.MI.mi_param.MaxGoodNullMHz
         bMIPass = False
         lastNullSpaceMHz = -10
         for index, row in midataframe.iterrows():
             overpowercounts = 0 
             lastNullSpaceMHz = -10
             lastPowerState = 0x0
             bMIPass = False
             powerMatrixState = int(row['PowerMatrix']) & 0xffff 
   #          print(row)
             if ((powerMatrixState & 0xFF00 ) != ( 0xFF00)):
                 dBPowerStateEnum = powerMatrixState & 0xf
                 nullSpaceMHz = row['NullSpace']
                 if (( row['PeakSeparation'] > 6.0 ) and ( nullSpaceMHz >= 1.5 ) and (nullSpaceMHz <= 4) and  ( (( powerMatrixState & ( 0xE << 4 ) ) >> 4 )   == 0xE) ):
                     lastNullSpaceMHz = nullSpaceMHz
                     lastPowerState = powerMatrixState
                     lastIndex = index
                 if ((( dBPowerStateEnum ==  self.MIPOWER_Normal_Power or dBPowerStateEnum ==  self.MIPOWER_Over_Power ) and (nullSpaceMHz >= 0.5 ) and ( nullSpaceMHz <= targetNull ) ) or \
                     (( dBPowerStateEnum == self.MIPOWER_Over_Power) and ( (( powerMatrixState & ( 0xA << 4 ) ) >> 4) == 0xA ) and ( nullSpaceMHz < 3. ))):
                     bMIPass = True    
                     return row
                 if (dBPowerStateEnum == self.MIPOWER_Over_Power):
                     overpowercounts += 1
                 if (overpowercounts > self.maxOverPowerCounts):  
                     break
         if ( not bMIPass ):   
            if ( lastNullSpaceMHz > 0 ):
               if ( overpowercounts >= self.maxOverPowerCounts):
                   return pandas.DataFrame()
               else:
                   return midataframe.iloc[lastIndex]
            else:
               return pandas.DataFrame()       
         else:
             return pandas.DataFrame()
             
     def plotReProcessedData(self, reprocesseddata, saveFig=False, filename='ReProcessed.png', nwells=384):
         title= (self.PlateType + '-' + self.Concentration)
         solvedwells = reprocesseddata.shape[0]
         title += ':: ' + str(solvedwells) + '/' + str(nwells)
         fig, ax = plt.subplots(nrows=3,ncols=2, figsize=(12,12))
         cols=['D2AVpp','NullPeak','NumOfIterations','Preamble','PeakSeparation','PM']
         reprocesseddata['PM'] = reprocesseddata['PowerMatrix'].apply(lambda x: int(x) & 0xf)
         for i in range(0,3):
             for j in range(0,2):
                 reprocesseddata.plot(kind='scatter', y=cols[i*2+j], x='FluidThicknessMM', ax=ax[i][j])          
       #          reprocesseddata.boxplot(column=cols[i*2+j], by='FH', ax=ax[i][j])
                 ax[i][j].set_xlabel('FillHeight (mm)')
         fig.suptitle(title,size='16')
         plt.tight_layout()
         fig.subplots_adjust(hspace=0.25,top=0.95)
         if (saveFig):
              fi = plt.gcf()
              fi.savefig(self.path + '\\' + filename,bbox_inches='tight')
         return  
            
             