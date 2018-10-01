# -*- coding: utf-8 -*-
"""
Created on Tue Oct  4 09:46:28 2016

@author: avandenbroucke
"""

import pandas
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mpltcolors
from ..PlateQC import barCodes
import os, shutil
import datetime


arenaFileName = 'AllMaps.csv'

def genMap(wells=384, geo='PP', style='UCP', fluid='DMSO', conc=0, version='2', impedance=None, volume=None, instrument='55X'):
    styles = ['UCP','ICP','SIG','FT','FF','DD','HC']
    fluids = ['DMSO','GLY','SP','AQ','CP','MPD','MIX']
    version = int(version)
    nrows, ncols, rowletters = wellsToRowCols(wells)
    thismap = []
    for i in range(0,nrows):
        for j in range(0,ncols):
            thiswell={}
            thiswell['Well'] = rowletters[i].upper() + str(j+1)
            thiswell['Row'] = i
            thiswell['Col'] = j
            if (volume):
                thiswell['mVolume'] = volume
            else:    
                thiswell['mVolume'] =  0 
            thiswell['mFluid'] = fluid
            thiswell['mConc'] = conc
            if (impedance):
                thiswell['mImpedance'] = impedance
            else:    
                thiswell['mImpedance'] = concToImpedance([conc],fluid)[0]
            thiswell['mFillHeight'] = 0
            thismap.append(thiswell)
            
    if style not in styles:
        print(' *** ERROR :: Map style ', style , ' not suported. Supported modes are : ')
        print(styles)
        return
    
    if ( style=='SIG' ):
        df = pandas.DataFrame(thismap)
        if (geo == 'PP'):
            df['mVolume'] = 30
        if (geo == 'LDV' ):
            if  ( wells == 384 ):
                df['mVolume'] = 7
            if  ( wells == 1536 ):
                df['mVolume'] = 4
        return df 
    
    if ( style=='HC'):
        df = pandas.DataFrame(thismap)
        if (geo == 'PP'):
            thismap = populatePPHCConc(thismap, nrows, ncols)  
        return pandas.DataFrame(thismap)
        
    if (wells == 384 ):
         if ( style == 'UCP' or style == 'ICP' ) :
             # Fill Volumes first
             if ( geo == 'PP'):
                 if instrument == '525' :
                     thismap = populatePPUCPVolumes3(thismap,nrows,ncols)
                     if fluid == 'PBS':
                         thismap = populate525UCP(thismap,nrows,ncols, fluids=['PBS00','PBS14','PBS200'])
                         return pandas.DataFrame(thismap)
                     else :    
                         thismap = populate525UCP(thismap,nrows,ncols,fluids=['GPS00','GPS14','GPS25'])
                         return pandas.DataFrame(thismap)
                 else :    
                     thismap = populatePPICPVolumes(thismap, nrows, ncols) 
             if (geo == 'LDV'):
                 if ( fluid == 'DMSO' ):
                    thismap = populateLDVICPVolumes(thismap, nrows, ncols, version)
                 if ( fluid == 'AQ' ) :
                    thismap = populateLDVAQICPVolumes(thismap, nrows, ncols)
                 if ( fluid == 'GLY' ) :
                    thismap = populateLDVGPICPVolumes(thismap, nrows, ncols)
                    
         if ( style == 'FT' ):
             if (geo == 'PP' ):
                 if ((fluid == 'AQ' ) or (fluid == '2.4M-HEPES') or (fluid == 'PEG-3350') ):
                     thismap = populatePPFTVolumes(thismap, nrows, ncols, [20,30,40,50], version )
                 else:
                     if (fluid == 'MPD'):
                         thismap = populatePPFTVolumes(thismap, nrows, ncols, [30,35,40,45],version )
                     else:    
                         if (version == '1' ):
                             if ( fluid == 'DMSO' ):
                                 thismap = populatePPFTVolumes(thismap, nrows, ncols, [20,30,40,50], version)
                             else:
                                 thismap = populatePPFTVolumes(thismap, nrows, ncols, [20,30,40,50], version)
                         else: 
                             if ( fluid == 'DMSO' ):
                                 thismap = populatePPFTVolumes(thismap, nrows, ncols, [15,20,30,65], version)
                             else :
                                 if (fluid == 'PBS200' ):
                                     thismap = populatePPFTVolumes(thismap, nrows, ncols, [18,20,40,65], version)
                                 else:    
                                     thismap = populatePPFTVolumes(thismap, nrows, ncols, [15,20,40,65], version)
             if (geo == 'LDV'):
                 if (fluid == 'DMSO'):
                     thismap = populateLDVFTVolumes(thismap, nrows, ncols, version)
                 if (fluid == 'GLY'):
                     thismap = populateLDVPlusFTVolumes(thismap, nrows, ncols, version)
         if ( style == 'DD' ):
             if (geo == 'PP'):
                 if ((fluid.startswith('GPS')) or fluid.startswith('GLY') ):
                     thismap = populateDDVolumes(thismap, nrows, ncols, cols=[3,4,5,7,8,9,11,12,13,15,16,17,19,20,21], vol=volume)
                 else:
                     thismap = populateDDVolumes(thismap, nrows, ncols, cols=[8,10,12,14,16], vol=volume)
             if (geo == 'LDV'):
                 if ((fluid.startswith('GLY'))):
                     thismap = populateDDVolumes(thismap, nrows, ncols, cols=[3,4,6,7,9,10,12,13,15,16,18,19], vol=volume)
         if ( not thismap):
            return
         
         if ( fluid == 'PBS' ):
             if (style == 'UCP' and int(version) > 2):
                 thismap = populateSPUCP(thismap, nrows, ncols)
           
            # Lookup concentrations        
         if ( fluid == 'DMSO' ):
             if ( style == 'UCP' ):
                 thismap = populateUCP(thismap, nrows, ncols, concentrations=[70, 90, 100, 80],fluid=fluid)
             if ( style == 'ICP' ):
                 thismap = populateDMSOICP(thismap, nrows, ncols)
         if (fluid.startswith('GLY') ) or (fluid.startswith('GPS')) :
            if ( style == 'ICP' ):
                thismap = populateGlyICP(thismap, nrows, ncols)
            if ( style == 'UCP' ) and ( geo == 'LDV' ) and ( instrument == '525') :
                thismap = populateUCP(thismap,nrows,ncols, concentrations=[0,20,40,50],fluid=fluid)
            if ( style == 'DD' ):
                if (geo == 'PP'):
                    thismap = populateGlyDDCols(thismap, nrows, ncols, cols=[3,4,5,7,8,9,11,12,13,15,16,17,19,20,21], concs=[10,10,10,20,20,20,30,30,30,40,40,40,50,50,50])
                if (geo == 'LDV'):
                    thismap = populateGlyDDCols(thismap, nrows, ncols, cols=[3,4,6,7,9,10,12,13,15,16,18,19], concs=[0,0,10,10,20,20,30,30,40,40,50,50])
         if ( fluid.startswith('PBS')):
             if (style == 'DD' ):
                thismap = populateGlyDDCols(thismap, nrows, ncols, cols=[8,10,12,14,16], concs=[100,100,100,100,100])
    if (wells == 1536 ):            
         if (geo == 'LDV'): 
              if ( fluid == 'DMSO' ):
                  if ( style == 'ICP' ) :
                      thismap = populate1536LDVVolumes(thismap, nrows, ncols)
                  if ( style == 'UCP' ) :
                      if int(version) == 1:
                          thismap = populate1536LDVVolumes(thismap, nrows,ncols)
                      else:    
                          thismap = populate1536LDVUCPVolumes(thismap,nrows,ncols)
         if (geo == 'HB'):
             if (fluid == 'DMSO'):
                if (style == 'UCP' ):
                    if int(version) == 1:
                        thismap = populate1536LDVVolumes(thismap, nrows,ncols)
         if (fluid == 'DMSO'):
              if (style =='ICP' ) :
                  thismap = populate1536DMSOICSP(thismap, nrows, ncols)
              if (style == 'UCP' ):
                  if int(version) == 1:
                      thismap = populate1536DMSOICSP(thismap,nrows,ncols)
                  else:    
                      thismap = populate1536DMSOUCP(thismap, nrows, ncols)
              if (style == 'FT'):
                  thismap = populateLDVFTVolumes(thismap, nrows, ncols, version)
         
                  
    if (wells == 96 ):
        if ( style == 'UCP' ):
            thismap = populateTRVolumes(thismap, nrows, ncols,  colvols=[35,60,26,79,100,72,86,18,44,65,93,53])
        if ( style == 'FT' ):
            if (fluid == 'DMSO' ):
                thismap = populateTRVolumes(thismap, nrows, ncols, colvols=[18,18,18,18,55,55,55,55,90,90,90,90])
            else:
                thismap = populateTRVolumes(thismap, nrows, ncols, colvols=[20,20,20,20,55,55,55,55,90,90,90,90]) 
              
    return pandas.DataFrame(thismap)  
 
def mapframeAsMatrix(mapdataframe,field='mVolume',rfield='Row',cfield='Col'):
#    print(mapdataframe.columns)
    nrows = max(mapdataframe[rfield].unique())+1
    ncols = max(mapdataframe[cfield].unique())+1
    mtrx = np.zeros([nrows,ncols])
    for i,row in mapdataframe.iterrows():
        try:
            mtrx[row[rfield]][row[cfield]] = row[field]
        except ValueError:
            mtrx[row[rfield]][row[cfield]] = -1
    return mtrx    
 
def plotMap(mapdataframe,row_labels,columns, ax=None,title='XXp',fluidscale = False, fluidkey='PBS' ):
        #row_labels = list('ABCDEFGHIJKLMNOP')
        colors=['palegreen','lightskyblue', 'yellow','hotpink','silver','beige','orange','lightcoral','azure']
        col_labels = [ c+1 for c in columns ]
        if len(columns) > 24 :
            scale = 1.5
        else :
            scale = 1
        #fig, ax = plt.subplots(nrows=1,ncols=1,figsize=(12,18))
        if ax == None:
            fig = plt.figure(figsize=(12*scale, 8*scale))
            ax = fig.add_axes([0.1, 0.1, 0.9, 0.9])
#        axt = fig.add_axes([0.1, 0.8, 0.8, 0.1 ])

 
        # local change for fluids        
        if fluidscale:
             for i,row in mapdataframe.iterrows():
                 mapdataframe.loc[i,'mConc'] = int(str.split(row['mFluid'],fluidkey)[1])
                        
       
        concdata = mapframeAsMatrix(mapdataframe,'mConc')
        data = mapframeAsMatrix(mapdataframe,'mVolume')
       
        uniques = [ u for u in mapdataframe['mConc'].unique() if u != '-' ] #if u[0] in '0123456789' ]
    #    print(' uniques: ', uniques, ' ', mapdataframe['mConc'].unique())

        
                
        
       
        concentrations = np.sort(uniques)      
        nconcentrations = len(concentrations)
        bounds = np.zeros(nconcentrations+1)
  #      print(' concentrations : ', nconcentrations, ' title: ', title)
        if (nconcentrations > 1 ) :
            for i in range(0,nconcentrations-1):
                bounds[i+1]=(concentrations[i+1]+concentrations[i])/2
            if ( nconcentrations > 2 ):    
                spread = (bounds[3]-bounds[2]) / 2     
                spread = 0.05;
            else:
                spread = 8
            bounds[0] = concentrations[0] - spread
            bounds[nconcentrations] = concentrations[nconcentrations-1] + spread
        else :
            if concentrations[0] != 0 :
                bounds[0] = 0.95*concentrations[0]
                bounds[1] = 1.05*concentrations[0]
            else :    
                 bounds[0] = -0.05
                 bounds[1] = 0.05      
        
        cmap = mpltcolors.ListedColormap(colors[0:nconcentrations])
        norm = mpltcolors.BoundaryNorm(bounds,cmap.N)
    
       
        heatmap = ax.imshow(concdata,cmap=cmap, norm=norm ,interpolation='None') #,vmin=0.6*mean,vmax=1.4*mean)
        for y in range(data.shape[0]):
            for x in range(data.shape[1]):
                ax.text(x , y , '{:.3g}'.format(data[y, x]),
                         horizontalalignment='center',
                         verticalalignment='center',
                     )
    
        # create an axes on the right side of ax. The width of cax will be 5%
        # of ax and the padding between cax and ax will be fixed at 0.05 inch.
     #   divider = plt.make_axes_locatable(ax)
     #   cax = divider.append_axes("right", size="5%", pad=0.05)
    
        
        plt.colorbar(heatmap, ax=ax, cmap=cmap, norm=norm, boundaries=bounds, ticks=concentrations, fraction=0.025, pad=0.04)
        # put the major ticks at the middle of each cell
        ax.set_xticks(np.arange(data.shape[1]) , minor=False)
        ax.set_yticks(np.arange(data.shape[0]) , minor=False)
        
        ax.set_xticks(np.arange(data.shape[1]) + 0.5 , minor=True)
        ax.set_yticks(np.arange(data.shape[0]) + 0.5 , minor=True)
        # want a more natural, table-like display
    #    ax.invert_yaxis()
        ax.xaxis.tick_top()
        ax.set_xticklabels(col_labels)
        ax.set_yticklabels(row_labels)    
        
        ax.yaxis.grid(True, which='minor')
        ax.xaxis.grid(True, which='minor')         
        
           
        
        # make text box with stats
        textstring = title
#        textstring = title + ' Mean : ' + '{:4.2f}'.format(printstats.Mean) + 'nL'
#        textstring += ' CV : ' + '{:4.1f}'.format(printstats.CV) + '%'
        #+ '\n'
#        textstring += ' Empties : ' + '{:3d}'.format(printstats.Empties)
#        textstring += ' Outliers : ' + '{:3d}'.format(printstats.Outlier)
#        textstring += ' Reliabilities : ' + '{:3d}'.format(printstats.Reliability)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        
      #  axt.get_yaxis().set_visible(False)
      #  axt.get_xaxis().set_visible(Falsse)
        ax.text(0.05, 1.1, textstring, transform=ax.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)
        return

def populatePPHCConc(thismap, nrows, ncols):
    updatedmap = []
    concentrations = [80,100]
    impedances = [1.78 ,1.48 ]
    fluids = ['DMSO','PBS']
    for well in thismap:
        if well['Row'] < 7 :
            idx = 0
        else :
            if well['Row'] > 8 :
                idx = 1
            else:
                idx = -1
        if idx >= 0 :
            well['mConc'] = concentrations[idx]
            well['mImpedance'] = impedances[idx]
            well['mFluid'] = fluids[idx]
            well['mVolume'] = 30
        else:
            well['mVolume'] = 0
            well['mImpedance'] = 0
        updatedmap.append(well)
    return updatedmap    
        
def populateUCP(thismap, nrows, ncols, concentrations=[70, 90, 100, 80], fluid='DMSO'):
    updatedmap = []    
    #concentrations = [70, 90, 100, 80]
    impedances = concToImpedance(concentrations, fluid)
    nconcentrations = len(concentrations)
    updatedmap = []
    for well in thismap: 
        concentrationindex = well['Row']//nconcentrations
        well['mConc'] = concentrations[concentrationindex]
        well['mImpedance'] = impedances[concentrationindex]
        updatedmap.append(well)
    return updatedmap    
 
    
    
def populateSPUCP(thismap, nrows, ncols):
    updatedmap = []
    fluids = ['PBS14','PBS200']
    nfluids = len(fluids)
    for well in thismap: 
        fluidindex = well['Row']//8
        well['mFluid'] = fluids[fluidindex]
        updatedmap.append(well)
    return updatedmap

def populate525UCP(thismap, nrows, ncols,  fluids=['PBS00','PBS14','PBS200']):
    updatedmap = []
    nfluids = len(fluids)
    for well in thismap: 
        fluidindex = well['Col']//8
        well['mFluid'] = fluids[fluidindex]
        updatedmap.append(well)
    return updatedmap

def populateDMSOICP(thismap, nrows, ncols):
    updatedmap = []    
    concentrations = [70, 75, 80, 85, 90, 95, 100, 100, 100, 95, 90, 85, 80, 75, 70, 70]
    impedances = concToImpedance(concentrations,'DMSO')
    updatedmap = []
    for well in thismap: 
        concentrationindex = well['Row']
        well['mConc'] = concentrations[concentrationindex]
        well['mImpedance'] = impedances[concentrationindex]
        updatedmap.append(well)
    return updatedmap    

def populate1536DMSOICSP(thismap, nrows, ncols):
    updatedmap = []    
    concentrations = [70, 70, 75, 75, 80, 80 ,85, 85, 90, 90, 95, 95, 100, 100, 100, 100, 100, 100, 95, 95, 90, 90, 85, 85, 80, 80, 75 ,75, 70 ,70 ,70 ,70]
    impedances = concToImpedance(concentrations,'DMSO')
    updatedmap = []
    for well in thismap: 
        concentrationindex = well['Row']
        well['mConc'] = concentrations[concentrationindex]
        well['mImpedance'] = impedances[concentrationindex]
        updatedmap.append(well)
    return updatedmap  
 
    
def populate1536DMSOUCP(thismap, nrows, ncols):
    updatedmap = []    
    subconcentrations = [70, 70, 90, 90, 100, 100, 80, 80 ]
    concentrations = subconcentrations
    for i in range(0,3):
        concentrations += subconcentrations
    impedances = concToImpedance(concentrations,'DMSO')
    updatedmap = []
    for well in thismap: 
        concentrationindex = well['Row']
        well['mConc'] = concentrations[concentrationindex]
        well['mImpedance'] = impedances[concentrationindex]
        updatedmap.append(well)
    return updatedmap     
    

def populateGlyICP(thismap, nrows, ncols):
    updatedmap = []
    concentrations = [0 , 10, 20, 30, 40, 45, 50, 55]
    impedances = concToImpedance(concentrations,'GLY')
    nconcentrations = len(concentrations)
    updatedmap = []
    for well in thismap: 
        concentrationindex = well['Row']%nconcentrations
        well['mConc'] = concentrations[concentrationindex]
        well['mImpedance'] = impedances[concentrationindex]
        updatedmap.append(well)
    return updatedmap    

def populateGlyDDCols(thismap, nrows, ncols, cols=[8,10,12,14,16], concs=[10,20,30,40,50]):
     impmap = np.zeros([nrows,ncols])
     concmap = np.zeros([nrows,ncols])
     imp = concToImpedance(concs,'GLY')
     for i,c in enumerate(cols):
         impmap[:,c-1]  = imp[i]
         concmap[:,c-1] = concs[i]              
     updatedmap = []
     for well in thismap: 
#         if well['mVolume'] > 0:
            col = well['Col']
            row = well['Row']
            well['mConc'] =  concmap[row,col]
            well['mImpedance'] = impmap[row,col]
            updatedmap.append(well)
     return updatedmap       
            
          
def populatePPUCPVolumes3(thismap, nrows, ncols):    
    colvolhalf=[65,65,50,50,35,35,25,25]
    colvols = colvolhalf + colvolhalf + colvolhalf
    if ( len(colvols) != ncols ) :
        print(' *** ERROR :: number of columns inconsistent ')
        return []
    updatedmap = []    
    for well in thismap:
        well['mVolume'] = colvols[well['Col']]
        updatedmap.append(well)
    return updatedmap 
    
def populatePPICPVolumes(thismap, nrows, ncols):    
    colvolhalf=[68,40,55,13,25,15,50,65,45,60,20,30]
    colvols = colvolhalf + colvolhalf
    if ( len(colvols) != ncols ) :
        print(' *** ERROR :: number of columns inconsistent ')
        return []
    updatedmap = []    
    for well in thismap:
        well['mVolume'] = colvols[well['Col']]
        updatedmap.append(well)
    return updatedmap   

def populateLDVGPICPVolumes(thismap, nrows, ncols):
    colvols=[14,14,14,12,12,12,4,4,4,6,6,6,8,8,8,7,7,7,9,9,9,10,10,10]
    if ( len(colvols) != ncols ) :
            print(' *** ERROR :: number of columns inconsistent ')
            return []
    updatedmap = []    
    for well in thismap:
        well['mVolume'] = colvols[well['Col']]
        updatedmap.append(well)
    return updatedmap    
    
def populateLDVAQICPVolumes(thismap, nrows, ncols,version=2):
    if version == 3 :
        colvols=[14,14,14,12,12,12,4,4,4,6,6,6,8,8,8,7,7,7,9,9,9,10,10,10]
    else:    
        colvols=[13,13,13,12,12,12,2.75,2.75,2.75,4,4,4,7.5,7.5,7.5,6,6,6,9,9,9,10,10,10]
    
    if ( len(colvols) != ncols ) :
        print(' *** ERROR :: number of columns inconsistent ')
        return []
    updatedmap = []    
    for well in thismap:
        well['mVolume'] = colvols[well['Col']]
        updatedmap.append(well)
    return updatedmap    

def populateDDVolumes(thismap, nrows, ncols, cols=[8,10,12,14,16], vol=60):
    volmap = np.zeros([nrows,ncols])
    for c in cols:    
        volmap[:,c-1] = vol
    updatedmap = []    
    for well in thismap:
         well['mVolume'] = volmap[well['Row'],well['Col']]
         updatedmap.append(well)
    return updatedmap         
    

def populatePPFTVolumes(thismap, nrows, ncols, quadvols=[15,20,40,65], version=2):
        print('version = ', version)
        halfrows = nrows//2
        halfcols = ncols//2
        volmap = np.zeros([nrows,ncols])
        if version == 3:
            for i, vol in enumerate(quadvols):
                rstart = i//2
                cstart = i%2 
                volmap[rstart:nrows:2, cstart:ncols:2] = vol 
        else:    
            for i, vol in enumerate(quadvols):
                rstart = (i//2)*halfrows
                rstop = rstart + halfrows
                cstart = (i%2)*halfcols
                cstop = cstart + halfcols
         #       print( ' c: ', cstart, ' - ' , cstop)
         #       print( ' r: ', rstart, ' - ' , rstop)
                volmap[rstart:rstop,cstart:cstop] = vol
        updatedmap = []    
        for well in thismap:
             well['mVolume'] = volmap[well['Row'],well['Col']]
             updatedmap.append(well)
        return updatedmap      

def populateLDVPlusFTVolumes(thismap, nrows, ncols, version):
    volmap = np.zeros([nrows,ncols])
    if ( nrows == 16 ):
       pattern0 = np.array([[4.5,6],[7,8]])
       pattern1 = np.array([[9,10],[12, 14]])
    if ( nrows == 32 ):
       pattern0 = np.array([[4,5],[4.5,5.5]])
       pattern1 = np.array([[1,2],[1.5,3]])
        
    patterns =[pattern0,pattern1,pattern0,pattern1]
        
    for i in range(0,4):
            volmap = fillquadrant(volmap,i,patterns[i],nrows,ncols)
            
        
        
    updatedmap = []    
    for well in thismap:
        well['mVolume'] = volmap[well['Row'],well['Col']]
        updatedmap.append(well)
    return updatedmap 

def populateLDVFTVolumes(thismap, nrows, ncols, version):
    volmap = np.zeros([nrows,ncols])
    
    if version == 3 :
        if (nrows == 16) :
            volumes = [6,4,8,10,7,2.75,9,12]
        else:
            # 1536 LDV
            volumes = [4,1,1.5,5.5,5,2,3,4.5]
        halfrow = nrows //2
        quartercol = ncols //4
        for i in range(0,2):
            for j in range(0,4):
                rstart = i*halfrow
                rstop = rstart + halfrow
                cstart = j*quartercol 
                cstop = cstart+ quartercol
                volmap[rstart:rstop,cstart:cstop] = volumes[i*4 + j ]
    else:    
        if ( nrows == 16 ):
            pattern0 = np.array([[2.75,4],[6,7]])
            pattern1 = np.array([[8,9],[10, 12]])
        if ( nrows == 32 ):
            pattern0 = np.array([[4,5],[4.5,5.5]])
            pattern1 = np.array([[1,2],[1.5,3]])
        
        patterns =[pattern0,pattern1,pattern0,pattern1]
        
        for i in range(0,4):
            volmap = fillquadrant(volmap,i,patterns[i],nrows,ncols)
            
        
        
    updatedmap = []    
    for well in thismap:
        well['mVolume'] = volmap[well['Row'],well['Col']]
        updatedmap.append(well)
    return updatedmap  

def populateLDVICPVolumes(thismap, nrows, ncols, version):
    if version == 3:
        colvols = [13,12,3.5,4,9,8,6.5,7,6,5,10,11]
        colvols += colvols
    else:    
        colvols=[13,13,12,12,3.5,3.5,4,4,9,9,8,8,6.5,6.5,7,7,6,6,5,5,10,10,11,11]
    if ( len(colvols) != ncols ) :
        print(' *** ERROR :: number of columns inconsistent ')
        return []
    updatedmap = []    
    for well in thismap:
        well['mVolume'] = colvols[well['Col']]
        updatedmap.append(well)
    return updatedmap    


def populateTRVolumes(thismap, nrows, ncols, colvols):    
   
    if ( len(colvols) != ncols ) :
        print(' *** ERROR :: number of columns inconsistent ')
        return []
    updatedmap = []    
    for well in thismap:
        well['mVolume'] = colvols[well['Col']]
        updatedmap.append(well)
    return updatedmap    

     
def populate1536LDVVolumes(thismap, nrows, ncols):
    volmap = np.zeros([nrows,ncols])
    pattern0 = np.array([[3.5,1.5],[1.2,2.0]])
    pattern1 = np.array([[2.5,3.5],[3.0,4.0]])
    pattern2 = np.array([[4.5,5.5],[5.0,6.0]])
    pattern3 = np.array([[2.0,1.2],[2.5,4.0]])
    patterns =[pattern0,pattern1, pattern2, pattern3]
    for i in range(0,4):
        volmap = fillquadrant(volmap,i,patterns[i],nrows,ncols)
    updatedmap = []    
    for well in thismap:
        well['mVolume'] = volmap[well['Row'],well['Col']]
        updatedmap.append(well)
    return updatedmap      
   
def populate1536LDVUCPVolumes(thismap, nrows, ncols):
    volmap = np.zeros([nrows,ncols])
    volumes = [4.5,5,5.5,6,2,2.5,1.2,4,3.5,1.2,1.5,2,4,3,3.5,2.5]
    quarterrow = nrows //4
    quartercol = ncols //4
    for i in range(0,4):
        for j in range(0,4):
            rstart = i*quarterrow
            rstop = rstart + quarterrow
            cstart = j*quartercol 
            cstop = cstart+ quartercol
            volmap[rstart:rstop,cstart:cstop] = volumes[ i*4 + j ]
    
    updatedmap = []    
    for well in thismap:
        well['mVolume'] = volmap[well['Row'],well['Col']]
        updatedmap.append(well)
    return updatedmap     

    
def fillquadrant(volmap,quadrant,pattern,nrows,ncols):
    if pattern.shape != (2,2) :
        print(' ** ERROR :: invalid pattern shape for function')
        return volmap
    halfrows = nrows//2
    halfcols = ncols//2
    righthalve =  quadrant%2
    bottomhalve = quadrant//2
    rstart = bottomhalve*halfrows 
    cstart =  righthalve*halfcols
    rstop = rstart + halfrows
    cstop = cstart + halfcols
#    print( ' c: ', cstart, ' - ' , cstop)
#    print( ' r: ', rstart, ' - ' , rstop)
    for i in range(0,2):
        for j in range(0,2):         
            volmap[rstart+j:rstop:2,cstart+i:cstop:2] = pattern[i][j]
    return volmap    
     
def concToImpedance(concentrations,fluid='DMSO'):    
    impedances = []
    conv = {}
    if ( fluid == 'DMSO' ):
        conv = {}
        conv['70'] = 1.83
        conv['75'] = 1.81
        conv['80'] = 1.78
        conv['85'] = 1.75
        conv['90'] = 1.71
        conv['95'] = 1.67
        conv['100'] = 1.63                
    if ( fluid.startswith('GLY')) or ( fluid.startswith('GPS') ) :
        conv = {}
        conv['0'] = 1.48
        conv['10'] = 1.59
        conv['20'] = 1.71
        conv['30'] = 1.82
        conv['40'] = 1.93
        conv['45'] = 1.96
        conv['50'] = 2.02
        conv['55'] = 2.06
        conv['100'] = 1.48
    if ( fluid.startswith('PBS')) or (fluid.startswith('AQ')):
        conv = {}
        conv['100'] = 1.48
    try:
        for c in concentrations:
            if str(c) in conv:
                impedances.append(conv[str(c)])
            else:
                impedances.append(c)
    except TypeError:
        c = concentrations
        if str(c) in conv:
            imp = conv[str(concentrations)]    
        else:
            imp = str(c)
        return imp         
    return impedances        
    
    
def wellsToRowCols(nwells):
    row1536 = list(map(chr, range(97, 97+26))) 
    row1536b = [ 'A' + x for x  in list(map(chr, range(97, 97+6))) ]
    row1536 = row1536 + row1536b
    row384 = list(map(chr, range(97, 97+16)))  
    row96 = list(map(chr, range(97, 97+8))) 
    rowRES = list(map(chr, range(97, 97+2))) 
    if nwells == 384 :
        nrows = 16
        ncols = 24
        rowletter = row384
    else:
        if nwells == 1536 :
            nrows = 32
            ncols = 48
            rowletter = row1536
        else :
            if nwells == 96:
                nrows = 8
                ncols = 12
                rowletter = row96
            else:
                nrows = 2
                ncols = 3
                rowletter =  rowRES
    return nrows, ncols, rowletter    


def writeMap(dfMap, platetype='384PP', nwells=384, geo='PP', style='FT', fluid='DMSO', conc='-', version='2', vol='-', fluidscale=False, fluidkey='PBS', ArenaPN = None):
    ''' Master function that takes a Pandas dataframe, writes CSV and generates a figure of the fillmap.
        The method returns a dictionary that corresponds to one line in the AllMaps.csv file. Here are the inputs:
        (note a good way to figure out all inputs is to simply open AllMaps.csv in Excel, you will then see all fields )    
            platetype: 384PPL, 384LDVS, 1536LDVS
            nwells: 6,96,384 or 1536
            geo: geometry, can be PP, LDV or GEO
            style: FT, FF, ICP, UCP, SIG, DD, HC
            fluid: see \BarCodes\FluidType.csv
            conc: concentration, '-' can be used if multiple concentrations are used
            version: a version number
            vol: for SIG or FF if one volume is specified, else can be '-'
            fluidscale: if False (default), the color scale axis on the graphs is based on concentration, 
                        if True, color scale asis is a different fluid ( typically done fore SP maps e.g. PBS5, PBS14)
            fluidkey: introduced to deal with GPS fluids for 525, typically PBS by default, for GPSA/GPSB fluids this should be GPS
            ArenaPN: arena part number, has to be of the form 'XXX-YYYYY', if not specified will be looked up in AllMaps.csv
                '''
    bc = barCodes.BarCodes()    
   # basedir='\\\\seg\\data\\PlateMaps'
    basedir = os.path.join(os.path.dirname(__file__), 'PlateMaps')
    if not os.path.exists(basedir):
        os.mkdir(basedir)
    writedir = basedir  + '\\\\' + platetype
    if not os.path.exists( writedir) :
        os.mkdir (writedir)
    if nwells > 384:
        scale = 2.0
    else:
        scale = 1
    fig, ax = plt.subplots(figsize=(12*scale, 8*scale))
    if ( (style=='FF') or (style=='DD') ):
        title = platetype + '__' + style + '__' + str(conc) + '__' + fluid + '__' + str(vol) + 'uL__v' + version
    else:    
        title = platetype + '__' + style + '__' + str(conc) + '__' + fluid + '__v' + version
    nr, nc, rl = wellsToRowCols(nwells)
    cols = [ i for i in range(0,nc)]
    entry = {}
    entry['PlateType'] = platetype
    entry['Style'] = style
    entry['Fluid'] = fluid
    entry['Conc'] = str(conc)
    entry['Version'] = str(version)
    
    entry['Vol'] = str(vol)
    entry['BarCode'] = bc.genGenericBarCode(entry)
    thisbarcode = entry['BarCode'][0:7]
    title = thisbarcode + '__' + title

# Looking for Arena Part Number::
    if not ArenaPN:
        arenaPmFile = basedir + '\\\\' + arenaFileName 
        arenaPmFrame = pandas.read_csv(arenaPmFile)
        arenaPmFrame['ShortBarcode'] = arenaPmFrame['BarCode'].apply(lambda x: str(x)[0:7] )
        subset = arenaPmFrame['Arena Part Number'][arenaPmFrame['ShortBarcode'] == thisbarcode]
        print(' title: ', title, ' subset: ', subset.values, ' thisbarcode: ', thisbarcode)
        if len(subset) == 0 :
            PN = 'XXX-YYYYY'
        else:
            if  (str(subset.values[0]) == 'nan' ):
                PN = 'XXX-YYYYY'
            else:
                PN = str(subset.values[0])
    else:
        if len(ArenaPN) == 9 and ArenaPN[3] == '-' :
            PN = ArenaPN
        else:
            PN = 'XXX-YYYYY'
            
    title =  PN + '__' + title 
    entry['Arena Part Number'] = PN
    
    plotMap(dfMap, rl, cols, title=title, ax = ax, fluidscale = fluidscale, fluidkey=fluidkey)
    
    filebase  = writedir +  '\\\\' + title 
    entry['Filename'] = filebase + '.csv'
    plt.savefig(filebase + '.png')
#    fig.close()
    dfMap.to_csv(filebase +'.csv', index=False)

    return entry


def gen384PP_Omics2Map():
    nwells = 384
    platetypes = ['384PPG_AQ_GP2','384PPL_AQ_GP2']
    version = '2'
    geo='PP'
    styles = ['SIG','UCP','ICP']
    fluid = 'GLY'
    concentrations_sig = [0,10,20,30,40,50,55]
    concentrations_ucp = [0,20,50]
    allmaps = []
    for platetype in platetypes:
        for s in styles:
            if ( s == 'ICP' ) :
                m = genMap(wells=384,geo=geo,style=s,fluid=fluid,version=version)
                thisentry = writeMap(m,platetype=platetype, nwells=nwells, geo=geo,style=s,fluid=fluid,conc='-',version=version)
                allmaps.append(thisentry)
            else :    
                if ( s == 'UCP' ):
                     cc = concentrations_ucp
                if ( s == 'SIG' ):
                     cc = concentrations_sig
                for c in cc :
                     m = genMap(wells=nwells,geo=geo,style=s,fluid=fluid,conc=c,version=version)
                     thisentry = writeMap(m,platetype=platetype, nwells=nwells, geo=geo,style=s,fluid=fluid,conc=c,version=version)
                     allmaps.append(thisentry)
    # Final Test Plates             
    style='FT'
    platetypes=['384PPG_AQ_BP2','384PPL_AQ_BP2']
    concentrations=[0,10,30]
    fluid='GLY'
    for platetype in platetypes:
        for c in concentrations:
           m = genMap(wells=nwells,geo=geo,style=style,fluid=fluid,conc=c,version=version)
           thisentry = writeMap(m,platetype=platetype, nwells=nwells, geo=geo,style=style,fluid=fluid,conc=c,version=version)
           allmaps.append(thisentry)  
       
    platetypes=['384PPG_AQ_GP2','384PPL_AQ_GP2']
    concentrations=[20,40,50]
    for platetype in platetypes:
        for c in concentrations:
           m = genMap(wells=nwells,geo=geo,style=style,fluid=fluid,conc=c,version=version)
           thisentry = writeMap(m,platetype=platetype, nwells=nwells, geo=geo,style=style,fluid=fluid,conc=c,version=version)
           allmaps.append(thisentry)
           
    platetypes=['384PPG_AQ_CP','384PPL_AQ_CP']    
    fluids=['AQ','2.4M-HEPES','PEG-3350','MPD']
    impedance=[1.48,2.25,1.76,1.55]
    style='FT'
    concentrations=[100,100,30,50]
    for platetype in platetypes:
        for i,c in enumerate(concentrations):
           m = genMap(wells=nwells,geo=geo,style=style,fluid=fluids[i],conc=c,version=version,impedance=impedance[i])
           thisentry = writeMap(m,platetype=platetype, nwells=nwells, geo=geo,style=style,fluid=fluids[i],conc=c,version=version)
           allmaps.append(thisentry)  
           
         
    style = 'FF'
    version = '2'
    fluid = '2.4M-HEPES'
    impedance=2.25
    concentration=100
    for platetype in platetypes:
        m = genMap(wells=nwells,geo=geo,style=style,fluid=fluid, conc=concentration, version=version, impedance=impedance, volume='40')
        thisentry = writeMap(m,platetype=platetype, nwells=nwells, geo=geo,style=style,fluid=fluid,conc=concentration,version=version, vol='40')
        allmaps.append(thisentry)

    platetypes=['384PPG_AQ_SP2','384PPL_AQ_SP2']
    fluids=['PBS5','PBS14','PBS200']
    concentration=100
    for platetype in platetypes:
        for i,f in enumerate(fluids):
           m = genMap(wells=nwells,geo=geo,style='FT',fluid=f,conc=concentration,version=version,impedance=1.48)
           thisentry = writeMap(m,platetype=platetype, nwells=nwells, geo=geo,style='FT',fluid=f,conc=concentration,version=version)
           allmaps.append(thisentry) 
        style = 'ICP'
        m = genMap(wells=nwells,geo=geo,style=style,fluid='PBS14',conc=concentration,version=version, impedance=1.48)
        thisentry = writeMap(m,platetype=platetype, nwells=nwells, geo=geo,style=style,fluid='PBS14',conc=concentration,version=version)
        allmaps.append(thisentry)
        style = 'UCP'
        version = '3'
        m = genMap(wells=nwells,geo=geo,style=style,fluid='PBS', conc=concentration, version=version, impedance=1.48)
        thisentry = writeMap(m,platetype=platetype, nwells=nwells, geo=geo,style=style,fluid='PBS',conc=concentration,version=version,fluidscale=True)
        allmaps.append(thisentry)
        style = 'FF'
        version = '2'
        fluid = 'PBS5'
        m = genMap(wells=nwells,geo=geo,style=style,fluid=fluid, conc=concentration, version=version, impedance=1.48, volume='40')
        thisentry = writeMap(m,platetype=platetype, nwells=nwells, geo=geo,style=style,fluid=fluid,conc=concentration,version=version, vol='40')
        allmaps.append(thisentry)
   
    platetypes=['384PPG_AQ_BP','384PPL_AQ_BP']
    geo = 'PP'
    style = 'FT'
    fluid = 'GLY'
    concentration = 0
    version = '1'
    nwells = 384        
    for p in platetypes:                
        m = genMap(wells=nwells,geo=geo,style=style,fluid=fluid,conc=concentration,version=version)
            # version = 1 above is superceded here by plate type 384PP_DMSO
        thisentry = writeMap(m,platetype=p, nwells=nwells, geo=geo,style=style,fluid=fluid,conc=concentration,version=version)
        allmaps.append(thisentry)
     
    platetypes=['384PPG_AQ_SP','384PPL_AQ_SP']
    geo = 'PP'
    style = 'FT'
    fluid = 'GLY'
    concentration = 0
    version = '1'
    nwells = 384  
    fluids=['PBS5','PBS14','PBS200']
    concentration=100
    for p in platetypes:
        for i, f in enumerate(fluids):
            m = genMap(wells=nwells,geo=geo,style=style,fluid=f,conc=concentration,version=version)
                # version = 1 above is superceded here by plate type 384PP_DMSO
            thisentry = writeMap(m,platetype=p, nwells=nwells, geo=geo,style=style,fluid=f,conc=concentration,version=version)
            allmaps.append(thisentry) 
    
            
    style='HC'
    f='PBS'        
    plate='384PPG_HC'
    version= '2'
    m = genMap(wells=384,geo='PP',style=style,version=version,fluid=f)        
    thisentry = writeMap(m, platetype=plate,fluid=f,style=style,version=version)
    allmaps.append(thisentry)
    plate='384PPL_HC'
    m = genMap(wells=384,geo='PP',style=style,version=version,fluid=f)        
    thisentry = writeMap(m, platetype=plate,fluid=f,style=style,version=version)
    allmaps.append(thisentry)
    return allmaps  

def genLDVAQMaps():
    platetype='384LDVS_AQ_B2'
    version='2'
    fluid = 'AQ'
    wells = 384
    geo = 'LDV'
    concentration=100
    impedance=1.48
    allmaps = []
    m = genMap(wells=wells,geo=geo,style='ICP',fluid=fluid,conc=concentration,version=version)
    thisentry = writeMap(m,platetype=platetype, nwells=wells, geo=geo,style='ICP',fluid=fluid,conc=concentration,version=version)
    allmaps.append(thisentry)
    style='FF'
    for vol in [2.75,4,6,7,8,9,10,12]:
        m = genMap(wells=wells,geo=geo,style=style,fluid=fluid,conc=concentration,version=version,volume=vol,impedance=impedance)
        thisentry = writeMap(m,platetype=platetype, nwells=wells, geo=geo,style=style,fluid=fluid,conc=concentration,version=version,vol=vol)
        allmaps.append(thisentry)
    return allmaps

def genLDVPlusGPMaps():
    platetype='384LDVS_PLUS_AQ_GP'
    version='2'
    wells = 384
    geo = 'LDV'
    fluid = 'GLY'
    allmaps = []
    m = genMap(wells=wells,geo=geo,style='UCP',fluid=fluid,version=version, instrument='525')
    thisentry = writeMap(m,platetype=platetype, nwells=wells, geo=geo, style='UCP',fluid=fluid,version=version)
    allmaps.append(thisentry)
    concentrations = [0,10,20,30,40,50]
    for c in concentrations:
        m = genMap(wells=wells,geo=geo,style='FT',conc=c,fluid=fluid,version=version)
        thisentry = writeMap(m,platetype=platetype, nwells=wells, geo=geo, style='FT',conc=c,fluid=fluid,version=version)
        allmaps.append(thisentry)
    vol=14
    style='DD'    
    m = genMap(wells=wells,geo=geo,style=style,fluid=fluid,version='3',volume=vol)
    thisentry = writeMap(m,platetype=platetype,nwells=wells, geo=geo, style=style,fluid=fluid,version='3',vol=vol)
    allmaps.append(thisentry)    
    return allmaps   
    
def genLDVGPMaps():    
    platetype='384LDVS_AQ_GP'
    version='2'
    wells = 384
    geo = 'LDV'
    fluid = 'GLY'
    allmaps = []
    concentrations = [0,10,20]
    for c in concentrations:
        m = genMap(wells=wells,geo=geo,style='UCP',fluid=fluid,version=version,conc=c)
        thisentry = writeMap(m,platetype=platetype,nwells=wells,geo=geo,style='UCP',fluid=fluid,conc=c,version=version)
        allmaps.append(thisentry)
    return allmaps    
    
def genDMSO2Maps():
    nwells = [384,1536]
 #   platetypes = ['384PPG_DMSO2','384PPL_DMSO2']
    version='2'
    geo= ['PPG','PPL','LDV','HB']
    styles = ['SIG','UCP','ICP','FT']
    fluid = ['DMSO']
    concentrations = [70,75,80,85,90,95,100]
    allmaps = []
    for g in geo:
        for w in nwells:
            if ( g.startswith('PP')) and (w==1536):
                continue
            if ( g.startswith('PP') ):
                platetype = str(w) + g + '_DMSO2'
                gs = 'PP'
            else:
                if ( g.startswith('HB') and (w==384)):
                    continue
                platetype = str(w) + g + 'S_DMSO'
                gs = g
            for f in fluid:
                for s in styles:
                    if   (( s == 'FT' ) or ( s == 'SIG' ) ):
                        if ( s == 'SIG' ) and ( gs == 'HB' ):
                            continue
                        for c in concentrations:
                            m = genMap(wells=w,geo=gs,style=s,fluid=f,conc=c,version=version)
                            thisentry = writeMap(m,platetype=platetype, nwells=w, geo=gs,style=s,fluid=f,conc=c,version=version)
                            allmaps.append(thisentry)
                    else :
                        m = genMap(wells=w,geo=gs,style=s,fluid=f,version=version)
                        thisentry = writeMap(m,platetype=platetype, nwells=w, geo=gs,style=s,fluid=f,conc='-',version=version)
                        allmaps.append(thisentry)
    
    #version 1 of UCP plates are the same as ICP                    
    version='1'                    
    styles = ['UCP']
    nwells = [1536]
    geo = ['LDV','HB']
    for g in geo:
      for w in nwells:
          if ( g.startswith('PP')) and (w==1536):
              continue
          if ( g.startswith('PP') ):
              platetype = str(w) + g + '_DMSO2'
              gs = 'PP'
          else:
              platetype = str(w) + g + 'S_DMSO'
              gs = g
          for f in fluid:
              for s in styles:
                 if   (( s == 'FT' ) or ( s == 'SIG' ) ):
                    if ( s == 'SIG' ) and ( gs == 'HB' ):
                        continue
                    for c in concentrations:
                        m = genMap(wells=w,geo=gs,style=s,fluid=f,conc=c,version=version)
                        thisentry = writeMap(m,platetype=platetype, nwells=w, geo=gs,style=s,fluid=f,conc=c,version=version)
                        allmaps.append(thisentry)
                 else :
                    m = genMap(wells=w,geo=gs,style=s,fluid=f,version=version)
                    thisentry = writeMap(m,platetype=platetype, nwells=w, geo=gs,style=s,fluid=f,conc='-',version=version)
                    allmaps.append(thisentry)
    
                        
    geo = ['PPG','PPL']
    style = 'FT'
    fluid = 'DMSO'
    version = '1'
    nwells = 384        
    for g in geo:                
        for c in concentrations:
            m = genMap(wells=nwells,geo=g[0:2],style=style,fluid=fluid,conc=c,version='1')
            # version = 1 above is superceded here by plate type 384PP_DMSO
           # version='2'
            p = '384' + g + '_DMSO'
            thisentry = writeMap(m,platetype=p, nwells=nwells, geo=g,style=style,fluid=fluid,conc=c,version=version)
            allmaps.append(thisentry)
        
    return allmaps

def genPPPlusGPMaps():
    nwells = 384
    platetypes = ['384PPG_PLUS_AQ_GP','384PPL_PLUS_AQ_GP']
    version = '2'
    geo= 'PP'

    for i, platetype in enumerate(platetypes):    
        fluid='GLY'
    
        allmaps = []
        
    
        style='SIG'
        concentrations = [0,10,20,30,40,50,55]
        for c in concentrations:
            m = genMap(wells=nwells,geo=geo,style=style,fluid=fluid,conc=c,version=version)
            thisentry = writeMap(m,platetype=platetype, nwells=nwells, geo=geo, style=style, fluid=fluid, conc=c,version=version)
            allmaps.append(thisentry)
    
        style='ICP'
        m = genMap(wells=nwells,geo=geo,style=style,fluid=fluid,conc='-',version=version)
        thisentry = writeMap(m,platetype=platetype, nwells=nwells, geo=geo, style=style, fluid=fluid, conc='-',version=version)
        allmaps.append(thisentry)
    
        style = 'FT'
        concentrations =  [10, 20, 30, 40, 50]
        for c in concentrations:
            m = genMap(wells=nwells,geo=geo,style=style,fluid=fluid,conc=c,version='1')
            m['mVolume'][m['mVolume']==50] = 65
            thisentry = writeMap(m,platetype=platetype, nwells=nwells, geo=geo, style=style, fluid=fluid, conc=c,version=version)
            allmaps.append(thisentry)
        
        style='DD'
        vol=60
        fluid += '-DF'
        m = genMap(wells=nwells,geo=geo,style=style,fluid=fluid,conc='-',version='3',volume=vol)
        thisentry = writeMap(m,platetype=platetype, nwells=nwells, geo=geo, style=style, fluid=fluid, conc='-',version='3', vol=vol) 
        allmaps.append(thisentry)
        
    return allmaps    

def genPPSPBPPlusMaps():
    nwells = 384
    platetypes = [ '384PPG_PLUS_AQ_SP', '384PPG_PLUS_AQ_BP', '384PPL_PLUS_AQ_SP', '384PPL_PLUS_AQ_BP' ]
    geo='PP'
    version='2'
    fluids = ['PBS14','PBS']
    vols = [20,30,40,65]
   
    allmaps = []
    
    impedance = 1.48
    
    for i, platetype in enumerate(platetypes):
        fluid = fluids[i%2]
        style = 'FT' 
        # note version number here ! version 1 tricks vols to be 20,30,40,50         
        # overwrite 15
       
        m = genMap(wells=nwells,geo=geo,style=style,fluid=fluid,conc=100,impedance=impedance,version='1')
        m['mVolume'][m['mVolume']==50] = 65
        thisentry = writeMap(m,platetype=platetype, nwells=nwells, geo=geo, style=style, fluid=fluid, conc=100, version=version)
        allmaps.append(thisentry)    
    
        style = 'FF'
        for v in vols:
            m = genMap(wells=nwells,geo=geo,style=style,fluid=fluid,conc=100,version=version, volume=v)
            thisentry = writeMap(m,platetype=platetype, nwells=nwells, geo=geo, style=style, fluid=fluid, conc=100,vol=v,version=version)
            allmaps.append(thisentry)
            
        style='DD'
        vol=60   
        fluid += '-DF'
        m = genMap(wells=nwells,geo=geo,style=style,fluid=fluid,conc=100,version='3', volume=vol)
        thisentry = writeMap(m,platetype=platetype, nwells=nwells, geo=geo, style=style, fluid=fluid, conc=100,vol=vol,version='3')
        allmaps.append(thisentry)
    return allmaps

def gen525SPMaps():
    nwells = 384
    platetypes = ['384PPG_AQ_SP_High','384PPG_AQ_SP','384PPL_AQ_SP_High','384PPL_AQ_SP']
    geo='PP'
    version='2'
    
    allmaps = []
    # ICP plat e actually is FT plate
    style='FT'
    fluids = ['PBS200','PBS14']
    concentration=100
    impedance=1.48
    
    for i in range(0,len(platetypes)):
        fluid = fluids[i%len(fluids)] 
        style='FT'
        platetype = platetypes[i]
        # note version number here ! version 1 tricks vols to be 20,30,40,50 
        m = genMap(wells=nwells,geo=geo,style=style,fluid=fluid,conc=concentration,impedance=impedance,version='1')
       # overwrite 15
        m['mVolume'][m['mVolume']==50] = 65
        thisentry = writeMap(m,platetype=platetype, nwells=nwells, geo=geo, style=style, fluid=fluid, conc=concentration,version=version)
        allmaps.append(thisentry)
        
        vols = [20,30,40,65]
        style = 'FF'
        
        for v in vols:
            m = genMap(wells=nwells,geo=geo,style=style,fluid=fluid,conc=concentration,impedance=impedance,version=version, volume=v)
            thisentry = writeMap(m,platetype=platetype, nwells=nwells, geo=geo, style=style, fluid=fluid, conc=100,vol=v,version=version)
            allmaps.append(thisentry)
            
        style='DD'
        vol=60 
        fluid += '-DF'
        m = genMap(wells=nwells,geo=geo,style=style,fluid=fluid,conc=concentration,impedance=impedance,version='3', volume=vol)
        thisentry = writeMap(m,platetype=platetype, nwells=nwells, geo=geo, style=style, fluid=fluid, conc=100,vol=vol,version='3')
        allmaps.append(thisentry)
        
    return allmaps

def gen525BPMaps():
    nwells = 384
    platetypes = ['384PPG_AQ_BP','384PPL_AQ_BP']
    geo='PP'
    version='2'
    
    allmaps = []
    # dimpleping map
    style='FF'
    fluid='PBS'
    concentration=100
    vol=40
    for platetype in platetypes:
        style='FF'
        fluid = 'PBS'
        m = genMap(wells=nwells,geo=geo,style=style,fluid=fluid,conc=concentration,version=version, volume=vol)
        thisentry = writeMap(m,platetype=platetype, nwells=nwells, geo=geo, style=style, fluid=fluid, conc=concentration,vol=vol,version=version)
        allmaps.append(thisentry)
    
        vols = [20,30,40,65]
        style = 'FF'
        allmaps = []
        for v in vols:
            m = genMap(wells=nwells,geo=geo,style=style,fluid=fluid,conc=100,version=version, volume=v)
            thisentry = writeMap(m,platetype=platetype, nwells=nwells, geo=geo, style=style, fluid=fluid, conc=100,vol=v,version=version)
            allmaps.append(thisentry)
            
        style='DD'
        vol=60   
        fluid = 'PBS-DF'
        m = genMap(wells=nwells,geo=geo,style=style,fluid=fluid,conc=100,version='3', volume=vol)
        thisentry = writeMap(m,platetype=platetype, nwells=nwells, geo=geo, style=style, fluid=fluid, conc=100,vol=vol,version='3')
        allmaps.append(thisentry)
    return allmaps

def gen525Lemonade():
    allmaps = []
    nwells = 384
    version = '2'
    geo = 'PP'
    style = 'UCP'
    concentrations = [0,10,20,50]
    platetypes = ['384PPL_PLUS_AQ_GP','384PPG_PLUS_AQ_GP']
    for p in platetypes:
        for i,c in enumerate(concentrations):
            m = genMap(wells=nwells,geo=geo,style=style,fluid='GLY',conc=c, version = version,instrument='525')
            thisentry = writeMap(m, platetype=p, nwells=nwells, geo=geo, style=style, fluid='GLY', fluidscale=True, fluidkey='GPS', conc=c, version=version)
            allmaps.append(thisentry)
      
    platetypes = ['384PPL_AQ_SP','384PPG_AQ_SP']  
    for p in platetypes:
        m = genMap(wells=nwells,geo=geo,style=style,fluid='PBS',conc=100, impedance=1.48, version = version, instrument='525')  
        thisentry = writeMap(m, platetype=p, nwells=nwells, geo=geo, style=style, fluid='PBS', conc='100', fluidscale=True, version=version)
        allmaps.append(thisentry)
    return allmaps
    
def genPPPlusMaps():
    nwells = 384
    platetypes = ['384PPG_PLUS_AQ_GPSA','384PPG_PLUS_AQ_GPSB','384PPL_PLUS_AQ_GPSA','384PPL_PLUS_AQ_GPSB']
    version='2'
    geo='PP'
   
    fluids = ['GPS14','GPS25']
    allmaps = []
    for i,p in enumerate(platetypes):
        platetype = p
        fluid = fluids[i%2]
        style = 'ICP'
        m = genMap(wells=nwells,geo=geo,style=style,fluid=fluid,conc='-',version=version)
        thisentry = writeMap(m,platetype=platetype, nwells=nwells, geo=geo, style=style, fluid=fluid, conc='-',version=version)
        allmaps.append(thisentry)
         
        style = 'FT'
        concentrations =  [10, 20, 30, 40, 50]
        
        for c in concentrations:
            # version number trick
            m = genMap(wells=nwells,geo=geo,style=style,fluid=fluid,conc=c,version='1')  
            m['mVolume'][m['mVolume']==50] = 65
            thisentry = writeMap(m,platetype=platetype, nwells=nwells, geo=geo, style=style, fluid=fluid, conc=c,version=version)
            allmaps.append(thisentry)
            
        style='DD'
        fluid += '-DF'
        vol=60
        m = genMap(wells=nwells,geo=geo,style=style,fluid=fluid,conc='-',version='3',volume=vol)
        thisentry = writeMap(m,platetype=platetype, nwells=nwells, geo=geo, style=style, fluid=fluid, conc='-',version='3', vol=vol) 
        allmaps.append(thisentry)
    return allmaps 

def genAllTRXMaps():
  
  
    plate = {}
    plate['platetype'] = '96TRK_DMSO'
    plate['fluids'] = [ 'DMSO' ]
    plate['concentrations'] = [ 70, 75, 80, 85, 90, 95, 100]
    plate['version'] = '1'
    plate['volumes'] =  [ '20', '55', '95']
    plate['styles'] = [ 'UCP', 'FF', 'FT'] 
    dmsomap =  genTRXMap(plate)
    
    plate = {}
    plate['platetype'] = '96TRK_AQ_GP'
    plate['fluids'] =   [ 'GLY' ]
    plate['concentrations'] = [ 0, 10, 20, 30, 40, 45, 50, 55]
    plate['version'] = '1'
    plate['volumes'] =  [ '20', '55', '95']
    plate['styles'] = [ 'UCP', 'FF', 'FT'] 
    gpmap = genTRXMap(plate)
    
    plate = {}
    plate['platetype'] = '96TRK_AQ_SP'
    plate['fluids'] = ['PBS5','PBS14','PBS200']
    plate['concentrations'] = [ 100 ]
    plate['version'] = '1'
    plate['volumes'] =  [ '20', '55', '95']
    plate['styles'] = [ 'UCP', 'FF', 'FT'] 
    spmap = genTRX_SPMap(plate)
#    
    allmaps = dmsomap + gpmap + spmap

    return allmaps
    
def genTRXMap(platedict):
    nwells = 96
    geo = 'TR'
    allmaps = []
    styles = platedict['styles']    
    concentrations = platedict['concentrations']
    volumes = platedict['volumes']
    platetype = platedict['platetype']
    fluids = platedict['fluids']
    version = platedict['version']
    for fluid in fluids:
        for style in styles:
            for c in concentrations:
                if style == 'FF' :
                    for v in volumes:
                        m = genMap(wells=nwells, geo=geo, style=style, fluid=fluid, version=version,  conc = c, volume=v)
                        thisentry = writeMap(m, platetype=platetype, nwells=nwells, geo=geo, style=style,  fluid=fluid, conc=c, vol=v, version= version)
                        allmaps.append(thisentry)
                else:        
                    m = genMap(wells=nwells, geo=geo, style=style, fluid=fluid, version=version, conc = c )
                    thisentry = writeMap(m, platetype=platetype, nwells=nwells, geo=geo, style=style, fluid=fluid, conc=c,  version= version)
                    allmaps.append(thisentry)
 
    return allmaps

def genTRX_SPMap(platedict):
    nwells = 96
    geo = 'TR'
    allmaps = []
    styles = platedict['styles']    
    concentrations = platedict['concentrations']
    volumes = platedict['volumes']
    platetype = platedict['platetype']
    fluids = platedict['fluids']
    version = platedict['version']
    for fluid in fluids:
        for style in styles:
            for c in concentrations:
                if style == 'FF' :
                    for v in volumes:
                        m = genMap(wells=nwells, geo=geo, style=style, fluid=fluid, version=version, impedance= 1.48, conc = c, volume=v)
                        thisentry = writeMap(m, platetype=platetype, nwells=nwells, geo=geo, style=style, fluidscale=True, fluid=fluid, conc=c, vol=v, version= version)
                        allmaps.append(thisentry)
                else:        
                    m = genMap(wells=nwells, geo=geo, style=style, fluid=fluid, version=version, conc = c, impedance=1.48)
                    thisentry = writeMap(m, platetype=platetype, nwells=nwells, geo=geo, style=style, fluid=fluid, conc=c, fluidscale=True, version= version)
                    allmaps.append(thisentry)
 
    return allmaps
     
def genResMaps():
    nwells= 6
    geo = 'RES'
    allmaps = []
    platetypes = [ '6RESP_AQ_BP2', '6RESP_AQ_GPSA2', '6RESP_AQ_GPSB2' ]    
    style = 'ICP'
    version = '2'
    fluids= [ 'GLY', 'GPS30' , 'GPS50']
    for i,p in enumerate(platetypes):
        fluid=fluids[i]
        m = genMap(wells=nwells,geo='RES',style=style,fluid=fluid,version=version, volume=2000)
        for i,r in m.iterrows():
            if (r.Row == 0) :
                conc = 10 
            else:
                conc = 30
            m.loc[i, 'mConc'] = conc
            m.loc[i, 'mImpedance'] = concToImpedance(conc,r.mFluid)
        thisentry = writeMap(m,platetype=p, nwells=nwells, geo=geo, style=style, fluid=fluid, conc='-',version=version)
        allmaps.append(thisentry)
    
    style = 'DD'
    platetypes_mpp = [ '6RESP_AQ_BP2', '6RESP_AQ_GPSA2', '6RESP_AQ_GPSB2', '6RESP_AQ_GPSB2' ] 
    fluids_mpp = [ 'GLY', 'GPS5', 'GPS30' , 'GPS50']
    platetypes_dd = [ '6RESP_AQ_BP2', '6RESP_AQ_GPSA2', '6RESP_AQ_GPSB2' ] 
    fluids_dd = [ 'GLY-T', 'GPS10-T', 'GPS50-T' ]
    vols = [ 2000, 2172]
    # ' MPP' plates are actually DD at 2 ml
    for ii,v in enumerate(vols):
       if (ii == 0):
         platetypes =  platetypes_mpp
         fluids = fluids_mpp
       else:
         platetypes = platetypes_dd
         fluids = fluids_dd
       
       for i,p in enumerate(platetypes):
            fluid=fluids[i]
            m = genMap(wells=nwells,geo='RES',style=style,fluid=fluid,version=version, volume=v)
            for i,r in m.iterrows():
                if (r.Col == 0 ):
                    conc = 0 + 20 *r.Row
                    vol = r.mVolume
                else :
                    if (r.Col == 1):
                        conc = 10 + 20*r.Row
                        vol = r.mVolume
                    else : 
                        vol = 0
                m.loc[i, 'mConc'] = conc
                m.loc[i, 'mImpedance'] = concToImpedance(conc,r.mFluid)
                m.loc[i, 'mVolume'] = vol
            thisentry = writeMap(m,platetype=p, nwells=nwells, geo=geo, style=style, fluid=fluid, conc='-',version=version, vol=v)
            allmaps.append(thisentry)
    
    platetype = '6RESP_AQ_BP2'
    concentrations = [0,10,20,30,40]
    style='SIG'
    fluid='GLY'
    for c in concentrations:
        m = genMap(wells=nwells,geo=geo,style=style,fluid=fluid,conc=c,version=version, volume=2000)         
        thisentry = writeMap(m,platetype=platetype, nwells=nwells, geo=geo, style=style, fluid=fluid, conc=c,version=version)
        allmaps.append(thisentry)
    return allmaps    
        
        
        
def genAllMaps(datespecific=False):
      ''' Master Function that will generate all platemaps. Note: The code takes a while to run. 
          AllMaps.csv will be re-generated'''
      DMSO_MAPS = genDMSO2Maps()
      LDVS_PLUS_MAPS = genLDVPlusGPMaps()
      LDVS_GP_MAPS = genLDVGPMaps()
      OMICS_MAPS = gen384PP_Omics2Map()
      LDVAQ_MAPS = genLDVAQMaps()
      PPS_MAPS = genPPSPBPPlusMaps()
      GPPLUS_MAPS = genPPPlusGPMaps()
      GPSPLUS_MAPS = genPPPlusMaps()
      e525_BPMAPS = gen525BPMaps()
      e525_SPMAPS = gen525SPMaps()
      e525_LEMONADE = gen525Lemonade()
 #     ALLMAPS = OMICS_MAPS
      RES_MAPS = genResMaps()
      TRK_MAPS = genAllTRXMaps()
      ALLMAPS = DMSO_MAPS + OMICS_MAPS + LDVAQ_MAPS + LDVS_PLUS_MAPS + LDVS_GP_MAPS
      ALLMAPS += PPS_MAPS + GPSPLUS_MAPS + GPPLUS_MAPS + e525_BPMAPS + e525_SPMAPS + RES_MAPS + e525_LEMONADE + TRK_MAPS
      ALLMAPS = LDVAQ_MAPS
      return writeAllMaps(ALLMAPS,datespecific)
      
def writeAllMaps(MapList, datespecific=False):
      ALLMAPSFrame = pandas.DataFrame(MapList)
      cols=['BarCode','PlateType','Style','Fluid','Conc','Vol','Version','Filename','Arena Part Number']
      date = datetime.datetime.now().strftime('%Y%m%d') 
      basedir = os.path.join(os.path.dirname(__file__), 'PlateMaps')
      ALLMAPSFromFile =  pandas.read_csv(basedir + '\\\\AllMaps.csv')
      ALLMAPSDataFrame = pandas.concat([ALLMAPSFrame, ALLMAPSFromFile])
      ALLMAPSDataFrame = ALLMAPSDataFrame.drop_duplicates(subset=['BarCode','PlateType','Style','Vol'])
      if (datespecific):
          filename = basedir + '\\AllMaps' + '_' + date + '.csv'
      else:
          filename = basedir + '\\AllMaps.csv'
          filename2 = basedir + '\\AllMaps' + '_' + date + '_Arena.csv'
          # back up just in case
          shutil.copy2(filename,filename2)
      ALLMAPSDataFrame[cols].to_csv(filename, index=False)
      return ALLMAPSFrame[cols]

# note::
# reprocess a certain part (e.g. because of bug or issue change)    
#    m = genMaps.genLDVPlusGPMaps()
#    M = genMaps.writeAllMaps(m)
  
