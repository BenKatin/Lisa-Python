# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 08:06:32 2015

@author: avandenbroucke
"""

import xlrd
from xlrd.sheet import ctype_text
import numpy as np
import matplotlib.pyplot as plt
import os

transdir='\\\\fserver\\picodocs\\Projects_2016-17\\Transducer_Swap\\Transducers'


def openbook(filename):
    "Open Excel file and return list of sheetnames"
    xl_workbook = xlrd.open_workbook(filename)
    return xl_workbook
    
def processrow(sheet,rownr,startcolumn,endcolumn):
    "Returns row from startcolumn to endcolumn in sheet as list"
    row = sheet.row(rownr)
    r = []
    for idx, cell_obj in enumerate (row):
#        cell_type_str = ctype_text.get(cell_obj.ctype, 'unknown type')
        if (idx >= startcolumn) and (idx < endcolumn):
            r.append(cell_obj.value)
#        print('(%s) %s %s' % (idx, cell_type_str, cell_obj.value))
    return r

 
def processbook(filename,ncols=24,ylo=40,yhi=70,startdb=-0.85,step=0.075):
    xlfile = openbook(filename)
    sheets = xlfile.sheet_names()
    valuesheets = []
    for i,val in enumerate(sheets):
        if val.endswith('_grf'):
            i += 1
            valuesheets.append(sheets[i])
            print(sheets[i])      

def OpenBooks(workbook1='./MEDMAN_20151109115944.xls', workbook2='../ZOE/Zoedb.xlsx', platetype='384PP_DMSO2'):
    # hardcoded nr books for now:
    nbooks = 2    

# open the excel files and store in list:
    books = [None] * nbooks
    books[0] = openbook(workbook1)
    books[1] = openbook(workbook2)
    
    booknames=[None]*nbooks
    booknames[0] = workbook1.rsplit('/')[-1].rsplit('.x')[0]
    booknames[1] = workbook2.rsplit('/')[-1].rsplit('.x')[0]   
    
    return books, booknames

def SignatureAnalysis(books, booknames, platetype='384PP_DMSO2'):

    nbooks = len(books)
    
# open both PlateSignature and PingParamerersheet and store in list:
    PlateSigSheet = [None]*nbooks
    PingParaSheet = [None]*nbooks
    for i,var in enumerate(books): 
        PlateSigSheet[i] = books[i].sheet_by_name('PlateSignature')
        PingParaSheet[i] = books[i].sheet_by_name('PingParameters')
        
# Get PingAmplitude data and store in list
# PingPara is 3d : 
#  dim0: database, dim1: #of columns in db for this platetype ( 1 in this case), dim2: cols in each row        
    PingParaData = [None]*nbooks    
    for i,var in enumerate(PingParaSheet):
        PingParaData[i] = processSheet(var, platetype,2, 5,4)
        print(PingParaData[i])
 
# Extract pingAmp, TOF, and Dimple info
    pingAmp = [None]*nbooks
    TOF = [None]*nbooks
    Dimple = [None]*nbooks
    PA = [None]*nbooks
    for i in range(0,nbooks):
        pingAmp[i] = PingParaData[i][0][0]
        TOF[i] = PingParaData[i][0][1] + ( PingParaData[i][0][2] - PingParaData[i][0][1])/2.
        Dimple[i] = PingParaData[i][0][4]
        PA[i] = booknames[i] + ': PingAmp: ' + str(pingAmp[i]) + ' TOF: ' + str(TOF[i]) + ' PingFile: ' + str(Dimple[i])
        
# Get Signature data and store in list        
    PlateSigData = [None]*nbooks    
    for i,var in enumerate(PlateSigSheet):
        PlateSigData[i] = processSheet(var, platetype,2, 5,6)    

# Extract Fit parameters ( all potential four, i.e. up to 3rd order poly ):
# fitpar will be 3dim matrix. dim0 corresponds to DB, dim1 gives fitparnr, dim2 is actual data
    fitpar = []
    for k in range(0,nbooks):
        new = [] 
        for i in range(0,4):
          fp = [row[i+1] for row in PlateSigData[k]]
          new.append(fp)
#          print(' size of new : ', len(new))  
        fitpar.append(new)
#        print(' size of fitpar : ', len(fitpar))        
        
    npfitpar = np.array(fitpar)

# let's plot some data:
    nrows = 3
    ncols = 3
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(12,8))
    plottitle = PA[0] + '\n' + PA[1]
    st = fig.suptitle(plottitle,fontsize='large')
    #rows: plots of fit parameter p_i
    off = 1 
    nbins=25
    labels = [None]*nbooks
    for i in range(0,nbooks):
        labels[i] = booknames[i].rsplit("_")[0]
        
    for i in range(0,nrows):
        # just plot the distribution of fit parameters
        #colors = ['g','r']
        axes[i,0].hist([npfitpar[0][off+i], npfitpar[1][off+i]], nbins, alpha=0.5, color=['g','r'], label=labels)
        axes[i,0].legend(prop={'size': 10})
        title = "P" + str(3-(i+off))        
        #axes[i,0].set_title(title)        
        # plot a distribution of the difference
        diff = npfitpar[0][off+i] - npfitpar[1][off+i]
        axes[i,1].hist(diff, nbins, color='b')
#        tit = labels[0] + ' - ' + labels[1]
#        axes[i,1].set_title(tit)
        # plot difference as a function of well id
        axes[i,2].plot(diff)
        axes[i,0].set_xlabel(title)
        difftitle = '(' + title + '-' + labels[0] + ') - (' + title + '-' +labels[1] + ')'
        axes[i,1].set_xlabel(difftitle)
        for jj in range(0,2):
            axes[i,jj].set_ylabel('Entries')
        axes[i,2].set_ylabel(difftitle)
        axes[i,2].set_xlabel('well_id')
    
     # these are matplotlib.patch.Patch properties
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    axes[0][0].text(-0.20, 1.15, platetype, transform=axes[0][0].transAxes, fontsize=14, verticalalignment='top', bbox=props)

    plt.tight_layout()
    
    #shift down
    st.set_y(0.95)
    fig.subplots_adjust(top=0.85)
    
    plt.show()    
#    return npfitpar         
    return fig
    
def SCRATCH():           
    xlbook = openbook('./MEDMAN_20151109115944.xls')            
    xlsheet = xlbook.sheet_by_name('PlateSignature')
    
    Zoebook = openbook('../ZOE/Zoedb.xlsx')
    Zoesheets = Zoebook.sheet_names()
    ZoeSig = Zoebook.sheet_by_name('PlateSignature')
    zoesig = processSignature(ZoeSig)
    
    zoep1=[row[3] for row in zoesig]
    zoep0=[row[4] for row in zoesig]
    
    diffp1 = zoep1 - p1
    npp1 = np.array(p1)
    
    npzoep1 = np.array(zoep1)
    
    diffp1 = npp1 - npzoep1
    npp0 = np.array(p0)
    
    npzoep0 = np.array(zoep0)
    
    diffp0 = npp0 - npzoep0

def CompareDB(db1='./1552/TX948334_MC1234567/E1552_TX948334_MC1234567_20151104.xls', db2='./1476/TX948334_MC0000001/E1476_TX948334_MC0000001_20151027.xls',transducer='TXNNNNNN'):
    
    BOOKS, BOOKNAMES = OpenBooks(db1,db2)

#    BOOKS, BOOKNAMES = OpenBooks('./1552/TX948334_MC1234567/E1552_TX948334_MC1234567_20151104.xls','./1476/TX948334_MC0000001/E1476_TX948334_MC0000001_20151027.xls')
  #  platetypes = ['384LDV_AQ_B2', '384LDV_DMSO', '384PP_AQ_BP2', '384PP_DMSO2', '384PP_AQ_CP', '1536LDV_DMSO', '384PP_AQ_SP2', '384PP_AQ_GP2','384PP_DMSO2_MIP']    
    platetypes = ['384PPL_DMSO2']
#    platetypes = ['384LDV_DMSO', '384PP_AQ_BP2', '384PP_DMSO2', '384PP_AQ_CP', '1536LDV_DMSO', '384PP_AQ_SP2', '384PP_AQ_GP2']   
#    platetypes = ['384LDV_AQ_B2']
    for plate in platetypes: 
        ComparePlateType(BOOKS,BOOKNAMES,plate,transducer)


def ComparePlateType(books, booknames=['DB1','DB2'], platetype='384PP_DMSO2', transducer='TXXNNNNNN'):
    
    if not os.path.exists(transducer):
        os.makedirs(transducer)

    plottype = ['Signature']    
    lut2dlist=['SolventFluidThickThreshEnergy','EjectionOffset','Thresh2XferdB']
    percentplot=[True, False, False]

    for val in lut2dlist:
        plottype.append(val)
    plottype.append('ToneX')
    
    legend=['Amp (V)','DZ (um)','T2T (dB)']    
       
    #platetype='384PP_DMSO2'

    platefolder = transducer + "/" + platetype

    if not os.path.exists(platefolder):
        os.makedirs(platefolder)
    
    
    fig = [None]*(1+len(lut2dlist)+1)    
    figcnt = 0    
    
    fig[figcnt] = SignatureAnalysis(books, booknames, platetype)
    figcnt += 1    
    
    for i,var in enumerate(lut2dlist):
        fig[figcnt] = plotLUT2D(books, booknames, platetype, lut2dlist[i], percentplot[i] , legend[i])
        figcnt += 1
#   dat = plotLUT2D(BOOKS,BOOKNAMES,platetype,'Thresh2XferdB','T2T (dB)') 
#   dat = plotLUT2D(BOOKS,BOOKNAMES,platetype,'EjectionOffset','DZ (um)')
    fig[figcnt] = plotToneX(books, booknames, platetype)    
    figcnt += 1
    
    for i,var in enumerate(fig):
        filebase = platefolder + "/" + transducer + "_" + platetype + "_"  + plottype[i]
        for k in ['.png','.svg']:
            filename = filebase + k
            var.savefig(filename,bbox_inches='tight')
    return

def processSheet(xlsheet, plateofinterest='384PP_DMSO2', platecol=2, ncols = 5, offset = 6, lut = False):
    nldv = 0
    others =  0
    #ncols = 5
    #offset = 6
#    plateofinterest = '384PP_DMSO2'    
    mtrx = []
    # make 2d list
#    signature.append([])
#    signature.append([])    
    for row_idx in range(0, xlsheet.nrows):
        cell_obj = xlsheet.cell(row_idx,platecol)
        plate = cell_obj.value
        if ( plate == plateofinterest ):
            nldv += 1
            row = []
            if (lut):
                p = xlsheet.cell(row_idx,1).value
                row.append(p)
            for i in range(0,ncols):
                p = xlsheet.cell(row_idx,i+offset).value
                row.append(p)

            mtrx.append(row)   
        else:     
            others += 1
    print('Processed ',xlsheet.nrows, ' rows ', nldv, ' entries of interest ', others, ' others. Plate of interest: ',
     plateofinterest)
    
    return mtrx
    
def processLUT2D(l2m, lut='SolventFluidThickThreshEnergy', xind=None):
    # extract relevant LUT form LUT Sheet
    power = [ row[1:] for row in l2m if row[0] == lut]
    # extract first index
    idx1 = [ row[0] for row in power ]
    # look for unique entries
    
    if xind == None:
        xind =  set(np.sort(idx1))
        
    xxind = np.sort(list(xind))
    # extract all LUT1D
    mtrx = [None]*len(xxind)
    for i,val in enumerate(xxind):
        mtrx[i] = [ row[1:] for row in power if row[0] == val ]
    return mtrx, xxind  
    
    
def plotLUT2D(books, booknames=['DB1','DB2'], plate='384PP_DMSO2', lut='SolventFluidThickThreshEnergy', percentplot=True, ylab='Amp (V)', xlab='Thickness (mm)'):   

    nbooks = len(books)
    LUT2DSheets = [None]*nbooks
    for i,var in enumerate(books): 
        LUT2DSheets[i] = books[i].sheet_by_name('LUT2D')
        
    data = [None]*nbooks
    for k in range(0,nbooks):
        l2 = processSheet(LUT2DSheets[k],plate,4,3,7,True)
        if k == 0 :
            dat, xind = processLUT2D(l2,lut)
            print(' xind: ', xind)
        else:
            dat, xind = processLUT2D(l2,lut)
            print(' xind: ', xind)
        data[k] = dat
                
    colors=['b','r','g']
    markers=['o','o','^']    
    nrows = (len(xind)+1)//2
 
    ncols = 2
    # data conversions
    npdata = np.array(data)

    xxi = list(xind) 
    
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(8,4*nrows))
   
# avoid singularityL
    if (nrows == 1):
        axes = np.atleast_2d(axes)
   
    print(' xind: ', xind, ' nrows: ', nrows, ' shape(axes):', np.shape(axes)   )
   
    # turn off last axis is odd number of entries
    if (len(xind)%2):
      axes[-1, -1].axis('off')
    ax2=axes
    plottitle = booknames[0] + ' vs ' + booknames[1] + ': ' + lut #PA[0] + '\n' + PA[1]
    st = fig.suptitle(plottitle,fontsize='large')
#    bt = fig.suptitle(plate,fontsize='large',fontweight='bold')
    ii = 0
    
    labels = [None]*nbooks
    for i in range(0,nbooks):
        labels[i] = booknames[i].rsplit("_")[0]

     # these are matplotlib.patch.Patch properties
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    alldif = []

    for i in range(0,nrows):
         for j in range(0,ncols):
             if ii >= len(xind):
                break
             for k in range(0,nbooks):
                 axes[i][j].plot(npdata[k][ii,:,0],npdata[k][ii,:,1],color=colors[k],markersize=8,marker=markers[k],label=labels[k])
             xdiff,ydiff = lutdif(npdata[0][ii,:,0],npdata[0][ii,:,1],npdata[1][ii,:,0],npdata[1][ii,:,1],percentplot)
             alldif.append(ydiff)
             axes[i][j].set_title(xxi[ii])
             axes[i][j].set_xlabel(xlab)
             axes[i][j].set_ylabel(ylab)
 
          
            # place a text box in upper left in axes coords
             if (i==0 and j==0):
                 axes[i][j].text(-0.20, 1.15, plate, transform=axes[i][j].transAxes, fontsize=14, verticalalignment='top', bbox=props)
             ii += 1
             if (ii == len(xind) ):
                 axes[i][j].legend(prop={'size': 10})    
                 box = axes[i,j].get_position()
                 axes[i,j].set_position([box.x0, box.y0, box.width * 0.8, box.height])
                 # Put a legend to the right of the current axis
                 axes[i,j].legend(numpoints=1, loc='center left', bbox_to_anchor=(1.2, 0.85))
             ax2[i][j] = axes[i][j].twinx()
             ax2[i][j].plot(xdiff,ydiff,color='silver',marker='^')
             if (percentplot):
                 ax2label = 'Difference (%)'
             else:
                 ax2label = 'Difference'
             ax2[i][j].set_ylabel(ax2label, color='gray')   
   
     
    plt.tight_layout()
    Delta = ' Diff: ' + '{:.1f}'.format(np.mean(np.asarray(alldif).flatten())) + ' +/- ' + '{:.1f}'.format(np.std(np.asarray(alldif).flatten()))
    if (percentplot):
        Delta += ' %'
    axes[0][1].text(-0.20, 1.15, Delta, transform=axes[0][1].transAxes, fontsize=14, verticalalignment='top', bbox=props)
    #shift down
    st.set_y(0.95)
#    bt.set_y(0.925)
    
    fig.subplots_adjust(top=0.9,bottom=0.05)
    
    
    plt.show()           
    return fig
    
def lutdif(x1,y1,x2,y2,reportpercent=True, reverse=False):
#select x value of difference array according to this logic:
#     
    if (x1[0]<x2[0]):
        xval = x2
    else:
        xval = x1
#    print('x1 =' , x1, ' x2 = ', x2, ' xval = ', xval)    
#    print('np.interp(xval,x1,y1) : ' , np.interp(xval,x1[::-1],y1[::-1]) )
#    print('np.interp(xval,x2,y2) : ' , np.interp(xval,x2[::-1],y2[::-1]) )
    if (not reverse):
        yval = np.interp(xval,x1,y1) 
    else:
        yval = np.interp(xval,x1[::-1],y1[::-1])
    if (not reverse):        
        yval -= np.interp(xval,x2,y2)
    else:
        yval -= np.interp(xval,x2[::-1],y2[::-1])
        
#    print('y1 =' , y1, '\ny2 = ', y2, '\nyval = ', yval)    
    if reportpercent:
        yval /= y1
        yval *= 100    
#    print('xval = ', xval, '\nyval = ', yval)     
     
    return  xval,yval
    
# of interest will be : ToneX_CF_MHz, ToneX_RelAmp,  ToneX_Width_us   
def plotToneX(books, booknames=['DB1','DB2'], plate='384PP_DMSO2', luts=['ToneX_CF_MHz','ToneX_Width_us','ToneX_RelAmp']):
            
            #ylab='Freq (MHz)', xlab='Z (MRayl)'):   
    ylabes = ['Freq (MHz)','Length (us)', 'RA']
    nbooks = len(books)
    LUTSheets = [None]*nbooks
    for i,var in enumerate(books): 
        LUTSheets[i] = books[i].sheet_by_name('LUT')
        
    data = [None]*nbooks
    for k in range(0,nbooks):
        lut = processSheet(LUTSheets[k],plate,4,3,6,True)
        dat = [None]*len(luts)
        for i,var in enumerate(luts):          
            dat[i] = [ row[1:4] for row in lut if row[0] == luts[i] ]
        data[k] = dat    
     
    npdata  = np.array(data)
   
    nrows = len(luts)
    ncols = 2

    colors=['b','r','g']
    markers=['o','o','s'] 
    segments=[1.0,3.0]    
    
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(8,4*nrows))
    ax2 = axes
    
    plottitle = booknames[0] + ' vs ' + booknames[1] + ': ' + 'ToneX' #PA[0] + '\n' + PA[1]
    st = fig.suptitle(plottitle,fontsize='large')

    labels = [None]*nbooks
    for i in range(0,nbooks):
        labels[i] = booknames[i].rsplit("_")[0]

 # these are matplotlib.patch.Patch properties
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

    for i in range(0,nrows):
         thisrowdat = npdata[:,i]
         for j in range(0,ncols):
             thiscoldat = [None]*len(books)
             for k in range(0,nbooks):
                 thiscoldat[k] = np.array([ row[1:3] for row in thisrowdat[k] if row[0] == segments[j]])
                 axes[i][j].plot(thiscoldat[k][:,0],thiscoldat[k][:,1],color=colors[k],marker=markers[k],label=labels[k])
             xdiff,ydiff = lutdif(thiscoldat[0][:,0],thiscoldat[0][:,1],thiscoldat[1][:,0],thiscoldat[1][:,1], False, True)
             tit = luts[i] + 'Seg ' + str(segments[j])
             axes[i][j].set_title(tit)
             axes[i][j].set_xlabel('Z (MRayl)')
             axes[i][j].set_ylabel(ylabes[i])
             if (i==0 and j==0):
                 axes[i][j].text(-0.20, 1.16, plate, transform=axes[i][j].transAxes, fontsize=14, verticalalignment='top', bbox=props)

             if (i == nrows-1 and j == ncols-1):
                 axes[i][j].legend(prop={'size': 10})    
                 box = axes[i,j].get_position()
                 axes[i,j].set_position([box.x0, box.y0, box.width * 0.8, box.height])
                 # Put a legend to the right of the current axis
                 axes[i,j].legend(numpoints=1, loc='center left', bbox_to_anchor=(1.2, 0.85))
             ax2[i][j] = axes[i][j].twinx()
             ax2[i][j].plot(xdiff,ydiff,color='silver',marker='^')
             ax2[i][j].set_ylabel('Difference',color='gray')
             
    plt.tight_layout()
    
    #shift down
    st.set_y(0.95)
    fig.subplots_adjust(top=0.88,bottom=0.05)
    
    
    plt.show()           
    return fig
    