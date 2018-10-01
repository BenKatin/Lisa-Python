# -*- coding: utf-8 -*-
"""
Created on Mon May 30 13:52:21 2016

@author: avandenbroucke
"""

import numpy as np
import xlrd
from collections import namedtuple
#from recordtype import recordtype
import matplotlib.pyplot as plt
import os
import pandas as pd


#if ( __package__ is None ):
#    from ReadEchoFiles  import ReadCSV
#else:
#    print( ' --package-- :: ' , __package__)
#    from ..ReadEchoFiles import ReadCSV

    

#if ( __package__ is None ):
from ..ReadEchoFiles  import ReadCSV
import time
import datetime
#else:
#    print( ' --package-- :: ' , __package__)
#    from ReadEchoFiles import ReadCSV






class ReaderDat():
 #   StdCurveType = namedtuple('StdCurveType','Slope Offset PMTCorr PMTRef')
    PRINTSTATS_FIELDS = ['N','Mean','RawCV','CV','Reliability','Outlier','Empties','PMTCorr']
    _PrintStats =  namedtuple('_PrintStats',PRINTSTATS_FIELDS)
    STDCURVE_FIELDS = ['Slope','Offset','PMTRef','PMTCorr']
    
    
    def __init__(self):
        self.StdCurveA = 0
        self.StdCurveSlope = 0
        self.StdCurveOffset = 0
        self.StdCurvePMTRef = 1
        self.StdCurvePMTCorr = 1
        self.EmptyThresh = 0.9
        self.OverFlVal = 999999
        self.OverFlVol = 20000
        self.InternalRefCol = 15
        self.bUseInternalStd = False
        self.PMTCorrectionTolerance = 0.15
        self.readerCalsDF = self.readCalCurves()
        self.verbose = False
        self.readerdatAvailable = False
        self.applyPMTCorr = False
        self.exclude16 = False
        return     

    def getSupportedReaders(self, UseInternalStd = False, MFG=False, Fluor=True):
        if Fluor:
            mode ='Fluor'
        else:
            mode = 'Abs'
        if MFG:
            readers = list(set(self.readerCalsDF['Reader'][(self.readerCalsDF['IntStd'] == UseInternalStd) & (self.readerCalsDF['Category'] == 'MFG') & (self.readerCalsDF['Mode'] == mode)].values))
        else:
            readers = list(set(self.readerCalsDF['Reader'][(self.readerCalsDF['IntStd'] == UseInternalStd) & (self.readerCalsDF['Mode'] == mode)].values))
        
        return readers
        

    def getSupportedLUTs(self,reader, UseInternalStd = False, MFG=False, Fluor=True):
        if Fluor:
            mode ='Fluor'
        else:
            mode = 'Abs'
        if MFG:
            LUTs = list(set(self.readerCalsDF['LUTDate'][(self.readerCalsDF['Reader'] == reader ) & (self.readerCalsDF['IntStd'] == UseInternalStd) & (self.readerCalsDF['Category'] == 'MFG') & (self.readerCalsDF['Mode'] == mode)]))
        else:
            LUTs = list(set(self.readerCalsDF['LUTDate'][(self.readerCalsDF['Reader'] == reader ) & (self.readerCalsDF['IntStd'] == UseInternalStd) & (self.readerCalsDF['Mode'] == mode)]))
        return LUTs
        
    def getCalibrations(self, reader, UseInternalStd = False, MFG=False, Fluor=True):
        return self.getSupportedLUTs(reader,UseInternalStd, MFG, Fluor)
        
 
    def getInternalStdCalibrations(self, reader = None, lutdate=None, useInternalStd = True):
        if not reader:
            print('Please specify reader')
            return
        if not lutdate:
            print('Please specify lutdate')
            return
        return list(set(self.readerCalsDF['CalDate'][(self.readerCalsDF['LUTDate'] == lutdate) & (self.readerCalsDF['Reader'] == reader ) & (self.readerCalsDF['IntStd'] == useInternalStd)]))    
        
        
    def getCalDate(self, reader, lutdate, processdate = None, useInternalStd = True) :
        # processdate in Unix format, use os.path.getmtime(filename)
        if not processdate:

            return
        else :
            PossibleDates =  sorted(self.getInternalStdCalibrations(reader, lutdate), reverse=True)
            for k in PossibleDates:
                dt0 = datetime.datetime.strptime(str(k), '%Y%m%d')
                dt = time.mktime(dt0.timetuple())
                if processdate >= dt:
                    return k
 
    def calCurvesToDF(self):
        AllCals = []
        for reader in self._getSupportedReaders():
            for i in range(0,2):
                if i==0:
                    intstd = False
                else: 
                    intstd = True
                cals = self._getCalibrations(reader,UseInternalStd=intstd)
                if cals == None :
                    continue
                print(' Reader: ', reader)
                for lutkey, luts in cals.items():
                    for k, cals in luts.items():
                        ThisCal = {}
                        ThisCal['LUTDate'] = lutkey
                        ThisCal['Reader'] = reader
                        ThisCal['IntStd'] = intstd
                        ThisCal['CalDate'] = k
                        coef = [ 'A','B','C','PMTCorr'] 
                        for j, l in enumerate(coef):
                            ThisCal[l] = cals[j]
                        AllCals.append(ThisCal)                
        return pd.DataFrame.from_dict(AllCals)
        
    def _writeCalCurves(self):
        readercals = self.calCurvesToDF()
        basedir = os.path.join(os.path.dirname(__file__), 'ReaderCal')
        filename = basedir + os.sep + 'ReaderCal.csv'
        print('Writing ReaderCal to file : ',filename)
        readercals.to_csv(filename,index=False, columns= ['Reader','LUTDate','IntStd','CalDate','A','B','C','PMTCorr'])
        
    def readCalCurves(self):
        basedir = os.path.join(os.path.dirname(__file__), 'ReaderCal')
        filename = basedir + os.sep + 'ReaderCal.csv'
 #       print(' filename:: ',filename)
 #       time.sleep(30)
        return pd.read_csv(filename, dtype={'CalDate' : 'str'})
                    
    def setStdCurve(self,lutdate='042016', reader='BioTek1', UseInternalStd = False, caldate=None):
        self.bUseInternalStd = UseInternalStd
        if reader not in self.getSupportedReaders():
           print(' ***** Error **** Reader ', reader, ' not supported')
           return 
        self.setCalCurve(reader=reader,useInternalStd=UseInternalStd,lutdate=lutdate,caldate=caldate)
        self.reader = reader
        return
        
   
    def setCalCurve(self, reader, useInternalStd, lutdate, caldate = None):
        self.bUseInternalStd = useInternalStd
        stdcurvecaldates = self.getInternalStdCalibrations(reader=reader,lutdate=lutdate, useInternalStd = useInternalStd)
        indexes = sorted(stdcurvecaldates, reverse= False)
        nodate = False
        if self.verbose:
            print('stdcurvecaldates: ' ,stdcurvecaldates)
            print('indexes: ', indexes)
        if len(stdcurvecaldates) == 1:
           date = indexes[0]
           try:
               len(date)
           except:
               nodate = True
        if not caldate:
           date = indexes[-1]
        else:
           if caldate in stdcurvecaldates:
               date = caldate
           else:
               print(' Calibration date ', caldate, ' not referenced for reader: ', reader)
               return [0]    
        if nodate :
            CC = self.readerCalsDF[(self.readerCalsDF['Reader'] == reader) & (self.readerCalsDF['IntStd'] == useInternalStd) & (self.readerCalsDF['LUTDate'] ==  lutdate) 
                    ] 
        else :    
            CC = self.readerCalsDF[(self.readerCalsDF['Reader'] == reader) & (self.readerCalsDF['IntStd'] == useInternalStd) & (self.readerCalsDF['LUTDate'] ==  lutdate) 
                     & (self.readerCalsDF['CalDate'] == date)]
        if len(CC) != 1:
            print( ' Ambiguous combination for caldate ', caldate, ' reader: ', reader, ' lutdate: ', lutdate)
            return [0]
        if (self.verbose):
            print(CC)
        self.StdCurveA = CC['A'].values[0]
        self.StdCurveSlope = CC['B'].values[0]
        self.StdCurveOffset = CC['C'].values[0]
        self.StdCurvePMTRef = CC['PMTCorr'].values[0]
        self.reader=reader
        return
 
        
    def setPMTCorr(self,f1,f2):
        '''
        Calculates PMT Correction based on matech files
        f1: Matech File 1
        f2: Matech File 2
        '''
        # todo :: check if f1 exists :: generic function
        if 'BioTek'.lower() in self.reader.lower() :
            PMT_Before = self.processBiotek(f1,12,8)
            PMT_After = self.processBiotek(f2,12,8)
        elif 'Neo'.lower() in self.reader.lower() :
            PMT_Before = self.processBiotek(f1,12,8)
            PMT_After = self.processBiotek(f2,12,8)
        elif ('AscentUK'.lower() in self.reader.lower() ):    
            PMT_Before = self.processAscent(f1, 12, 8)
            PMT_After = self.processAscent(f2, 12, 8 )
        elif ('BMG'.lower() in self.reader.lower() ):
            PMT_Before = self.processBMG(f1, 12, 8)
            PMT_After = self.processBMG(f2, 12, 8 )
        else:
            print(' *** ERROR --- PMT Corr not supported for reader ', self.reader)
            self.StdCurvePMTCorr = 1
            return
        PMT_Average = (PMT_Before.mean() + PMT_After.mean())/2.
        self.StdCurvePMTCorr =  self.StdCurvePMTRef / PMT_Average
        return
    
    def setInternalRefCorr(self,readerdat):
        refcol0 = readerdat[:,self.InternalRefCol]
        mean0 = refcol0.mean()
        #refcol = [d for d in refcol0 if d > 0.85*mean0 and d < 1.15*mean0]
  #      print('refcol: ', refcol0)
  #      print(' PMTRef : ', self.StdCurvePMTRef)
        refcol =  [d for d in refcol0 if d > (self.StdCurvePMTRef*(1-self.PMTCorrectionTolerance)) and d < (self.StdCurvePMTRef*(1+self.PMTCorrectionTolerance ))]
    #    print('Ref wells: ', len(refcol))
        if len(refcol) > 0 :
            mean = np.mean(refcol)
        else:
            mean = mean0
        self.StdCurvePMTCorr = self.StdCurvePMTRef / mean
 #       print('PMT correction: ', self.StdCurvePMTCorr)
        return
    
    def getPrintStats(self,readerdat,mask=0xFFFF,rows=16, rowmask=True):        
        # here we mark reliabilities:
        # let's count mean on reliabilites only
        # here we need to count the numer of empties
        

        if not  self.readerdatAvailable :
            print(' *** ERROR *** No valid readerdata available to calculate stats ')
            return self._PrintStats(0,0,0,0,0,0,0,self.StdCurvePMTCorr) 
        

        if (self.bUseInternalStd) or (self.exclude16):        #added to support internal reference
            readerdat0 = np.delete(readerdat, self.InternalRefCol, 1) # drop column where the internal standard is located - LC
        else:
            readerdat0 = readerdat
        if ( abs(self.StdCurveA) > 1e-8 ):
            readerdat_valid = [d for d in readerdat0.flatten() if d > self.EmptyThresh]           
        else:
            readerdat_valid = [ d for d in readerdat0.flatten() if d > self.EmptyThresh and d <  self.StdCurvePMTCorr*((self.OverFlVal - self.StdCurveOffset) / self.StdCurveSlope)]
        
        if (rowmask):
            rows_to_delete = []
            for i in range(0,rows):
                if not ( ( 1 << i ) & mask ):
                    rows_to_delete.append(i)
          #  print(' rows to delete: ', rows_to_delete)    
          #  readerdat_valid = np.delete(readerdat_valid, rows_to_delete, 0)   
            readerdat0 = np.delete(readerdat0, rows_to_delete, 0)
        else:
            cols_to_delete = []
            cols = rows
            for i in range(0,cols):
                if not ( ( 1 << i ) & mask):
                    cols_to_delete.append(i)
            readerdat0 = np.delete(readerdat0, cols_to_delete,1)        
            
#        self.OverFlVol = self.StdCurvePMTCorr*( self.OverFlVal*self.StdCurveSlope + self.StdCurveOffset) 
#    
        readerdat_valid = [ d for d in readerdat0.flatten() if d > self.EmptyThresh and d < self.OverFlVol ]
  #      print( ' rederdat_valid : ' , np.shape(readerdat0))
        mean = np.asarray(readerdat_valid).mean()     
        
        Reliability = np.ma.masked_inside(readerdat_valid,0.6*mean,1.4*mean).count()
        if (Reliability):
            Mean = np.ma.masked_outside(readerdat0,0.6*mean,1.4*mean).mean()
            CV = 100*np.ma.masked_outside(readerdat0,0.6*mean,1.4*mean).std()
        else:
            Mean = mean
            CV = 100*np.asarray(readerdat_valid).std()
        CV /= Mean
       
        
        RawCV = 100*np.asarray(readerdat_valid).std()
        RawCV /= Mean
        
        
        Empties = np.ma.masked_greater(readerdat0,self.EmptyThresh).count()
        N = len(readerdat0.flatten()) 
        # here we mark reliabilities based on updated mean:
        Reliability = np.ma.masked_inside(readerdat_valid,0.6*Mean,1.4*Mean).count()
        # here we count the outliers:
  #      if (self.bUseInternalStd):
  #          readerdat0 = np.delete(readerdat, self.InternalRefCol, 1) # drop column where the internal standard is located
  #          readerdat_not_reliability = [ d for d in readerdat0.flatten() if d > 0.6*Mean and d < 1.4*Mean ]
  #      else:
        readerdat_not_reliability = [ d for d in readerdat0.flatten() if d > 0.6*Mean and d < 1.4*Mean ]
            
        Outlier = np.ma.masked_inside(readerdat_not_reliability,0.85*Mean,1.15*Mean).count()
#        MeanC = Mean*self.StdCurvePMTCorr
        thisstats = self._PrintStats(N,Mean,RawCV,CV,Reliability,Outlier,Empties,self.StdCurvePMTCorr) 
        return thisstats     
    
    def validStdCurve(self):
        if ( self.StdCurvePMTCorr == 1):
            # FIXME :: the equation above should be a float comparison
            print(' ***** WARNING ::: PMT Correction factor = 1')
        if ( self.StdCurvePMTCorr < ( 1-self.PMTCorrectionTolerance )) or (self.StdCurvePMTCorr > ( 1 + self.PMTCorrectionTolerance)):
            print(' ***** ERROR :: PMT correction too high (PMTCorr = ', self.StdCurvePMTCorr, ')')
            return False
        if abs(( self.StdCurveSlope ) * (self.StdCurveOffset ) ) > 1e-6 :
            return True
        else:
            print(' ***** ERROR :: Please add Standard curve information ')
            return False

    def openXLbook(self, filename):
        """Open Excel file and return list of sheetnames"""
        xl_workbook = xlrd.open_workbook(filename)
        return xl_workbook
        
    def processRow(self, sheet,rownr,startcolumn,endcolumn):
        """Returns row from startcolumn to endcolumn in sheet as list"""
        row = sheet.row(rownr)
        r = []
        for idx, cell_obj in enumerate (row):
    #        cell_type_str = ctype_text.get(cell_obj.ctype, 'unknown type')
            if (idx >= startcolumn) and (idx < endcolumn):
                val = cell_obj.value
                try:
                    fval = float(val)
                except ValueError:
                    fval = self.OverFlVal
                r.append(fval)
    #        print('(%s) %s %s' % (idx, cell_type_str, cell_obj.value))
        return r
    
    def processReaderFile(self,filename,ncols=24,nrows=16,pattern=0xFFFF):
        if ('UK') in self.reader:
            if 'Ascent'.lower() in self.reader.lower(): 
                return self.processAscent(filename,ncols,nrows,pattern)
            elif 'BMG'.lower() in self.reader.lower():
                return self.processBMGUK(filename,ncols,nrows,pattern)
            else:
                print(' ***  ERROR ::  Reader ', self.reader, ' not supported ')
        else:    
            if 'Biotek'.lower() in self.reader.lower():
                return self.processBiotek(filename,ncols,nrows,pattern)
            elif  'Neo'.lower() in self.reader.lower():
                return self.processBiotek(filename,ncols,nrows,pattern)
            elif 'Ascent'.lower() in self.reader.lower(): 
                return self.processAscent(filename,ncols,nrows,pattern)
            elif 'BMG'.lower() in self.reader.lower():
                return self.processBMG(filename,ncols,nrows,pattern)
            else:
                print(' ***  ERROR ::  Reader ', self.reader, ' not supported ')
        return
    
    def processBiotek(self, filename,ncols=24,nrows=16,pattern=0xFFFF):
        """Process XLS file from Biotek Reader"""
        xlbook = self.openXLbook(filename)
        xlsheet =  xlbook.sheet_by_name('Sheet1')  
        startrow = 15
        startcol = 2
        rawreaderdat = np.empty([nrows,ncols])
        for ii in range(0,nrows):
          if (( pattern >> ii ) & 0x1 ):
              tmp = np.array(self.processRow(xlsheet,startrow+ii,startcol,startcol+ncols))
              rawreaderdat[ii] = tmp.astype(np.float)
    # Extract mean, stde , cv 
        return rawreaderdat  
         
    def processAscent(self, filename,ncols=24,nrows=16,pattern=0xFFFF):
        """Process XLS file from Ascent Reader"""
        print( ' Ascent file :: ', filename)
        basename = os.path.basename(filename)
        sheetname = basename.rstrip('.XLS')
        sheetname = sheetname.replace('.','') 
        xlbook = self.openXLbook(filename)
        sheetnames = xlbook.sheet_names()
 #       print(' sheetname : ', sheetname )
 #       print(' sheet : ', sheetnames)
        if sheetname not in sheetnames:
            sheetname = sheetnames[0]
        xlsheet =  xlbook.sheet_by_name(sheetname)  
        startrow = 3
        startcol = 1
        rawreaderdat = np.empty([nrows,ncols])
        for ii in range(0,nrows):
          if (( pattern >> ii ) & 0x1 ):
              tmp = np.array(self.processRow(xlsheet,startrow+ii,startcol,startcol+ncols))
              rawreaderdat[ii] = tmp.astype(np.float)
    # Extract mean, stde , cv 
        return rawreaderdat

    def processAscentUK(self, filename, ncols=24, nrows=16, pattern=0xFFFF, headerrow=7):
        print(' Warning -- AVDB 2017JAN29 -- this code likely is broken as this was chagned : ')
        return self.processBMGUK(filename, ncols, nrows, pattern, headerrow)

    def processBMGUK(self, filename, ncols=24, nrows=16, pattern=0xFFFF, headerrow=19):
        """Process CSV file from BMG Fluostar in Cannock"""
        header = ReadCSV.getCSVHeader(filename, headerrow)
        data =   ReadCSV.readCSV(filename,False,header)   
        validdata = [ f[1:] for f in data if len(f) > 0 and f[0] in 'ABCDEFGHIJKLMNOP' ]
        rawreaderdat = np.empty([nrows,ncols])
        rawreaderdat = np.asarray(validdata).astype(float)
        droplist = []
        for ii in range(0,nrows):
              if not (( pattern >> ii ) & 0x1 ):
                  # remove from array:
                  droplist.append(ii)
        if len(droplist) > 0:
            rawreaderdat = np.delete(rawreaderdat, droplist, 0 )
        return rawreaderdat
           
        
    def processBMG(self, filename, ncols=24, nrows=16, pattern=0xFFFF, headerrow=19):        
#        if 'Clariostar' in self.reader:
#            headerrow = 17
        """Process CSV file from BMG Fluostar"""
        header = ReadCSV.getCSVHeader(filename, headerrow)
        data =   ReadCSV.readCSV(filename,False,header)   
        validdata = [ f[1:] for f in data if len(f) > 0 and f[0] in 'ABCDEFGHIJKLMNOP' ]
        rawreaderdat = np.empty([nrows,ncols])
        if '' in validdata[0]:
            validdata=validdata[1:]
        rawreaderdat = np.asarray(validdata).astype(float)
        droplist = []
        for ii in range(0,nrows):
              if not (( pattern >> ii ) & 0x1 ):
                  # remove from array:
                  droplist.append(ii)
        if len(droplist) > 0:
            rawreaderdat = np.delete(rawreaderdat, droplist, 0 )
        return rawreaderdat
    
    def getProcessDate(self, filename):
         """Get process date from BMG Fluostar csv file"""
         df = pd.read_csv(filename, nrows = 7)
         dt = datetime.datetime.strptime(df.iloc[0][0], 'Date: %m/%d/%Y  Time: %I:%M:%S %p')
         processdate = time.mktime(dt.timetuple())
         return processdate
        
     
    def applyCalCurve(self,rawreaderdat): 
        if self.bUseInternalStd == True:
            self.setInternalRefCorr(rawreaderdat)
        if self.validStdCurve() == False:
            print(' *** ERROR :: improper std curve ')
            self.readerdatAvailable = False
            return        
        if ( abs(self.StdCurveA) > 1e-8 ):
            coeff = [self.StdCurveA,self.StdCurveSlope,self.StdCurveOffset]
            readerdat = np.polyval(coeff,rawreaderdat)
##            Find roots of polynomial equation
#            poly = np.poly1d([self.StdCurveA,self.StdCurveSlope,self.StdCurveOffset])
#            for x in np.nditer(rawreaderdat, op_flags=['readwrite']):
#                x[...] = min((poly-x).roots)
#            readerdat=rawreaderdat
#            r = (poly-rawreaderdat).roots
#            readerdat = r.max()
        else:    
            readerdat = (rawreaderdat - self.StdCurveOffset ) /  self.StdCurveSlope
        if self.applyPMTCorr:
            readerdat *= self.StdCurvePMTCorr
        self.readerdatAvailable = True
        return readerdat
         
    #    readerdat_f = np.ma.masked_less(readerdat,0.1)    
    def plotReaderDat(self,data,printstats,ax=None,title='XXp'):
        row_labels = list('ABCDEFGHIJKLMNOP')
        column_labels = [ i for i in range(1,25)]
        #fig, ax = plt.subplots(nrows=1,ncols=1,figsize=(12,18))
        if ax == None:
            fig = plt.figure(figsize=(12, 18))
            ax = fig.add_axes([0.1, 0.1, 0.9, 0.9])
#        axt = fig.add_axes([0.1, 0.8, 0.8, 0.1 ])
        mean = printstats.Mean
        heatmap = ax.imshow(data,cmap='coolwarm',interpolation='None',vmin=0.6*mean,vmax=1.4*mean)
        for y in range(data.shape[0]):
            for x in range(data.shape[1]):
                ax.text(x , y , '%.1f' % data[y, x],
                         horizontalalignment='center',
                         verticalalignment='center',
                     )
    
        # create an axes on the right side of ax. The width of cax will be 5%
        # of ax and the padding between cax and ax will be fixed at 0.05 inch.
     #   divider = plt.make_axes_locatable(ax)
     #   cax = divider.append_axes("right", size="5%", pad=0.05)
    
        
        plt.colorbar(heatmap,ax=ax,fraction=0.025, pad=0.04)
        # put the major ticks at the middle of each cell
        ax.set_xticks(np.arange(data.shape[1]) , minor=False)
        ax.set_yticks(np.arange(data.shape[0]) , minor=False)
    
        # want a more natural, table-like display
    #    ax.invert_yaxis()
        ax.xaxis.tick_top()
        ax.set_xticklabels(column_labels)
        ax.set_yticklabels(row_labels)    
        
        # make text box with stats
        textstring = title + ' Mean : ' + '{:4.2f}'.format(printstats.Mean) + 'nL'
        textstring += ' RawCV : ' + '{:4.1f}'.format(printstats.RawCV) + '%'
        #+ '\n'
        textstring += ' Empties : ' + '{:3d}'.format(printstats.Empties)
        textstring += ' Outliers : ' + '{:3d}'.format(printstats.Outlier)
        textstring += ' Reliabilities : ' + '{:3d}'.format(printstats.Reliability)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        
      #  axt.get_yaxis().set_visible(False)
      #  axt.get_xaxis().set_visible(Falsse)
        ax.text(0.05, 1.1, textstring, transform=ax.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)
        
    def processReaderDat(self,wdir='./'):
        fl = os.listdir(wdir)
        rf = [ f for f in fl if f.endswith('.xls') and 'matech' not in f.lower() ]        
        alld = {}
        for f in rf:
            dr = self.processBiotek(f);
            dc = self.applyCalCurve(dr); 
            if (dc):
                s = self.getPrintStats(dc)
                conc = f.split('_')[0]
                alld[conc] = s
        df = pd.DataFrame(alld).T  
        df.columns = self.PRINTSTATS_FIELDS
        df.index = [ float(i) for i in df.index ]
        return df.sort_index()
        
    def readertoDF(self,data,concentration):
        row_labels=list('ABCDEFGHIJKLMNOP')
        alldat = []
        for k in range(0,np.shape(data)[0]):
            for i in range(0,np.shape(data)[1]):
                l = [concentration, row_labels[k] + str(i+1), data[k,i] ]
                alldat.append(l)  
        df = pd.DataFrame(alldat)
        df.columns = [ 'concentration', 'DestWell', 'ReaderVol']        
        return df   
        
            