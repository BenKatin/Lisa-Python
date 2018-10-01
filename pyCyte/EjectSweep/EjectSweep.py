# -*- coding: utf-8 -*-
"""
Created on Fri Oct 30 17:21:14 2015

@author: avandenbroucke

Modified 1/30 to be used in pyCyte

Refactor 9/21/2016 to make code more robust and scalable
Need to also provide option to process raw reader data straight 

5/5/2017:
    Yongxi
    1. added the ability to process any picklist file. There should be 0 or "one and only
        one" csv file in the ejection sweep folder with "picklist" in the file name
        1a. Tested these functions
            processRawEjectSweep(...)    
            processEjectSweepRawReader_FixRange(...)
        1b. It should work for these too but not tested
            processEjectSweepDropCV_FixRange(self, filename, numTestsPerPlate=False )
            processEjectSweep(self, filelist, numTestsPerPlates=False)
    2. Write out (db, mean, std, cv) information to csv file
    3. Write out all the values in the BowlEstimate_bowl.png to csv file
    4. changed a default parameter. It may be danagerous unless the py code is updated regularly: 
        old: processRawEjectSweep(..., readercal='062016UKOmics', ...)
        new: processRawEjectSweep(..., readercal=None, ...)
    5. process any combinations of: [standard, HalfPlate, QuarterPlate]; [match, InternalStandard]
    6. The value of dB is not limited to -0.8 to 0.8. Any value listed in the picklist can be processed. 
    7. The quarter plate is limited to partition the plate as: row 1-4, 5-8, 9-12, 12-16. 
       It can NOT process any other way of splitting the plate. 
    8. replace the "dohalfplate = False|True" by self.numTestsPerPlate = [1|2|4]
    9. several other heavily used parameters moved to the class level. 
    10. The processEjectSweepDropCV_FixRange is not changed. 
        It should works the way as it used to but none of the new features. 

5/9/2017:
    Mask the data that has greater than platesettings[plate]['maxstdev'] so that they will not be 
    considered when estimating the bowl 
    Grouping so tha 1 CF and 1 T2T for SP, B2 and CP       

        


8/9/2017:
   AVDB:
   Refactor to streamline code especially in terms of useInternalStd
    
   Here is how the x-range can be set:
      Option 1: Read in a picklist ( readPickListFile )
      Option 2: Use predefined arrays: ( e.g. genPickListMtrxFromArray(self.xrange) )
      Option 3: Set start stop and step: ( setXrange(..) )
   Internally this will be converted in a matrix with dB values per dest well
   If internal std is used the arrays should only have 23 entries.   
    
12/8/2017:
 AVDB:
  
"""

## \brief Methods to process EjectSweep data and calculate bowl width
#

# see https://blogs.law.harvard.edu/rprasad/2014/06/1W6/reading-excel-with-python-xlrd/

import xlrd
import numpy as np
import matplotlib.pyplot as plt
import os
from collections import namedtuple
import pandas as pd
import matplotlib.gridspec as gridspec
from ..DropCV import ReaderDat
import fnmatch
from collections import defaultdict


class processEjectSweep():
    np.set_printoptions(threshold=np.nan)
    QuadStat = namedtuple('QuadStat','Sheet Q Vol StD') 
    xrange_tswap = [-0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.3, -0.2, -0.2, -0.1, -0.1, 0.0, 0.0, 0.1, 0.1, 0.2, 0.2, 0.3, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    xrange_tswap_IntStd = [-0.7, -0.6, -0.5, -0.4, -0.3, -0.3, -0.2, -0.2, -0.1, -0.1, 0.0, 0.0, 0.1, 0.1, 0.2, 0.2, 0.3, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    xrange_cct = [-1.4, -1.3, -1.2, -1.1, -1, -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
#    xrange_cct = [-0.8, -0.73, -0.66, -0.59, -0.52, -0.45, -0.38, -0.31, -0.24, -0.17, -0.1, -0.03, 0.04, 0.11, 0.18, 0.32, 0.39, 0.46, 0.53, 0.6, 0.67, 0.74, 0.81]
    plates = [ '384PP_DMSO2', '384LDV_DMSO', '384LDVS_DMSO', '384LDVS_AQ_B2', '384LDV_AQ_B2', '1536LDV_DMSO', '1536LDVS_DMSO', '384PP_AQ_CP', '384PP_AQ_GP2', '384PP_AQ_BP2', '384PP_AQ_SP2']
    plates += [ '384PPG_DMSO2', '384PPG_AQ_GP2', '384PPG_AQ_CP', '384PPG_AQ_BP2', '384PPG_AQ_SP2' ]
    plates += [ '384PPL_DMSO2', '384PPL_AQ_GP2', '384PPL_AQ_CP', '384PPL_AQ_BP2', '384PPL_AQ_SP2' ]
    plates += ['96TR_DMSO', '96TRX_DMSO', '96TRK_DMSO', '96TR_SP', '96TRX_SP', '96TR_AQ_SP', '96TRK_AQ_SP', '96TR_GP', '96TRX_GP', '96TR_AQ_GP', '96TRK_AQ_GP']
    markerlist=['o','s','^','v','<','>','d','p','H','*','h','8','x','+']
    markercolor=['b', 'g', 'r', 'c', 'm', 'y', 'k','hotpink','fuchsia','sage','azure','slategray','tan'] 
        
    def __init__(self):
        

        self.xrange = self.xrange_tswap
        self.verbose = False
        self.CFAdjustThreshold = 0.03
        self.ncols=24
        self.nrows=16
        self.ylo = 20
        self.yhi = 35
        self.workDir = ""
        self.numTestsPerPlate = 1
        self.UseInternalStd = False
        self.readertype = 'Biotek2'
        self.readercal = ''
        self.platesettings = self.genDefaultPlateSettings()    
        self.picklistdB = None  #It is a 16x24 np array with T2T values
        self.genDefaultPickListDbMatrix() #create default self.picklistdB
        self.platetype = "none"
        self.xtickstepsize = 0.2
        print(' ======================================================================= ')
        print(' =  NOTE:: THIS CODE IS DEPRECATED                                     = ')
        print(' =    please use ejectSweepAnalysis and/or processEjectSweep instead   =' )
        print(' =       processEjectSweep:: preserves functionality from EjectSweep   =' )
        print(' =       ejectSweepAnalysis:: bowl recognition code                    =' )
        print(' =======================================================================' )
        
        
    def genDefaultPlateSettings(self):
        platesettings = {}
        for plate in self.plates:
            platesettings[plate] = {}
            platesettings[plate]['maxvolfrac'] = 0.05
            platesettings[plate]['wallofdeath_adjust'] = -0.3
            platesettings[plate]['dd_threshold'] = 0
            platesettings[plate]['checkmark_adjust'] = 0.1
            platesettings[plate]['minvolindx'] = 3 #skip the number of data from the left
            platesettings[plate]['maxstdev'] = 3 #exclude points with stdev greater than it

            if 'DMSO' in plate:
                platesettings[plate]['nominalvolume'] = 25
            if ('DMSO' in plate) and not ('TR' in plate):
                platesettings[plate]['nominalvolume'] = 50
                platesettings[plate]['maximumslope'] = 0.4 
                platesettings[plate]['wallofdeath_threshold'] = 3.5
                platesettings[plate]['checkmarkwidth_threshold']  = 0.2
            else:
                platesettings[plate]['nominalvolume'] = 50
                platesettings[plate]['maximumslope'] = 0.8 
                # turn off wall of death settings for omics
                platesettings[plate]['wallofdeath_threshold'] = 100
                # turn off checkmark settings for omics
                platesettings[plate]['checkmarkwidth_threshold']  = 0.0
            # overrides:
            #if ( 'DMSO' in plate ) and ('384LDV' in plate) :        
            #    platesettings[plate]['dd_threshold'] = -0.05        
            #    platesettings[plate]['wallofdeath_adjust'] = -0.4    
            if ( 'DMSO' in plate ) and ( '1536LDV' in plate ):    
                platesettings[plate]['minvolindx'] = 7
            if ( 'DMSO' in plate ) and ( '384PP' in plate ):  
                platesettings[plate]['minvolindx'] = 6
                platesettings[plate]['maxstdev'] = 1.5
                platesettings[plate]['dd_threshold'] = -0.2
            if ( 'CP' in plate ):
                platesettings[plate]['minvolindx'] = 7
                platesettings[plate]['maxstdev'] = 1.5
            if ( 'SP2' in plate ):
                platesettings[plate]['maxstdev'] = 1.5
            if ('BP2' in plate ):
                platesettings[plate]['dd_threshold'] = -0.5 
            
        
        return platesettings

    def genDefaultPickListDbMatrix(self):
        #UseInternalStd is handled in function calcStats(...) by changing self.picklistdB 
        self.picklistdB = np.array([self.xrange_tswap for _ in range(16)])
        self.xrange = self.xrange_tswap_IntStd if self.UseInternalStd else self.xrange_tswap

        if (self.UseInternalStd):
            self.genPickListMtrxFromArray(self.xrange_tswap_IntStd)
        else:    
            self.genPickListMtrxFromArray(self.xrange_tswap) 
        return

    def genPickListMtrxFromArray(self, array):
        self.picklistdB = np.array([array for _ in range(16)])
        self.xrange = array
        return


    def validatePlateTypeDict(self, platetype):
        valid = True
        testkeys = ['minvolindx','checkmark_adjust', 'checkmarkwidth_threshold','dd_threshold', 'maximumslope', 'maxvolfrac', 'nominalvolume','wallofdeath_adjust', 'wallofdeath_threshold'] 
        for t in testkeys:
            if t not in platetype.keys():
                valid = False
        return valid        
        
    def printDefaultPlateSettings(self):
        df = pd.DataFrame(self.platesettings)
        print(df)
        return
       
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
                r.append(cell_obj.value)
    #        print('(%s) %s %s' % (idx, cell_type_str, cell_obj.value))
        return r

    def setXrange(self, nsteps=24, startdb=-0.85, stepsize=0.075):
        xrange = []
        for k in range(0,nsteps):
            xrange.append(startdb+k*stepsize)
        self.genPickListMtrxFromArray(xrange)    
        return
 
    def setYRange(self,platetype):
        self.ylo = self.platesettings[platetype]['nominalvolume']*0.8
        self.yhi = self.platesettings[platetype]['nominalvolume']*1.4
        return


    def Statistics2Csv(self, transfername, x, y, ye, cv,Slope, Offset, PMT):
        """
        Output the mean and cv into excel file
        It appends to the existing/old files. So manually delete the 
        file Statistics.csv if appending is not desired. 
        """
        sdata = np.vstack((x,y,ye,cv))
        sdata = np.transpose(sdata)
        sdata = sdata[sdata[:,0].argsort()]

        try:              
            with open(self.workDir + "\\EjectSweep_Stats.csv", "a") as statOut:
                statOut.write(transfername + "\n")
                statOut.write("StdCurveSlope = %f, StdCurveOffset = %f, PMTCorr = %f\n"%(tuple((Slope, Offset, PMT))))
                statOut.write("dB, mean, std, cv, readerSlope, readerOffset\n")
                for r in sdata:
                    statOut.write("%f, %f, %f, %f\n"%tuple(r))
        except Exception as error:
             print("Error opening file EjectSweep_stats.csv for writing in folder ", self.workDir)
             return        

    def transferFile2SquareCSV(self, adcherryPickList):
        """
        Convert a picklist file that is used by ADCherryPick to 
        a rectangle csv file that can be used by the EjectSweep.py
        """
        with open(adcherryPickList, "r") as inf:
            lines = inf.readlines()
        lines = lines[1:]
        #assert(len(lines) == 384), "wrong size of input"
        
        #T2T corresponds to destination plate wells
        square = [[float('inf')]*24 for r in range(16)]
        #square = [[1.5]*24 for r in range(16)]
        for L in lines:
            Ls = L.split(",")        
            w = Ls[1].strip()
            r = ord(w[0]) - ord("A")
            c = int(w[1:]) - 1
            t2t = Ls[3]
            square[r][c] = float(t2t)
                
        with open(self.workDir + "\\used_rectangle_pick_list.csv", "w") as outf:
            for r in square:
                outf.write(",".join([str(ri) for ri in r]) + "\n")
        
        square = np.array(square)
        return(square)

 
    #def processEjectSweepRawReader_FixRange(self,readerfilelist, numTestsPerPlate = 1, reader='Biotek2', cal='042016', UseInternalStd = False):
    def processEjectSweepRawReader_FixRange(self,readerfilelist):
        """Processes Raw BioTek reader data and returns a numpy array and list of sheets that contain reader data
         Input Arguments:
           filelist -- all files to process, these would be individual reader files, including matech files 
           numTestsPerPlates -- 1 | 2 | 4 :: number of different fill volumes or fluids per plates ( organized per row)
           reader   -- reader used to read transferred plates
           cal      -- calibration date of reader
           """  
        #self.numTestsPerPlate = numTestsPerPlate
        r = ReaderDat.ReaderDat();
        r.setStdCurve(self.readercal,self.readertype,self.UseInternalStd); 
        print(' ---- Std Curve Slope :: ', r.StdCurveSlope, ' Offset :: ', r.StdCurveOffset, ' ---- ')
        
        useMatech = not self.UseInternalStd
        #self.xrange = self.xrange_tswap_IntStd if self.UseInternalStd else self.xrange_tswap

        
        csv_or_xls = '.csv' if self.readertype.lower() == 'bmg' else '.xls'
        readerfiles = [f for f in readerfilelist if f.endswith(csv_or_xls)]
        matechfiles = [ f for f in readerfiles if 'matech' in f.lower()]  
        for m in matechfiles: readerfiles.remove(m) 
        
        if (useMatech): 
            assert(len(matechfiles) == 2), ' **** ERROR **** : need exactly 2 matech files but found: %d'%len(matechfiles)
            r.setPMTCorr(matechfiles[0],matechfiles[1]);
            print(' ---- PMT Correction:: ', r.StdCurvePMTCorr, ' ---- ')   
        assert(len(readerfilelist) >= 1), ' **** ERROR **** : No reader files found'
        

        xunique = set(self.xrange)
        if float('inf') in xunique: xunique.remove(float('inf'))
        transfernames = []
        transfername_posFix = [[""] for _ in range(5)]
        transfername_posFix[2] = ['_top', '_bot']
        transfername_posFix[4] = ["_T1","_T2", "_T3","_T4"]  #1/4 plate
    
        alldat = np.empty([4*len(readerfiles)*self.numTestsPerPlate,len(xunique)])
        nrows = ( len(readerfiles)+1)//2
        ncols = 2
        if ( nrows == 1) :
            nrows += 1
        fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(18*ncols,12*nrows))
     #   ax[-1][-1].axis('off')
     #   print( ' nrows : ', nrows, ' ncols: ' , ncols)
        rind = 0
        colind = 0
        for i in range(0,len(readerfiles)):
            dr = r.processReaderFile(readerfiles[i], 24, 16); 
            dc = r.applyCalCurve(dr); 
            r.plotReaderDat(dc,r.getPrintStats(dc), ax=ax[rind][colind], title=os.path.split(readerfiles[i])[-1])
            colind += 1
            if colind > 1:
                colind = 0
                rind += 1
            if (self.UseInternalStd):
                dc = np.delete(dc, r.InternalRefCol, 1)	
                print(' ---- PMT Correction:: ', r.StdCurvePMTCorr, ' ---- ') 
            dc_f = np.ma.masked_outside(dc,r.EmptyThresh,r.OverFlVol)

            if self.verbose:
                print(' shape(dc_f): ', dc_f.shape )	              


            for k in range(0,self.numTestsPerPlate):
                startRow = 0+k*(self.nrows//self.numTestsPerPlate)
                stopRow = (k+1)*(self.nrows//self.numTestsPerPlate)
                y, ye, x, cv = self.calcStats(dc_f, startRow, stopRow) 

                alldat[0+i*4*self.numTestsPerPlate+k*4] = x 
                alldat[1+i*4*self.numTestsPerPlate+k*4] = y
                alldat[2+i*4*self.numTestsPerPlate+k*4] = ye
                alldat[3+i*4*self.numTestsPerPlate+k*4] = cv

                transfername = os.path.basename(readerfiles[i]).split(csv_or_xls)[0]
                transfername += transfername_posFix[self.numTestsPerPlate][k]
                transfernames.append(transfername)

                
                readerPMT.append(r.StdCurvePMTCorr)
                
                self.Statistics2Csv(transfername, x, y, ye, cv, r.StdCurveSlope, r.StdCurveOffset, r.StdCurvePMTCorr)

        try:        
            plt.savefig('Readerdat.png')            
        except Exception as error:
            print('Can\'t save figure to file "Readerdat.png" in folder ', os.getcwd())
        return alldat, transfernames, readerPMT    

     
  
    
    def processEjectSweepDropCV_FixRange(self, filename, numTestsPerPlate=1 ):
        """Processes BioTek reader data and returns a numpy array and list of sheets that contain reader data
         Input Arguments:
           filename -- 
           ncols    -- number of destination columns to process, typically 24 (for 384 well dest plate)
           """  
           
        xlfile = self.openXLbook(filename)
        sheets = xlfile.sheet_names()
        valuesheets = []
        for i,val in enumerate(sheets):
            if val.endswith('_grf'):
                i += 1
                valuesheets.append(sheets[i])
        startrow = 43
        startcol = 2
        nrows = self.nrows
        xunique = set(self.xrange)
        if (numTestsPerPlate==2):
            multiplier = 2
        else :
            multiplier = 1
        sheetnames = []    
        alldat = np.empty([4*len(valuesheets)*multiplier,len(xunique)])
        for i in range(0,len(valuesheets)):
            print('Processing sheet ', valuesheets[i])          
            xlsheet =  xlfile.sheet_by_name(valuesheets[i])          
      
            readerdat = np.empty([nrows,self.ncols])
            for ii in range(0,self.nrows):
                tmp = np.array(self.processRow(xlsheet,startrow+ii,startcol,startcol+self.ncols))
                readerdat[ii] = tmp.astype(np.float)
            readerdat_f = np.ma.masked_outside(readerdat,0.1,100)
            if (self.verbose):
                print(' Calculating stats .. ')
            for k in range(0,multiplier):    
                start = 0+k*(nrows//multiplier)
                stop = (k+1)*(nrows//multiplier)
                y, ye, x, cv = self.calcStats_DropCV(readerdat_f[start:stop,:], self.xrange, False, start, stop)
            
                if (self.verbose):
                    print('  .. done ')
                    fig = plt.figure()
                    ax = fig.add_subplot(1, 1, 1)
                    ax.grid()
                    plt.errorbar(x, y, yerr=ye,marker='o',mfc='red',ls='None') 
                    plt.xlabel('Scale (dB)')
                    plt.ylabel('Volume (nL)')
                    ax.set_ylim(self.ylo,self.yhi)
                    ax.set_title(valuesheets[i])
                    #plt.show()
           
                alldat[0+i*4*multiplier+k*4] = x 
                alldat[1+i*4*multiplier+k*4] = y
                alldat[2+i*4*multiplier+k*4] = ye
                alldat[3+i*4*multiplier+k*4] = cv
                
                if (numTestsPerPlate==2):
                    if k==0:
                        sheetnames.append(valuesheets[i]+'_top')
                    else:
                        sheetnames.append(valuesheets[i]+'_bot')
                else:
                    sheetnames.append(valuesheets[i])

        if (self.verbose):    
            print(' ... done with FixRange .. ')    
        return alldat, sheetnames    


    def readPickListFile(self, pickListFilename = None):
        """
        if there is picklist file in the workdir, read it. 
        Otherwise, use the default standard one, i.e., do nothing here
        return True if successfully read a picklist file
        return False will use default picklist
        """

        #scan folder for picklistfilename  
        if ( not pickListFilename  ):
            if "" != self.workDir:
                tmplst =[f for f in os.listdir(self.workDir) if ("picklist" in f.lower())]
                tmplst =[f for f in tmplst if os.path.isfile(self.workDir+"\\"+f)]
                if len(tmplst) == 1:
                    pickListFilename = os.path.join(self.workDir, tmplst[0])
                    #print("pickListFilename", pickListFilename)
                elif len(tmplst) > 1:
                    print("\n\n*****************")
                    print("Warning: found more than one possible picklist files")
                    print("         Only one is allowed.")
                    print("         Not using picklist file at all")
                    print("         will use default standard picklist")
                    print("*****************")

        if pickListFilename and pickListFilename[-3:] == "csv":
            with open(pickListFilename, "r") as inf:
                firstLine = inf.readline()
            
            pickList = None
            firstItem = firstLine.split(",")[0]
            if firstItem.lower().strip() == "source":

                pickList = self.transferFile2SquareCSV(pickListFilename, self.UseInternalStd)

            else:
                try:
                    float(firstItem)
                    pickList = np.genfromtxt(pickListFilename, delimiter=',')                        
                except:
                    print("unknown picklist file")       

                    print(" ---- using default standard picklist file:")

                    self.genDefaultPickListDbMatrix()
                    return False
            print(" ---- use picklist file:")
            print("      " + "\n          ".join(pickListFilename.rsplit("\\", 1)) +"\n")
            self.picklistdB = pickList
            self.xrange = list(np.unique(pickList))
            return True
        else:
            print(" ---- use default standard picklist file:")
            self.genDefaultPickListDbMatrix()
            return False


    def calcStats(self, readerdat_fin, startRow=0, endRow=16):
            """Helper function that calculates column statistics for EjectSweeps
               readerdat_f -- typically  (16,24) array -- note that internalstd columns should be removed
               xrange    -- a list containing the x-values of the sweep in dB
               verbose  -- If True visualize the data 
            """       
            #readerC = ReaderDat.ReaderDat()

            
            local_picklistdB = self.picklistdB[startRow:endRow, :]
            readerdat_f = readerdat_fin[startRow:endRow, :]
            
            if self.verbose: #
                for r in self.picklistdB:
                    for c in r:
                        print("{:.2f}".format(c), end = ",")
                    print()
           
            errmsg = "Error! reader data and picklist data have difference dimensions\n"
            errmsg += "readerdat_f.shape: " + str(readerdat_f.shape) + "\n"
            errmsg += "local_picklistdB.shape" + str(local_picklistdB.shape) + "\n"
            assert(readerdat_f.shape == local_picklistdB.shape), errmsg


            # A list is created here where each key is a value in dB, 
            # the values are an array of reader volumes

            xAndvol = defaultdict(list)
            rows, cols = readerdat_f.shape
            for r in range(rows):
                for c in range(cols):

                    if "nan" != readerdat_f[r, c]:
                        xAndvol["%.2f"%(local_picklistdB[r,c])] += [readerdat_f[r, c]]
                    elif len(xAndvol["%.2f"%(local_picklistdB[r,c])]) == 0:
                        xAndvol["%.2f"%(local_picklistdB[r,c])] += [0]

            y, ye, x, cv = [], [], [], [] # np.array

            for key, lst in xAndvol.items():
                if lst != []:
                    val = np.array(lst)
                    mean = np.mean(val[:])
                    ste = np.std(val[:])
                    cvval = np.std(val[:])
                    n = (val.shape)[0]
                    cvval /= mean
                    ste /= np.sqrt(n)
    
                    x.append(float(key))               
                    y.append(mean)
                    ye.append(ste)
                    cv.append(cvval)

            y = np.array(y)
            ye = np.array(ye)
            x = np.asarray(x)   
            cv = np.array(cv)       
            return y, ye, x, cv  
            


    def estimateBowl(self, ejectsweepdat, index, thisplatetype):
        if not (self.validatePlateTypeDict(thisplatetype)):
            print(" Error::: invalid plate dictionary :: ", thisplatetype)
            return 0
        d = np.zeros([len(ejectsweepdat[index*4]),3],dtype=float)
        for j in range(0,len(ejectsweepdat[index*4])):
            for i in range(0,3):
                d[j,i] = ejectsweepdat[index*4+i][j]
        ee = d[np.lexsort(np.fliplr(d).T)]  
        der = np.gradient(ee[:,1])
        maxslope = thisplatetype['maximumslope']
        volfrac = thisplatetype['maxvolfrac']
        ddthresh = thisplatetype['dd_threshold']
        if (self.verbose):
            print(' -- estimating bowl based on change in volume (first derivative), maxslope: ', maxslope )
            print('   first derivative ::', der)
     #estimate minimum volume   
        minv = thisplatetype['minvolindx']    
        #print(' STDEV:: ', ee[:,2]) 
        mask1 = np.empty(ee.shape,dtype=bool)
        mask1[:,:] = (ee[:,2] >= thisplatetype['maxstdev'])[:,np.newaxis]
        ee_masked = np.ma.MaskedArray(ee,mask=mask1)
        
        minvolidx = minv + np.argmin(ee_masked[minv:len(der)-minv,1])
    # analyze bowl based on slope
        rr = np.argmax(abs(der[minvolidx:])>maxslope)
        if (rr > 0 ):
            rrs = minvolidx + rr
        else:
            #code prior to edit on 8/3/2016 by EZ
            # rrs = len(dr)  
            #edit
            rrs = len(der) - 1
        ll = np.argmax(abs(der[minvolidx::-1])>maxslope)
        if ( ll > 0 ):
            lls = minvolidx -  ll
        else:
            lls = 0
        if (self.verbose):    
            print('  ******  bowl (based on slope): ', lls, ' - ', rrs, ' around idx = ', minvolidx, ' (vol = ', ee[minvolidx,1], ')' )
            print('')
            print(' -- estimating bowl based on absolute volume, volume frac of minimum: ', 1+volfrac )
    # analyze bowl based on volume:
        vols = ee[:,1]  
        maxvol = ( 1 + volfrac)*vols[minvolidx]
        rr = np.argmax(vols[minvolidx:]>maxvol)   
        if (rr > 0):
            rrv = minvolidx + rr
        else:
            #code prior to edit on 8/3/2016 by EZ -see also BZ 12503
            #rrv = len(dr)  
            #edit
            rrv = len(der) - 1
        ll =  np.argmax(vols[minvolidx::-1]>maxvol) 
        if (ll > 0):
            llv = minvolidx - ll
        else:
            llv = 0
        if (self.verbose):
            print('  volumes ::', vols)
            print('  ******* bowl  (based on volume): ', llv, ' - ', rrv, ' around idx = ', minvolidx, ' (vol = ', ee[minvolidx,1], ', maxvol = ', maxvol, ')' )
        #leftbowlidx = np.argmax(abs(dr)<maxslope)
        #rightbowlidx = len(dr) - np.argmax(abs(dr[::-1])<maxslope) - 1
        derder = np.gradient(der)   
        if (self.verbose):
            print('')
            print(' -- estimating bowl based on 2nd derivative   -- ')
            print(' 2nd derivatives :: ', derder)
        ddrr = np.argmax(derder[minvolidx:]<ddthresh)
        if (ddrr > 0 ):
            ddrrs = minvolidx + ddrr
        else:
            #code prior to edit on 8/3/2016 by EZ
            # rrs = len(dr)  
            #edit
            ddrrs = len(derder) - 1
        ddll = np.argmax(derder[minvolidx::-1]<ddthresh)
        if ( ddll > 0 ):
            ddlls = minvolidx -  ddll
        else:
            ddlls = 0
        if (self.verbose):    
            print('  ******  bowl (based on 2nd der): ', ddlls, ' - ', ddrrs, ' around idx = ', minvolidx, ' (vol = ', ee[minvolidx,1], ')' )
        
        rightbowlidx = np.min([rrv,rrs,ddrrs])
        leftbowlidx = np.max([llv,lls,ddlls])
        bowlwidth = ee[rightbowlidx,0] - ee[leftbowlidx,0]
        return [ leftbowlidx, rightbowlidx, bowlwidth ], ee

    def plotBowls(self, ejectsweepdat,plotname,readerPMT,thisplatetype,ti='BowlEstimate',basedir="./"):
        if not (self.validatePlateTypeDict(thisplatetype)):
            print(" Error::: invalid plate dictionary :: ", thisplatetype)
            return 0
        fig = plt.figure()
        if (self.verbose):
            print( ' len(ejectsweepdat) : ' , len(ejectsweepdat))
        nplots = len(ejectsweepdat)//4 # nr of plots
        nrows = (nplots+1)//2
        # Lame way of dealing with trouble of having only one row
        if (nrows == 1):
            nrows += 1
        ncols = 2     
        fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=(15,3*nrows))
        gs = gridspec.GridSpec(nrows, 3*ncols)
      #  gs.update(hspace=0.1)
        
        axlist = []
        axlist_att = []    
        thisrow = 0;
        colstart = 0;
        colend = 2;
        for ii in range(0,nplots):
            axx = plt.subplot(gs[thisrow,colstart:colend])
            axx_att = plt.subplot(gs[thisrow,colend])
            axx_att.axis('off')
            axlist.append(axx)
            axlist_att.append(axx_att)
            if ( ii%2 ):
                thisrow += 1
                colstart = 0
                colend = 2
            else:
                colstart=3
                colend = colstart+2
        rowcount = 0
        # turn off all axes:
        if (nrows > 1 ):
            axs[-1, -1].axis('off')
        else:
            print(" axes shape: ", axs.shape)
        if (self.verbose):   
            print(" plotname: ", plotname)    
            
        wdeath_thresh = thisplatetype['wallofdeath_threshold'] 
        wdeath_adj = thisplatetype['wallofdeath_adjust']
        checkmarkwidth_thresh = thisplatetype['checkmarkwidth_threshold'] 
        checkmarkwidth_adj = thisplatetype['checkmark_adjust'] 
        nominalvol = thisplatetype['nominalvolume']
        
        alladjusts = []	
        ccc_t2t_cf = []
        for kk in range(0,nplots):
            if (self.verbose):
                print('')
                print(' ------- processing ', plotname[kk], ' -------------- ')
            colcount = kk%2
            if (kk!=nplots):
                csv_wallofdeath = "NaN"
                ytextval = 0.9
                off = kk*4
                axlist[kk].errorbar(ejectsweepdat[off+0], ejectsweepdat[off+1], yerr=ejectsweepdat[off+2], ls='None',marker=self.markerlist[kk%len(self.markerlist)],color=self.markercolor[kk%len(self.markercolor)])
                axlist[kk].set_title(plotname[kk])            
                bowl,sortedvals = self.estimateBowl(ejectsweepdat, kk, thisplatetype)
                bowlcenter = ( sortedvals[bowl[1],0] + sortedvals[bowl[0],0])/2  
                if not ( bowl[1] == ( len(sortedvals)-1 )):
                    wdeathindex = np.argmax(np.gradient(sortedvals[bowl[1]:,1])> wdeath_thresh) 
                    if (self.verbose):
                        print(' gradient -- ' , np.gradient(sortedvals[bowl[1]:,1]))
                        print(' --- checking for wall of death wdeathindex = ' , wdeathindex, ' wdeath_thresh = ', wdeath_thresh, ' wdeath_adj = ', wdeath_adj)
                    # Check for wall of death
                    if (( wdeathindex > 0 ) or (np.gradient(sortedvals[bowl[1]:,1])[0] > wdeath_thresh ) ) and \
                      ((sortedvals[wdeathindex+bowl[1],0] + wdeath_adj ) < sortedvals[bowl[1],0] ):  
                        pstring = " Wall of death at " + str( sortedvals[wdeathindex+bowl[1],0])
                        csv_wallofdeath = str( sortedvals[wdeathindex+bowl[1],0])
                        bowlcenter = sortedvals[wdeathindex+bowl[1],0] + wdeath_adj
                        axlist_att[kk].text(0,ytextval+0.1, pstring) 
                    else:
                        #check for checkmark
                      #  bowlcenter = ( sortedvals[bowl[1],0] + sortedvals[bowl[0],0])/2  
                        bowlwidth = abs(sortedvals[bowl[0],0] - sortedvals[bowl[1],0])
                        volatbowlcenter = np.interp(bowlcenter,sortedvals[:,0],sortedvals[:,1])
                        volleft = np.interp(bowlcenter-0.2,sortedvals[:,0],sortedvals[:,1])
                        volright = np.interp(bowlcenter+0.2,sortedvals[:,0],sortedvals[:,1])
                        if (self.verbose):
                            print( ' --- checking for checkmark - bowlwidth : ', bowlwidth, ' volatcenter: ', volatbowlcenter, ' checkmarkwidth:',  checkmarkwidth_thresh)
                        if ( abs(bowlwidth - checkmarkwidth_thresh) < 0.01 ):
                            if ( volleft > volatbowlcenter*1.01 ) and ( volright > volatbowlcenter*1.01 ) :
                                pstring = " Checkmark at  " + str( bowlcenter ) 
                                if (self.verbose):
                                    print(' ---- Checkmark found at ', bowlcenter, ' bowlwidth = ', bowlwidth)
                                bowlcenter -= checkmarkwidth_adj
                                axlist_att[kk].text(0,ytextval+0.1, pstring) 
                        
           
                axlist_att[kk].text(0,ytextval,' Bowl Range :: ' + str(sortedvals[bowl[0],0]) + '-' + str(sortedvals[bowl[1],0]) )
                axlist_att[kk].text(0,ytextval-0.1,' Bowl Center :: ' + str( bowlcenter ))
                volatbowlcenter = np.interp(bowlcenter,sortedvals[:,0],sortedvals[:,1])
                pstring = "{:.2f}".format(volatbowlcenter)
                axlist_att[kk].text(0,ytextval-0.2,' Bowl Cent V :: ' + pstring)
                pstring = "{:.2f}".format(sortedvals[bowl[0]:bowl[1],1].std())
                axlist_att[kk].text(0,ytextval-0.3,' Bowl Std       :: ' + pstring) 
                pstring = "{:.2f}".format(sortedvals[bowl[0]:bowl[1],1].mean())
                axlist_att[kk].text(0,ytextval-0.4,' Bowl Mean V  :: ' + pstring) 
                pstring = "{:.2f}".format(sortedvals[len(sortedvals)//2,1])
                axlist_att[kk].text(0,ytextval-0.5,' Vol at 0 dB    :: ' + pstring)
                pstring = "{:.2f}".format(readerPMT[kk])
                axlist_att[kk].text(0,ytextval-0.6,' PMT    :: ' + pstring)
               
                pstring ="{:.2f}".format(self.round_nearest(bowlcenter,0.05))        
                t2tdelta = pstring
                axlist_att[kk].text(0,ytextval-0.8, 'T2T:: ' + pstring, fontweight='bold')
                if abs( volatbowlcenter/nominalvol - 1 ) < self.CFAdjustThreshold :
                    CFAdjust = 0
                else:    
                    CFAdjust = -(1-volatbowlcenter/nominalvol)*100*0.05
                pstring ="{:.2f}".format(self.round_nearest(CFAdjust,0.05))
                cfdelta = pstring
                axlist_att[kk].text(0,ytextval-0.9, 'CF :: ' + pstring + ' MHz', fontweight='bold')
                #ax2=axes[rowcount,colcount].twinx()
                ax2=axlist[kk].twinx()
                ax2.plot(sortedvals[:,0],np.gradient(sortedvals[:,1]),color='r',marker='.')
                ax2.plot(sortedvals[:,0],np.gradient(np.gradient(sortedvals[:,1])),color='m');
                ax2.set_ylim(-5,5)
                ax2.grid()
                ax2.set_ylabel('Gradient (nL/dB)')
                plt.axvspan(sortedvals[bowl[0],0], sortedvals[bowl[1],0], facecolor='lightgray', alpha=0.5)

                csv_BowlRange_L = "{:.2f}".format(sortedvals[bowl[0],0])
                csv_BowlRange_R = "{:.2f}".format(sortedvals[bowl[1],0]) 
                csv_BowlCenter = "{:.2f}".format(bowlcenter)
                csv_BowlCentVol = "{:.2f}".format(volatbowlcenter)
                csv_Bowl_Std = "{:.2f}".format(sortedvals[bowl[0]:bowl[1],1].std())
                csv_BowlMeanValue = "{:.2f}".format(sortedvals[bowl[0]:bowl[1],1].mean())
                csv_VolAt0DB = "{:.2f}".format(sortedvals[len(sortedvals)//2,1])
                thisdata = [ plotname[kk], t2tdelta, cfdelta, t2tdelta, cfdelta, t2tdelta, cfdelta]
                thisdata += [csv_wallofdeath]
                thisdata += [csv_BowlRange_L, csv_BowlRange_R, csv_BowlCenter]

                thisdata += [csv_BowlCentVol, csv_Bowl_Std, csv_BowlMeanValue, csv_VolAt0DB, readerPMT[kk]]

                
                if abs(float(cfdelta)) > 0.3:
                    thisdata[2] = "NaN"
                    thisdata[4] = "NaN"
                
                #used to deal with grouping T2T and CP for CP, B2 and SP2
                ccc = plotname[kk].split("_", 1)[0]
                ccc_t2t_cf.append([ccc, t2tdelta, thisdata[2], csv_BowlRange_L, csv_BowlRange_R])
                
                alladjusts.append(thisdata)
            else:    
                
                for k in range(0,nplots):
                    off = k*4
                    labelname = plotname[k].rsplit('_')[0]
                    axlist[kk].errorbar(ejectsweepdat[off+0], ejectsweepdat[off+1], yerr=ejectsweepdat[off+2],ls='None',marker=self.markerlist[k%len(self.markerlist)], label=labelname)            
                axlist[kk].set_title(ti)
                axlist[kk].axis('on')
                  # Shrink current axis by 20%
                box = axlist[kk].get_position()
                axlist[kk].set_position([box.x0, box.y0, box.width * 0.8, box.height])
                # Put a legend to the right of the current axis
                axlist[kk].legend(numpoints=1, loc='center left', bbox_to_anchor=(1, 0.5))
     
            axlist[kk].grid()  
            axlist[kk].set_ylim(self.ylo,self.yhi)
            start, end = axlist[kk].get_xlim()
            # steps of 0.2 dB
            axlist[kk].xaxis.set_ticks(np.arange(start, end, self.xtickstepsize))
            axlist[kk].set_xlabel('Scale (dB)')
            axlist[kk].set_ylabel('Volume (nL)')
            if (colcount==1):
                rowcount += 1
                
      
      # this statement messes up the drawing of the legend          
        fig.subplots_adjust(hspace=0.55, wspace=0.4)
    #    ax.legend()
        #plt.show()
        fi = plt.gcf()
    #    print("Current working dir: ", os.getcwd(), "saving to ", basedir)

        try:
            file = basedir + "\\" + ti + '_bowl.png'
            fi.savefig(file,bbox_inches='tight')
            file = basedir + "\\" + ti + '_bowl.svg'
            fi.savefig(file,bbox_inches='tight')
        except Exception as error:
            print('Can\'t write to file ', ti, '_bowl* in folder ', basedir)
        #plt.show()


        cf_group = "none"
        t2t_group = "none"
        if "_sp" in self.platetype.lower():
            if len(ccc_t2t_cf) != 3: 
                print("!!!! Warning !!!:")
                print("    only %d plates in SP found"%len(ccc_t2t_cf))
            cf_group = ccc_t2t_cf[0][2]
            t2t_group = ccc_t2t_cf[0][1]
            for L in ccc_t2t_cf:
                if "14" in L[0]:
                    cf_group = L[2]
                if "200" in L[0]:
                    t2t_group = L[1]
        if "_b2" in self.platetype.lower():
            cf_group = ccc_t2t_cf[0][2]
            t2t_group = ccc_t2t_cf[0][1]
            meanCF, meanCF_count = 0, 0
            for L in ccc_t2t_cf:
                meanCF += float(L[2])
                meanCF_count += 1
                if "4" in L[0]:
                    t2t_group = L[1]
            cf_group ="{:.2f}".format(meanCF / meanCF_count)
        if "_cp" in self.platetype.lower():
            bowl_width = 10
            cf_group = "0"
            t2t_group = ccc_t2t_cf[0][1]
            lmax, rmin = -10, 10
            for L in ccc_t2t_cf:
                tmp_Left = float(L[3])
                tmp_Right = float(L[4])
                
                lmax = max(lmax, tmp_Left)
                rmin = min(rmin, tmp_Right)
                
                if bowl_width > (tmp_Right - tmp_Left):
                    bowl_width = tmp_Right - tmp_Left
                    t2t_group = L[1]
            if not (lmax < float(t2t_group) < rmin):
                #There is no good range of bowl range that fit all plates
                if rmin >= lmax:
                    t2t_group = "{:.2f}".format((rmin + lmax)/2)
                else:
                    t2t_group = "NaN"

        if cf_group != "none" or t2t_group != "none":            
            for i in range(len(alladjusts)):
                alladjusts[i][1] = t2t_group
                alladjusts[i][3] = t2t_group
                alladjusts[i][2] = cf_group
                alladjusts[i][4] = cf_group

        colnames = ['concentration']
        colnames += ['T2T adjust','CF adjust','T2T suggested','CF suggested','T2T individual','CF individual']
        colnames += ['Wall of Death', 'Bowl Range Left', 'Bowl Range Right', 'Bowl Center dB']

        colnames += ['Bowl Center Vol', 'Bowl Std', 'Bowl Mean Value', 'Vol at 0 dB', 'PMTCorr']

        alladjusts_df = pd.DataFrame(alladjusts)
        alladjusts_df.columns=colnames
#        if self.verbose:
#            print(alladjusts_df)

        return alladjusts_df

    def plotEjectSweep(self, ejectsweepdat,plotname,ti='EjectSweep',basedir="./"):
        """ takes a numpy array generated by processEjectSweepDropCV and makes a figure of all data
        Automatically stores the plots in a svg and a png file     
        Input Arguments:
          ejectsweepdat  -- DataSet (numpy array)
          ti             -- Title of the plot
          basedir        -- Directory where to store files
        """  
        
        fig = plt.figure()
        if (self.verbose):
            print( ' len(ejectsweepdat) : ' , len(ejectsweepdat))
        nplots = len(ejectsweepdat)//4 # nr of plots
        nrows = (nplots+2)//2
        # Lame way of dealing with trouble of having only one row
        if (nrows == 1):
            nrows += 1
        fig, axes = plt.subplots(nrows=nrows, ncols=2, figsize=(6,3*nrows))
        
        rowcount = 0
        # turn off all axes:
        if (nrows > 1 ):
            axes[-1, -1].axis('off')
        else:
            print(" axes shape: ", axes.shape)
        if (self.verbose):
            print(" plotname: ", plotname)    
        for kk in range(0,nplots+1):
            colcount = kk%2
            if (kk!=nplots):
                off = kk*4
                axes[rowcount,colcount].errorbar(ejectsweepdat[off+0], ejectsweepdat[off+1], yerr=ejectsweepdat[off+2], ls='None',marker=self.markerlist[kk%len(self.markerlist)],color=self.markercolor[kk%len(self.markerlist)])
                axes[rowcount,colcount].set_title(plotname[kk])
            else:    
                for k in range(0,nplots):
                    off = k*4
                    labelname = plotname[k].rsplit('_')[0]
                    axes[rowcount,colcount].errorbar(ejectsweepdat[off+0], ejectsweepdat[off+1], yerr=ejectsweepdat[off+2],ls='None',marker=self.markerlist[k%len(self.markerlist)], label=labelname)
                axes[rowcount,colcount].set_title(ti)
                axes[rowcount,colcount].axis('on')
                  # Shrink current axis by 20%
                box = axes[rowcount,colcount].get_position()
                axes[rowcount,colcount].set_position([box.x0, box.y0, box.width * 0.8, box.height])
                # Put a legend to the right of the current axis
                axes[rowcount,colcount].legend(numpoints=1, loc='center left', bbox_to_anchor=(1, 0.5))
            
            axes[rowcount,colcount].grid()  
            axes[rowcount,colcount].set_ylim(self.ylo,self.yhi)
            axes[rowcount,colcount].set_xlabel('Scale (dB)')
            axes[rowcount,colcount].set_ylabel('Volume (nL)')
            if (colcount==1):
                rowcount += 1
         
        fig.subplots_adjust(hspace=0.6, wspace=0.4)
        fi = plt.gcf()
        file = basedir + "\\" + ti + '.png'
        fi.savefig(file,bbox_inches='tight')
        file = basedir + "\\" + ti + '.svg'
        fi.savefig(file,bbox_inches='tight')
        plt.close()
        return


    def LoopEcho(self):
        """ Master function that will process all sweeps in all DataSystem_ folders """
        filelist = self.getSweepFileList()
        if not filelist:
            print("No relevant files were detected.\nCheck that you have set the working directory appropriately.")
            return
        self.processEjectSweep(filelist)
        return
    
    
    def getSweepFileList(self):
        """ Get a list of all DropCV_EJECT or DropCV_Eject *xls files in all DataSystem_ subfolders 
        Operates on the current working directory.
        Returns a filelist"""
        curdir = os.getcwd()
        filelist = []
        for i in os.listdir(curdir):
            #print(i)
            if os.path.isdir(i) and ((i.startswith('DataSystem_')) or (i.startswith('384PP') or i.startswith('384LDV') or i.startswith('1536LDV') )):
               #     print(i)
                thisdir = curdir  + "\\" +  i
                vlist = os.listdir(thisdir)
                for k in vlist:
                    if (k=="Ejectsweep"):
                        workdir = thisdir + "\\" + k
                        for ll in os.listdir(workdir):
                            if (ll.startswith('DropCV_EJECT') or ll.startswith('DropCV_Eject') ) and ll.endswith('.xls'):
                                valfile = workdir + "\\" + ll
                                filelist.append([valfile,ll,workdir])
     #   print(filelist)
        return filelist 
    
    def processEjectSweep(self, filelist, numTestsPerPlates=False):
        """ Processes Eject Sweep DropCV; makes figures and writes them to disk. 
        Operates on current working directory
        Input Arguments:
          filelist -- list of DropCV files to be processed, full paths are needed since the DMSO/Omics distinction is made based on filepath'
          numTestsPerPlates -- for sweeps of plates where top half is one concentration or volume, and bottom half another  
          """    
        for ii,val in enumerate(filelist):
            if len(val) != 3:
                fullfilename = val
                filename = os.path.basename(val)
                filepath = os.path.dirname(val)
                if not filepath:
                    filepath=os.getcwd()
            else:
                fullfilename = val[0]
                filename = val[1]
                filepath = val[2]
            
            platetype  = self.getPlateType(filepath) 
            if (not platetype):
                print (" no known platetype identified in foldername : ", filepath)
                continue
            print("Processing plate", platetype, " - file", fullfilename)
            self.setYRange(platetype)
            self.workDir = filepath
            ejectsweepdat, sweeplist = self.processEjectSweepDropCV_FixRange(fullfilename, numTestsPerPlates)
            if (self.verbose):    
                print (' calling plotEjectSweep ')    
            self.plotEjectSweep(ejectsweepdat,sweeplist,filename,filepath)
            cfadjusts = self.plotBowls(ejectsweepdat,sweeplist, self.platesettings[platetype])
            if '384PP_AQ_SP' in filepath:
                if (self.verbose):
                     print(' -- Averaging for SP -- ' )
                cfadjusts = cfadjusts[cfadjusts['concentration'].str.startswith('14_')]
            cfadjusts.to_csv(filepath +  '//' + filename.replace('.xls','_dBAdjust.csv'), index=False)    
        return            
    
    def getVol(self, sheetname, q=1):
        """ Helper function that extracts average volume and std-dev. Returns a named tuple
        Input Arguments:
           sheetname -- an XLS sheet object
           q         -- quadrant of interest"""
        datarow = 1
        datacol = 23
        if (q > 2):
            datarow += 7
        if ( q%2 == 0 ):
            datacol += 4
        avg = self.processRow(sheetname,datarow,datacol,datacol+1)
        std = self.processRow(sheetname,datarow+1,datacol,datacol+1)
        QS = self.QuadStat(sheetname.name,q,avg[0],std[0])
        return QS
        
    def getQuadrantStats(self,xlsfile):    
        """ Function that extracts drop volume and std. dev across a quadrant. Returns a pandas DataFrame.
        """
        dropcv = self.openXLbook(xlsfile)
        sheets = dropcv.sheet_names()
        valuesheets = []
        for i,val in enumerate(sheets):
            if val.endswith('_grf'):
                i += 1
                valuesheets.append(sheets[i])
                print(sheets[i])  
        allstat = []
        for sheet in valuesheets:
            for i in range(1,5):
                xlsheet = dropcv.sheet_by_name(sheet)
                allstat.append(self.getVol(xlsheet,i))
        dd = pd.DataFrame(allstat, columns=allstat[0]._fields)
        return dd
        
    def getListOfEjectSweepFolders(self,wdir=None):
         """Finds all Ejectsweep folders in all subfolders of cwd. Returns list"""      
         ESFolders = []
         if wdir == None :
             wdir = os.getcwd()
         for root, dirs, files in os.walk(wdir):
             for k in fnmatch.filter(dirs,'EjectSweep'):
                 ESFolders.append(os.path.join(root,k))  
         return ESFolders 


    def processRawEjectSweep(self,filelist, **kwargs):
        #numTestsPerPlate=1, readertype='Biotek2', readercal=None, UseInternalStd = False, CCT= False):

        """ Processes Eject Sweep Raw Reader data; makes figures and writes them to disk. 
        Operates on current working directory
        Input Arguments:
          filelist -- list of ejection sweep folders locations to be processed.

         
          Optional arguments:
              UseInternalStd -  True / False
              numTestsPerPlate - numer of different fluids per plate (organized per row)
              readertype -  E.g. biotek1 / biotek2 / BMG
              readercal - e.g. 112017
              CCT - use xrange for Lemonade CCT
          """      
        
        CCT = False  
          
        if kwargs is not None:
            for key, value in kwargs.items():
                if (self.verbose):
                    print(' Input Arg: ', key,value)
                if key == 'UseInternalStd' :
                    self.UseInternalStd = value
                elif key == 'numTestsPerPlate' :
                    self.numTestsPerPlate = value
                elif key == 'readertype'    :
                    self.readertype = value
                elif key == 'readercal' :
                    self.readercal = value
                elif key == 'CCT' :
                    CCT = value
                else:
                    print(' Ignoring Unknown option ', key )
                    

        
        for ii,val in enumerate(filelist):
            if ( os.path.exists(val + './ReaderResults' ) ):
                    readerfilenames = os.listdir(val + './ReaderResults' )
                    readerfiles = [ val + './ReaderResults/' + f for f in readerfilenames ]
            else:
                    print ('ERROR -- no folder \'./ReaderResults\' found in path ', val)
                    continue
            platetype =  os.path.basename(os.path.dirname((val)))
            if platetype not in self.platesettings : 
                platetype = self.getPlateType(os.getcwd())
            filename = platetype
            filepath = os.path.dirname(val)
            print("Processing plate ", platetype)
            self.setYRange(platetype)
            self.workDir = filepath

            if not ( self.readPickListFile() ):
                self.genDefaultPickListDbMatrix()
            # override defaults if CCT    
            if (CCT):
                self.genPickListMtrxFromArray(self.xrange_cct)
                self.platesettings[platetype]['nominalvolume'] = 50
                self.setYRange(platetype)
     #       print('Readerfiles :: ', readerfiles)    
            ejectsweepdat, sweeplist, readerPMT  = self.processEjectSweepRawReader_FixRange(readerfiles)
            if (self.verbose):    
                print (' calling plotEjectSweep ')    
         #   self.plotEjectSweep(ejectsweepdat,sweeplist,filename,filepath)
            self.platetype = platetype
            cfadjusts = self.plotBowls(ejectsweepdat,sweeplist, readerPMT, self.platesettings[platetype])

            if '384PP_AQ_SP' in filepath:
                if (self.verbose):
                     print(' -- Averaging for SP -- ' )
                cfadjusts = cfadjusts[cfadjusts['concentration'].str.startswith('14_')]
            try:                          
                cfadjusts.to_csv(filepath +  '//' + filename + '_dBAdjust.csv', index=False) 
            except Exception as error:
                print('Can\'t write to file ', filename, '_dBAdjust.csv')
           # print(" ***** WARNING -- Code Refactor required T2T and CF estimates should not be trusted ******* ")
            """
            cfadjusts is dataframe with colnames = 
                   'Concentration','T2T used','CF used','T2T suggested',
                   'CF suggested','T2T individual','CF individual', 'Wall of Death',
                   'Bowl Range Left', 'Bowl Range Right', 'Bowl Center dB',
                   'Bowl Center Vol', 'Bowl Std', 'Bowl Mean Value', 'Vol at 0 dB']
            """
        return                
        
    def round_nearest(self, x, a):
        """ Little helper function that rounds x up to the value specified by a """
        try:       
            return round(x / a) * a    
        except:
            return float("NaN")
    
    def getPlateType(self,folder):
        for plate in self.plates:
            if plate in folder:
                 return plate
        return ""