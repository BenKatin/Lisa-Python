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


import numpy as np
import matplotlib.pyplot as plt
import os
from collections import namedtuple
import pandas as pd
import matplotlib.gridspec as gridspec

import fnmatch
from collections import defaultdict


class ejectSweepAnalysis():
    np.set_printoptions(threshold=np.nan)
    QuadStat = namedtuple('QuadStat','Sheet Q Vol StD') 
    xrange_tswap = [-0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.3, -0.2, -0.2, -0.1, -0.1, 0.0, 0.0, 0.1, 0.1, 0.2, 0.2, 0.3, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    xrange_tswap_IntStd = [-0.7, -0.6, -0.5, -0.4, -0.3, -0.3, -0.2, -0.2, -0.1, -0.1, 0.0, 0.0, 0.1, 0.1, 0.2, 0.2, 0.3, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    xrange_cct = [-1.4, -1.3, -1.2, -1.1, -1, -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
#    xrange_cct = [-0.8, -0.73, -0.66, -0.59, -0.52, -0.45, -0.38, -0.31, -0.24, -0.17, -0.1, -0.03, 0.04, 0.11, 0.18, 0.32, 0.39, 0.46, 0.53, 0.6, 0.67, 0.74, 0.81]
    plates = [ '384PP_DMSO2', '384LDV_DMSO', '384LDVS_DMSO', '384LDVS_AQ_B2', '384LDV_AQ_B2', '1536LDV_DMSO', '1536LDVS_DMSO', '384PP_AQ_CP', '384PP_AQ_GP2', '384PP_AQ_BP2', '384PP_AQ_SP2']
    plates += [ '384PPG_DMSO2', '384PPG_AQ_GP2', '384PPG_AQ_CP', '384PPG_AQ_BP2', '384PPG_AQ_SP2' ]
    plates += [ '384PPL_DMSO2', '384PPL_AQ_GP2', '384PPL_AQ_CP', '384PPL_AQ_BP2', '384PPL_AQ_SP2' ]
    plates += ['96TRK_DMSO',  '96TRK_AQ_SP',  '96TRK_AQ_GP']
    markerlist=['o','s','^','v','<','>','d','p','H','*','h','8','x','+']
    markercolor=['b', 'g', 'r', 'c', 'm', 'y', 'k','hotpink','fuchsia','sage','azure','slategray','tan'] 
        
    def __init__(self):
        

        self.xrange = self.xrange_tswap
        self.verbose = True
        self.CFAdjustThreshold = 0.03
        self.ncols=24
        self.nrows=16
        self.ylo = 20
        self.yhi = 35
        self.workDir = ""
        self.numTestsPerPlate = 1
        self.UseInternalStd = False
        self.exclude16 = False
        self._internalRefCol = 16
        self.platesettings = self.genDefaultPlateSettings()    
        self.picklistdB = None  #It is a 16x24 np array with T2T values
        self.genDefaultPickListDbMatrix() #create default self.picklistdB
        self.platetype = "none"
        self.xtickstepsize = 0.2

        
        
        
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
                platesettings[plate]['maximumslope'] = 0.5 
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

    def transferFile2SquareCSV(self, adcherryPickList):
        """
        Convert a picklist file that is used by ADCherryPick to 
        a rectangle csv file that can be used by the EjectSweep.py
        --- NOTE -- this is hardcoded to assume a 16x24 dest plate --
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
        
        square = np.array(square)
        
        if (self.UseInternalStd) or (self.exclude16):
            return np.delete(square, self._internalRefCol, 1)
        else:
            return(square)

    def writePickList(self, picklist):
        with open(self.workDir + "\\used_rectangle_pick_list.csv", "w") as outf:
            for r in picklist:
                outf.write(",".join([str(ri) for ri in r]) + "\n")
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
       
    

    def setXrange(self, nsteps=24, startdb=-0.85, stepsize=0.075):
        xrange = []
        for k in range(0,nsteps):
            xrange.append(startdb+k*stepsize)
        self.genPickListMtrxFromArray(xrange)    
        return
 
    def setYRange(self,platetypesettings):
        if not  self.validatePlateTypeDict(platetypesettings):
            print(' ERROR -- something wrong with platetypesettings: ', platetypesettings)
        print(' platetype:: ', platetypesettings)
        print(' -- SETYRANGE -- ', platetypesettings)
        self.ylo = platetypesettings['nominalvolume']*0.8
        self.yhi = platetypesettings['nominalvolume']*1.4
        return

    def getSweepData(self,readerdat):
          
        alldat = np.empty([4*self.numTestsPerPlate,len(set(self.xrange))])
        for k in range(0,self.numTestsPerPlate):
          startRow = 0+k*(self.nrows//self.numTestsPerPlate)
          stopRow = (k+1)*(self.nrows//self.numTestsPerPlate)
          y, ye, x, cv = self.calcStats(readerdat, startRow, stopRow) 

          alldat[0+k*4] = x 
          alldat[1+k*4] = y
          alldat[2+k*4] = ye
          alldat[3+k*4] = cv
    
          return alldat  

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

                pickList = self.transferFile2SquareCSV(pickListFilename)

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
            


    def estimateBowl(self, ejectsweepdat,  thisplatetype, plateindex=0):
        '''
        plateindex is the index in case there are multiple sweeps per file
        '''
        if not (self.validatePlateTypeDict(thisplatetype)):
            print(" Error::: invalid plate dictionary :: ", thisplatetype)
            return 0
        d = np.zeros([len(ejectsweepdat[plateindex*4]),3],dtype=float)
        for j in range(0,len(ejectsweepdat[plateindex*4])):
            for i in range(0,3):
                d[j,i] = ejectsweepdat[plateindex*4+i][j]
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

    def plotBowls(self, ejectsweepdat,plotname,readerPMT,thisplatetype,ti='BowlEstimate',basedir="./", saveFig= False, ax=None, fsize=20):
        if not (self.validatePlateTypeDict(thisplatetype)):
            print(" Error::: invalid plate dictionary :: ", thisplatetype)
            return 0
        
        if (self.verbose):
            print( ' len(ejectsweepdat) : ' , len(ejectsweepdat))
        
        self.setYRange(thisplatetype)
        
        
        
        if (ax == None):
                fig = plt.figure(figsize=(12, 8))
                _axx = fig.add_axes([0.1, 0.1, 0.8, 0.8])
                gs = gridspec.GridSpec(1, 3)
                plotax = plt.subplot(gs[0,0:2])
                textax = plt.subplot(gs[0,2])
                
        else:     
            
            if (len(ax) != 2):
                print(' Invalid axis object specified')
                print(' ax needs to be list of two axis, one for the graph, one for the text')
                print(' "ax= [ plt.subplot(gs[0,0:2]), plt.subplot(gs[0,2] )]"  for example.')
                print('     where gs = gridspec.GridSpec(1,3)')
                return {}
            else:
                plotax = plt.subplot(ax[0])
                textax = plt.subplot(ax[1])
            if (saveFig):
                print(' Can\'t save figure when axes are specified')
                saveFig = False    
                
      # Here is an example:
#          ncols=2
#          fig = plt.figure(figsize=(10*ncols,8)); gs = gridspec.GridSpec(2,3*cols);        
#          A,B = ea.plotBowls(allstat, thisplatetype=ea.platesettings['384PPL_AQ_BP2'],
#                             plotname='test',readerPMT=1, ax=[gs[0,0:2],gs[0,2]]) ;
#          A,B = ea.plotBowls(allstat, thisplatetype = ea.platesettings['384PPL_AQ_BP2'], 
#                             plotname='t2', readerPMT=1, ax=[gs[1,3:5],gs[1,5]]);          
                
  

            
        if (self.verbose):   
            print(" plotname: ", plotname)    
            
        wdeath_thresh = thisplatetype['wallofdeath_threshold'] 
        wdeath_adj = thisplatetype['wallofdeath_adjust']
        checkmarkwidth_thresh = thisplatetype['checkmarkwidth_threshold'] 
        checkmarkwidth_adj = thisplatetype['checkmark_adjust'] 
        nominalvol = thisplatetype['nominalvolume']
        
        thisdata  = {}	
   #     ccc_t2t_cf = []
       
        if (self.verbose):
            print('')
            print(' ------- processing ', plotname, ' -------------- ')
       
        csv_wallofdeath = "NaN"
        
        textax.axis('off')
        
        plotax.errorbar(ejectsweepdat[0], ejectsweepdat[1], yerr=ejectsweepdat[2], ls='None',marker=self.markerlist[0%len(self.markerlist)],color=self.markercolor[0%len(self.markercolor)])
        plotax.set_title(plotname, fontsize=fsize)
        
        
        bowl,sortedvals = self.estimateBowl(ejectsweepdat, plateindex=0, thisplatetype=thisplatetype)
        bowlcenter = ( sortedvals[bowl[1],0] + sortedvals[bowl[0],0])/2  
        plotax.set_xlabel('Scale (dB)', fontsize=fsize)
        plotax.set_ylabel('Volume (nL)', fontsize=fsize)
        plotax.set_ylim(self.ylo,self.yhi)
        plotax.tick_params(labelsize=fsize)
        #plotax.xticks(fontsize=fsize)
       # plotax.yticks(fontsize=fsize)
        #ax2=axes[rowcount,colcount].twinx()
        ax2=plotax.twinx()
        ax2.plot(sortedvals[:,0],np.gradient(sortedvals[:,1]),color='r',marker='.')
        ax2.plot(sortedvals[:,0],np.gradient(np.gradient(sortedvals[:,1])),color='m');
        ax2.set_ylim(-5,5)
        ax2.grid()
        ax2.set_ylabel('Gradient (nL/dB)', fontsize=fsize)
        plt.axvspan(sortedvals[bowl[0],0], sortedvals[bowl[1],0], facecolor='lightgray', alpha=0.5)
        
        # ytextval will typically be the heighest text, all text is scaled below this value, with the exception of
        # wall of death 
        ytextval = 0.8 #ejectsweepdat[1].max()
        ytextstep = 0.9 #( ejectsweepdat[1].max() - ejectsweepdat[0].min())
       # xlength = #ejectsweepdat[0].max() - ejectsweepdat[1].min()
        xtextval = 0.1 #ejectsweepdat[0].max() + xlength*0.06
        
        #ax.axis([ejectsweepdat[0].min() - 0.05*xlength, 0.05*xlength + ejectsweepdat[0].max(), -0.05, 50])
#        ax2.axis([-0.05,1.05,-0.05,1.05])
        
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
                textax.text(xtextval ,ytextval+0.1*ytextstep, pstring, fontsize=fsize) 
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
                        textax.text(xtextval ,ytextval+0.1*ytextstep, pstring) 
                
   
        textax.text(xtextval,ytextval,' Bowl Range :: ' + str(sortedvals[bowl[0],0]) + '-' + str(sortedvals[bowl[1],0]),fontsize=fsize )
        textax.text(xtextval,ytextval-0.1*ytextstep,' Bowl Center :: ' + str( bowlcenter ),fontsize=fsize)
        volatbowlcenter = np.interp(bowlcenter,sortedvals[:,0],sortedvals[:,1])
        pstring = "{:.2f}".format(volatbowlcenter)
        textax.text(xtextval,ytextval-0.2*ytextstep,' Bowl Cent V :: ' + pstring,fontsize=fsize)
        pstring = "{:.2f}".format(sortedvals[bowl[0]:bowl[1],1].std())
        textax.text(xtextval,ytextval-0.3*ytextstep,' Bowl Std       :: ' + pstring,fontsize=fsize) 
        pstring = "{:.2f}".format(sortedvals[bowl[0]:bowl[1],1].mean())
        textax.text(xtextval,ytextval-0.4*ytextstep,' Bowl Mean V  :: ' + pstring,fontsize=fsize) 
        pstring = "{:.2f}".format(sortedvals[len(sortedvals)//2,1])
        textax.text(xtextval,ytextval-0.5*ytextstep,' Vol at 0 dB    :: ' + pstring,fontsize=fsize)
        pstring = "{:.2f}".format(readerPMT)
        textax.text(xtextval,ytextval-0.6*ytextstep,' PMT    :: ' + pstring,fontsize=fsize)
       
        pstring ="{:.2f}".format(self.round_nearest(bowlcenter,0.05))        
        t2tdelta = pstring
        textax.text(xtextval,ytextval-0.8*ytextstep, 'T2T:: ' + pstring, fontweight='bold',fontsize=fsize)
        if abs( volatbowlcenter/nominalvol - 1 ) < self.CFAdjustThreshold :
            CFAdjust = 0
        else:    
            CFAdjust = -(1-volatbowlcenter/nominalvol)*100*0.05
        pstring ="{:.2f}".format(self.round_nearest(CFAdjust,0.05))
        cfdelta = pstring
        textax.text(xtextval,ytextval-0.9*ytextstep, 'CF :: ' + pstring + ' MHz', fontweight='bold',fontsize=fsize)
        





        csv_BowlRange_L = "{:.2f}".format(sortedvals[bowl[0],0])
        csv_BowlRange_R = "{:.2f}".format(sortedvals[bowl[1],0]) 
        csv_BowlCenter = "{:.2f}".format(bowlcenter)
        csv_BowlCentVol = "{:.2f}".format(volatbowlcenter)
        csv_Bowl_Std = "{:.2f}".format(sortedvals[bowl[0]:bowl[1],1].std())
        csv_BowlMeanValue = "{:.2f}".format(sortedvals[bowl[0]:bowl[1],1].mean())
        csv_VolAt0DB = "{:.2f}".format(sortedvals[len(sortedvals)//2,1])
        
        thisdata['Name'] = plotname
        thisdata['T2T adjust'] = t2tdelta
        thisdata['CF adjust'] = cfdelta
        thisdata['wallOfDeath'] = csv_wallofdeath
        thisdata['BowlLeft'] = csv_BowlRange_L
        thisdata['BowlCenter'] = csv_BowlCenter
        thisdata['BowlRight'] =  csv_BowlRange_R
        thisdata['BowlVol_Center'] = csv_BowlCentVol
        thisdata['BowlVol_Std'] = csv_Bowl_Std
        thisdata['BowlVol_Mean'] = csv_BowlMeanValue
        thisdata['BowlVol_0dB'] = csv_VolAt0DB
        thisdata['ReaderPMT'] = readerPMT

        
        if (saveFig):
            try:
                print(' -- saving to file :: ', plotname, ' in folder ', basedir, ' -- ')
                file = basedir + "\\" + plotname + '_bowl.png'
                fig.savefig(file,bbox_inches='tight')
                file = basedir + "\\" + plotname + '_bowl.svg'
                fig.savefig(file,bbox_inches='tight')
            except Exception as error:
                print('Can\'t write to file ', plotname, '_bowl* in folder ', basedir)
        
 #       if abs(float(cfdelta)) > 0.3:
 #           thisdata[2] = "NaN"
 #           thisdata[4] = "NaN"
        
        #used to deal with grouping T2T and CP for CP, B2 and SP2
   #     ccc = plotname.split("_", 1)[0]
    #    ccc_t2t_cf.append([ccc, t2tdelta, thisdata[2], csv_BowlRange_L, csv_BowlRange_R])
        
       # alladjusts.append(thisdata)
   
        return thisdata  #3   ccc_t2t_cf 
      
      # this statement messes up the drawing of the legend          
 
    def newmethod(self):      
      
        fig.subplots_adjust(hspace=0.55, wspace=0.4)
    #    ax.legend()
        #plt.show()
    
        fi = plt.gcf()
    #    print("Current working dir: ", os.getcwd(), "saving to ", basedir)

        
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