# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 14:09:17 2017

@author: avandenbroucke
"""

from ..EjectSweep import ejectSweepAnalysis
import xlrd
import matplotlib.pyplot as plt
from ..DropCV import ReaderDat
import os
import numpy as np
import pandas
import matplotlib.gridspec as gridspec
import matplotlib

class processEjectSweep(ejectSweepAnalysis.ejectSweepAnalysis):

    def __init__(self):
         super(processEjectSweep,self).__init__()
         self.verbose = True
         self.numTestsPerPlate = 1

         self.applyPMTCorr = False
         return
    
    def csv_or_xls(self):
        return  '.csv' if 'bmg' in self.reader.lower() else '.xls'
    
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

    def Statistics2Csv(self, transfername, x, y, ye, cv,  PMT):
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
                    statOut.write("Reader = %s, LUTDate = %s, PMTCorr = %f\n"%(tuple((self.readertype, self.readercal, PMT))))
                    statOut.write("dB, mean, std, cv\n")
                    for r in sdata:
                        statOut.write("%f, %f, %f, %f\n"%tuple(r))
            except Exception as error:
                 print("Error opening file EjectSweep_stats.csv for writing in folder ", self.workDir)
                 return        

    

 
    #def processEjectSweepRawReader_FixRange(self,readerfilelist, numTestsPerPlate = 1, reader='Biotek2', cal='042016', UseInternalStd = False):
    def processEjectSweepRawReader(self,readerfilelist, filename = 'Readerdat', outdir = os.getcwd()):
        """Processes Raw BioTek reader data and returns a dictionary with keys each reader file, and
           values the PMTCorr and the Volumetric data
         Input Arguments:
           filelist -- all files to process, these would be individual reader files, including matech files 
           reader and LUT are specified  at the Class level
           """  
        #self.numTestsPerPlate = numTestsPerPlate
        r = ReaderDat.ReaderDat();
        r.setCalCurve(lutdate=self.lutdate,reader=self.reader,useInternalStd=self.UseInternalStd); 
        r.applyPMTCorr = self.applyPMTCorr
        print(' ---- Std Curve Slope :: ', r.StdCurveSlope, ' Offset :: ', r.StdCurveOffset, ' ---- ')
        
        useMatech = not self.UseInternalStd
        #self.xrange = self.xrange_tswap_IntStd if self.UseInternalStd else self.xrange_tswap

        
        
        readerfiles = [f for f in readerfilelist if f.endswith(self.csv_or_xls()) and 'BowlAnalysis' not in f]
        matechfiles = [ f for f in readerfiles if 'matech' in f.lower()]  
        for m in matechfiles: readerfiles.remove(m) 
        
        if (useMatech): 
            assert(len(matechfiles) == 2), ' **** ERROR **** : need exactly 2 matech files but found: %d'%len(matechfiles)
            r.setPMTCorr(matechfiles[0],matechfiles[1]);
            print(' ---- PMT Correction:: ', r.StdCurvePMTCorr, ' ---- ')   
        assert(len(readerfilelist) >= 1), ' **** ERROR **** : No reader files found'
        

        alldat = {}
        if (self.verbose):
            print('readerfilelist:: ', readerfilelist)
            print('readerfiles:: ', readerfiles)
             
        nrows = ( len(readerfiles)+1)//2
        ncols = 2
        if ( nrows == 1) :
             nrows += 1
   #     print( ' nrows : ', nrows, ' ncols: ' , ncols)    
        fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(18*ncols,12*nrows))
        ax[-1][-1].axis('off')
    #    print( ' nrows : ', nrows, ' ncols: ' , ncols)
        rind = 0
        colind = 0
        for i in range(0,len(readerfiles)):
            dr = r.processReaderFile(readerfiles[i]); 
            dc = r.applyCalCurve(dr); 
            if not r.readerdatAvailable:
                print( "PMT correction of " +str(r.StdCurvePMTCorr)+" too high ? ( Tolerance : " + str(r.PMTCorrectionTolerance) + " )")
                continue
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

            alldat[readerfiles[i]] = {}
            alldat[readerfiles[i]]['VolDat'] = dc_f
            alldat[readerfiles[i]]['PMTCorr'] = r.StdCurvePMTCorr
   
        try:        
            plt.savefig(filename + '.png')            
        except Exception as error:
            print('Can\'t save figure to file ' + filename + '.png in folder ', outdir)
        return alldat   

     
  
    
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
            self.setYRange(self.platesettings[platetype])
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


    def processRawEjectSweep(self,folderlist, **kwargs):
        #numTestsPerPlate=1, readertype='Biotek2', readercal=None, UseInternalStd = False, CCT= False):

        """ Processes Eject Sweep Raw Reader data; makes figures and writes them to disk. 
        Operates on current working directory
        Input Arguments:
          filelist -- list of ejection sweep folders locations to be processed.

         
          Optional arguments:
              UseInternalStd -  True / False
              numTestsPerPlate - numer of different fluids per plate (organized per row)
              reader -  E.g. biotek1 / biotek2 / BMG
              lutdate - e.g. 112017
              CCT - use xrange for Lemonade CCT
          """      
        
        CCT = False  
        scale = 12
        AspectRatio = 1.5
       
        if kwargs is not None:
            for key, value in kwargs.items():
                if (self.verbose):
                    print(' Input Arg: ', key,value)
                if key == 'UseInternalStd' :
                    self.UseInternalStd = value
                elif key == 'numTestsPerPlate' :
                    self.numTestsPerPlate = value
                elif key == 'readertype'    :
                    self.reader = value
                elif key == 'lutdate' :
                    self.lutdate = value
                elif key == 'CCT' :
                    CCT = value
                elif key == 'Scale' :
                    scale = value
                elif key == 'AspectRatio' :
                    AspectRatio = value
                else:
                    print(' Ignoring Unknown option ', key )
                    
        AllDatDf = pandas.DataFrame()
        
        for ii,val in enumerate(folderlist):
            if ( os.path.exists(val + './ReaderResults' ) ):
                    readerfilenames = os.listdir(val + './ReaderResults' )
                    readerfiles = [ val + './ReaderResults/' + f for f in readerfilenames ]
                    self.workDir = val
            else:
                    print ('ERROR -- no folder \'./ReaderResults\' found in path ', val)
                    continue
            platetype =  os.path.basename(os.path.dirname((val)))
            if platetype not in self.platesettings : 
                platetype = self.getPlateType(os.getcwd())
            filename = platetype
            filepath = os.path.dirname(val)
      #      self.processRawEjectSweepFiles(readerfiles,filepath, filename)
            print("Processing plate ", platetype)
            self.setYRange(self.platesettings[platetype])
    #        self.workDir = filepath

            if not ( self.readPickListFile() ):
                self.genDefaultPickListDbMatrix()
            # override defaults if CCT    
            if (CCT):
                self.genPickListMtrxFromArray(self.xrange_cct)
                self.platesettings[platetype]['nominalvolume'] = 50
                self.setYRange(self.platesettings[platetype])
     #       print('Readerfiles :: ', readerfiles)    
            ejectsweepdat  = self.processEjectSweepRawReader(readerfiles)
          
            if (self.verbose):    
                print (' calling plotEjectSweep ')    
            # now for each file, we will need to figure out how many transfers, based on "numTestsPerPlate"  
            nplots = len(ejectsweepdat)*self.numTestsPerPlate
            ncols = 2
            nrows = ( nplots+1)//ncols
            
            if ( nrows == 1) :
               nrows += 1
            if self.verbose:
                print( ' nrows : ', nrows, ' ncols: ' , ncols)  
                print(' figsize : (', AspectRatio*scale*ncols, ',', nrows+scale,')')
            fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(AspectRatio*ncols*scale,nrows*scale))
       #     plt.tight_layout(pad=0.4,w_pad=0.5,h_pad=1.0)
#          fig = plt.figure(figsize=(10*ncols,8)); gs = gridspec.GridSpec(2,3*cols);  
#          fig = plt.figure(figsize=(10*ncols,8)); gs = gridspec.GridSpec(2,3*cols);  
            ax[-1][-1].axis('off')
            tcols = 3*ncols
            gs = gridspec.GridSpec(nrows,tcols);               
            irow = 0
            icol = 0   
            pltcnt = 0
            for ff, res in ejectsweepdat.items():
                voldat = res['VolDat']
                pmtcor = res['PMTCorr']
                for k in range(0,self.numTestsPerPlate):
                    startRow = 0+k*(self.nrows//self.numTestsPerPlate)
                    stopRow = (k+1)*(self.nrows//self.numTestsPerPlate)
                    y, ye, x, cv = self.calcStats(voldat, startRow, stopRow) 
                    title = os.path.basename(ff).split(self.csv_or_xls())[0]
                    if self.numTestsPerPlate > 1 :
                        title += '_' + str(k)
                    if self.verbose:    
                        print( ' irow: ', irow, ' icol: ', icol, ' pltcnt : ', pltcnt)    
                    A = self.plotBowls([x,y,ye,cv], ax=[gs[irow,icol:icol+2],gs[irow,icol+2]], plotname=title, readerPMT=pmtcor, thisplatetype=self.platesettings[platetype], basedir=self.workDir)
                    B = pandas.DataFrame.from_dict(A, orient='index').T
                    B['platetype'] = platetype
                    B['Conc'] = title.split('__')[0]
                    AllDatDf = AllDatDf.append(B)
       

                    transfername = os.path.basename(ff).split(self.csv_or_xls())[0]
                    transfername += str(k)
 #                   transfernames.append(transfername)
                    
                 
                    
                    self.Statistics2Csv(transfername, x, y, ye, cv, pmtcor) 
                    if (pltcnt+1)%(ncols) :
                        icol += 3
                    else:
                        irow +=1
                        icol = 0
                    pltcnt += 1    
            # we need to know the platetype as well  
            gs.tight_layout(fig)
      #      print('AllDatDF.columns:: ', AllDatDf.columns)
            AllDatDf['T2T suggested'] = AllDatDf['T2T adjust']
            AllDatDf['CF suggested'] = AllDatDf['CF adjust']
            AllDatDf['CF individual'] = AllDatDf['CF adjust']
            AllDatDf['T2T individual'] = AllDatDf['T2T adjust']
            
            # Adjust 'suggestions' for SP : CF/T2T based on value of CF at 14 #  
            if len(  AllDatDf[AllDatDf['platetype'] == '384PPL_AQ_SP2']) > 0 :
                if (self.verbose):
                    print(' -- Averaging for SP -- ' )
                cfs = AllDatDf['CF individual'][(AllDatDf['platetype'] == '384PPL_AQ_SP2') & (AllDatDf['Conc'] == '14')]
                if len(cfs) > 0 :
                    cf = cfs.values[0]
                    AllDatDf['CF suggested'][AllDatDf['platetype'] == '384PPL_AQ_SP2'] = cf
                else:
                    print('*** WARNING *** Unable to average CF for SP ! ')
                t2ts = AllDatDf['CF individual'][(AllDatDf['platetype'] == '384PPL_AQ_SP2') & (AllDatDf['Conc'] == '14')]
                if len(t2ts) > 0 :
                    t2t = t2ts.values[0]
                    AllDatDf['T2T suggested'][AllDatDf['platetype'] == '384PPL_AQ_SP2'] = t2t
                else:
                    print('*** WARNING *** Unable to average CF for SP ! ')    
                    
            dfcols = ['Name', 'platetype', 'Conc', 'T2T adjust', 'CF adjust',   'T2T suggested', 'CF suggested', 'T2T individual',   'CF individual', 
              'wallOfDeath', 'BowlLeft', 'BowlCenter', 'BowlRight',    'BowlVol_Center',   'BowlVol_Std',  'BowlVol_Mean', 'BowlVol_0dB',  'ReaderPMT'  ]
            
            AllDatDf = AllDatDf[dfcols]
            AllDatDf.columns = dfcols
            
            try:                          
                AllDatDf.to_csv(self.workDir +  '//' + filename + '_dBAdjust.csv', index=False) 
            except Exception as error:
                print('Can\'t write to file ', filename, '_dBAdjust.csv')
            
            try:                          
                print(' -- saving to file :: ', filename, ' in folder ', self.workDir, ' -- ')
                file = self.workDir + "\\" + filename + '_bowl.png'
                fig.savefig(file,bbox_inches='tight')
                
            except Exception as error:
                print('Can\'t write to file ', filename, '_bowl.png')
                
           # print(" ***** WARNING -- Code Refactor required T2T and CF estimates should not be trusted ******* ")
            """
            cfadjusts is dataframe with colnames = 
                   'Concentration','T2T used','CF used','T2T suggested',
                   'CF suggested','T2T individual','CF individual', 'Wall of Death',
                   'Bowl Range Left', 'Bowl Range Right', 'Bowl Center dB',
                   'Bowl Center Vol', 'Bowl Std', 'Bowl Mean Value', 'Vol at 0 dB']
            """
        return     AllDatDf            