# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 21:26:58 2016

@author: avandenbroucke
"""


import pandas
import csv 
import numpy as np
from ..ToolBox import SimpleTools
from ..PlateQC import barCodes
from ..PlateQC import genMaps
import os
import matplotlib.pyplot as plt
import time
  
def readEPAFile(filename, header=14):
  #  for index, row in enumerate(csv.reader(open(filename))):
  #      if ( len(row) > 0 ) and ( row[0] =='[DETAILS]'):
  ##        break;
    epaDF = pandas.read_csv(filename, header=header)
    epaMeta = {}
    for index, row in enumerate(csv.reader(open(filename))):
        if index >= (header-1):
            break
        #print(row[0], row[1])
        epaMeta[row[0]] = row[1]   
    return epaDF, epaMeta    

def loadMap():
    basedir = os.path.join(os.path.dirname(__file__), 'PlateMaps')
    allmaps = basedir + '\\AllMaps.csv'
    return pandas.read_csv(allmaps) 
    
def loadPlateMapHR(platetype='384PP_DMSO2',style='SIG',conc='100'):
 #   allmaps = '\\\\seg\\data\\PlateMaps\AllMaps.csv'
    allM = loadMap()
 #   allM = pandas.read_csv(allmaps)
    filenames = allM['Filename'][ (allM['Style']==style ) & (allM['PlateType']==platetype ) & (allM['Conc']==conc)]    
    ff = pandas.read_csv(filenames.values[0])
    return ff

def loadPlateMap(barcode):
#    allmaps = '\\\\seg\\data\\PlateMaps\AllMaps.csv'
#    allM = pandas.read_csv(allmaps)
    allM = loadMap()
    generic_bc = barcode[0:7]
    validbarcodes = [ v[0:7] for v in list(set(allM['BarCode'])) ]
    if generic_bc not in validbarcodes:
        print(' ** WARNING **  Unknown barcode ', generic_bc, ' -- ')
        return pandas.DataFrame()
    print(' Looking for barcode: ', generic_bc)
    filenames =  allM['Filename'][allM['BarCode'].str.startswith(generic_bc)]
    if len(filenames) > 1 :
        print("*** WARNING *** more than one match found for barcode ", generic_bc, " : ", filenames )
    ff = pandas.read_csv(filenames.values[0])
    return ff
    
def compareAuditToMap(auditDF,mapDF,impedancebased=True):
    mapDF['Source Well'] = mapDF['Well']
    r = pandas.merge(auditDF,mapDF,how='outer',on='Source Well') 
    r['VolDelta'] = r['Survey Fluid Volume']-r['mVolume']
    if (impedancebased):
         r['ImpDelta'] = r['Fluid Composition'] - r['mImpedance']
    else:     
        r['ImpDelta'] = r['Fluid Composition'] - r['mConc']
    return r
    
def plotDiff(auditMapDF, title='YADIEYADIE', impbased=True, volrange=[-5,5]):
    #platetype='384PP_DMSO2_FT_YADIEYADIE'
    nrows = auditMapDF['Source Row'].max()
    ncols = auditMapDF['Source Column'].max()
    voldelta = np.zeros([nrows,ncols])
    impdelta = np.zeros([nrows,ncols]) 
    for i,r in auditMapDF.iterrows():
        row = int(r['Source Row']) -1
        col = int(r['Source Column']) -1
        voldelta[row,col] = float(r['VolDelta'])
        impdelta[row,col] = float(r['ImpDelta'])
 #   fig,ax = plt.subplots(nrows=3,ncols=2,figsize=(10,16)); 
    fig = plt.figure(figsize=(32,15))
    ax01 = plt.subplot2grid((3, 12), (0, 0), colspan=6, rowspan=2)
    ax02 = plt.subplot2grid((3, 12), (0, 6), colspan=6, rowspan=2)
    ax03 = plt.subplot2grid((3, 12), (2, 0), colspan=3)
    ax04 = plt.subplot2grid((3, 12), (2, 3), colspan=3)
    ax05 = plt.subplot2grid((3, 12), (2, 6), colspan=3)
    ax06 = plt.subplot2grid((3, 12), (2, 9), colspan=3)
#    
    fig.suptitle(title, fontsize=18)
    fig.subplots_adjust(hspace=0.55, wspace=0.4)
    plotSurveyDat(auditMapDF, ax=ax01, title='Volume')
    plotSurveyDat(auditMapDF, ax=ax02, field='Fluid Composition', title='Concentration', volplot=False, impbased=impbased)
    SimpleTools.plotMatrix(voldelta,ax=ax03,title='Volume Delta',range=volrange);
    if (impbased):
        SimpleTools.plotMatrix(impdelta,ax=ax05,title='Impedance Delta', range=[-0.2,0.2]);
    else:
        SimpleTools.plotMatrix(impdelta,ax=ax05,title='Impedance Delta', range=[-7.5,7.5]);                          
    voldiff=SimpleTools.fitSimpleHist(voldelta,ax=ax04,xlabel='Volume Delta', title='Volume Delta');
    concdiff=SimpleTools.fitSimpleHist(impdelta,ax=ax06,xlabel='Concentration Delta',title='Concentration Delta');  
   
    return fig, voldiff, concdiff    

def plotSurveyDat(dataframe,field='Survey Fluid Volume',nwells=384,ax=None,title='XXp',volplot=True,impbased=True):
           
        data = genMaps.mapframeAsMatrix(dataframe, field=field)
        nrows, ncols, row_labels = genMaps.wellsToRowCols(nwells)
            
     #   row_labels = list('ABCDEFGHIJKLMNOP')
        column_labels = [ i for i in range(1,ncols+1)]
        #fig, ax = plt.subplots(nrows=1,ncols=1,figsize=(12,18))
        if ax == None:
            fig = plt.figure(figsize=(12, 18))
            ax = fig.add_axes([0.1, 0.1, 0.9, 0.9])
#        axt = fig.add_axes([0.1, 0.8, 0.8, 0.1 ])
        mean = data.mean()
        heatmap = ax.imshow(data,cmap='hsv',interpolation='None',vmin=data.min(),vmax=data.max())
        for y in range(data.shape[0]):
            for x in range(data.shape[1]):
                if (volplot):
                    ax.text(x , y , '%.1f' % data[y, x], horizontalalignment='center', verticalalignment='center',  )
                else:
                    if (impbased):
                        ax.text(x , y , '%.2f' % data[y, x], horizontalalignment='center', verticalalignment='center',  )
                    else:
                        ax.text(x , y , '%.0f' % data[y, x], horizontalalignment='center', verticalalignment='center',  )
    
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
        #ax.xaxis.tick_top()
        #ax.set_xticklabels(column_labels)
        #ax.set_yticklabels(row_labels) 

   #     plt.colorbar(heatmap, ax=ax, cmap=cmap, norm=norm, boundaries=bounds, ticks=concentrations, fraction=0.025, pad=0.04)
        # put the major ticks at the middle of each cell
   #     ax.set_xticks(np.arange(data.shape[1]) , minor=False)
   #     ax.set_yticks(np.arange(data.shape[0]) , minor=False)
        
        ax.set_xticks(np.arange(data.shape[1]) + 0.5 , minor=True)
        ax.set_yticks(np.arange(data.shape[0]) + 0.5 , minor=True)
        # want a more natural, table-like display
    #    ax.invert_yaxis()
        ax.xaxis.tick_top()
        ax.set_xticklabels(column_labels)
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
        
        return 

def extractBarCode(filename, field=2):
    fields=filename.split('__')
    if len(fields) < field:
        print(' ERROR , unable to extract field ', field, ' from filename ', filename)
        return '0'
    return fields[field]    
    

def processEPAFolder(runid=None, EPAFiles=[]):        
 #   os.chdir('//seg/data/Automation/Access1619/EchoPlateAudit/2016-10-04')
    if len(EPAFiles) == 0 :
        EPAFiles = [ f for f in os.listdir() if '_Survey__' in f and not f.startswith('Processed') and 'Interim' not in f and f.endswith('.csv')]      
    allentries = []
    bc = barCodes.BarCodes()
    maxbadwells = 0
    pp_volcriteria = {   'fwhmlim' : 4 ,
                      'minvoldelta' : -7.5 ,
                      'maxvoldelta' : 7.5,
                      'meanvoldelta' : 5 }
    ldv_volcriteria =  {
                      'fwhmlim' : 1.5 ,
                      'minvoldelta' : -2.5 ,
                      'maxvoldelta' : 2.5,
                      'meanvoldelta' : 1 }                                  
    for file in EPAFiles:  
        print(' Processing file ', file)
        ep, epm = readEPAFile(file)
        #barcode = extractBarCode(file)
        barcode = epm['Source Plate Barcode']
        pm = loadPlateMap(barcode)
        if len(pm) == 0:
            print(' *** WARNING, skipping file : ', file)
            thisentry = {}
            thisentry['filename'] = file
            thisentry['Pass'] = 'ERROR'
            allentries.append(thisentry)
            continue
        impbased = True
        if 'DMSO' in file:
            impbased = False
        r = compareAuditToMap(ep,pm,impbased)
        ofile = 'Processed_' + file
        r.to_csv(ofile,index=False)
        tit = getTitle(barcode, runid)
        if 'LDV' in file:
            volcriteria = ldv_volcriteria
            volrange = [-2,2]
        else:
            volcriteria = pp_volcriteria
            volrange = [-5,5]
        fig, vdiff, concdiff = plotDiff(r, title=tit, impbased=impbased,volrange=volrange)
        passedVolSpec, volmean, volfwhm, passvoldict = volume_ana(r['VolDelta'], vdiff,volcriteria)
        passedConcSpec, cmean, cfwhm, passconcdict  = conc_ana(r['ImpDelta'], concdiff, impbased)
        nbadwells =  len(ep.dropna(subset=['Survey Status']))
        if ( nbadwells > maxbadwells):
            passedVolSpec = False
        passfailstring = 'Pass'
        passed = passedVolSpec and passedConcSpec
        thisentry = {}
        thisentry['filename'] = file
        thisentry['barcode'] = barcode
        if (passed):
            thisentry['Pass'] = 'PASS'
        else:
            thisentry['Pass'] = 'FAIL'
        if (passedVolSpec):
            thisentry['VolQC'] = 'PASS'
        else:
            thisentry['VolQC'] = 'FAIL'
        if (passedConcSpec):
            thisentry['ConcQC'] = 'PASS'
        else:
            thisentry['ConcQC'] = 'FAIL'    
        thisentry['VolMeanDiff'] = volmean
        thisentry['VolFWHMDiff'] = volfwhm
        thisentry['ConcMeanDiff'] = cmean
        thisentry['ConcFWHMDiff'] = cfwhm
        decodedbarcode = bc.decodeBarCode(barcode)
        allfields = dict(list(decodedbarcode.items()) + list(thisentry.items()))
        allentries.append(allfields)
        voltit = 'Vol QC: '
        for key, value in passvoldict.items():
            voltit += ' ' + str(key) + ': ' + str(value)
        fig.axes[3].set_title(voltit)
        imptit = 'Imp QC: '
        for key, value in passconcdict.items():
            imptit += ' ' + str(key) + ': ' + str(value)
        fig.axes[5].set_title(imptit)
        if not passedVolSpec:
            fig.axes[3].set_axis_bgcolor('lightcoral')
            passfailstring = 'FailVol'
        if not passedConcSpec:
            fig.axes[5].set_axis_bgcolor('lightcoral')
            if passfailstring == 'Pass' :
                passfailstring = 'FailConc'
            else:
                passfailstring += 'Conc'
#        print(' vdiff : ' , vdiff)
        fstring = getTitle(barcode,runid)        
        b = fstring.replace(' ','__')
        b = b.replace(':','')
        print(' filename :: ' ,b)
        fig.savefig( b + '__' + passfailstring + '.png' )
    allentriesdf = pandas.DataFrame(allentries)
    if runid :
        outfile = str(runid) 
    else :
        outfile = ''
    outfile += '__EPAanalysis.csv'   
    csvsummary = ''
    if (runid):
        csvsummary = str(runid)    
        
    csvsummary += '_EPAanalysis.csv'    
    allentriesdf.to_csv(csvsummary, index=False)
    writeXLS(allentriesdf, xlfilename=csvsummary.replace('.csv','.xlsx'))
    return allentries

   
def writeXLS(dataframe, xlfilename='',  includefooter=True):
    writer = pandas.ExcelWriter(xlfilename,engine='xlsxwriter')
    df = dataframe[['PlateType','FillStyle','FluidType','Concentration','Volume','Version','LOC','Cavity','SN','PlateLot','Pass','VolQC','ConcQC','MFGDate','LUTDate','filename']]
    df.to_excel(writer, sheet_name='report')
    workbook = writer.book
    worksheet = writer.sheets['report']
    dec_fmt = workbook.add_format({'num_format': '0.0'})
    pmt_fmt = workbook.add_format({'num_format': '0.00'})
    pass_fmt = workbook.add_format({'align': 'center'})
    
    # Add a format. Light red fill with dark red text.
    format1 = workbook.add_format({'bg_color': '#FFC7CE',
                               'font_color': '#9C0006'})
     # Add a format.  crimson text.
    format1a = workbook.add_format({'font_color': '#DC143C'})                           
    # Add a format. Green fill with dark green text.
    format2 = workbook.add_format({'bg_color': '#C6EFCE',
                               'font_color': '#006100'})
     # Add a format.  green text.
    format2a = workbook.add_format({'font_color': '#006100'}) 
    
    worksheet.set_column('B:B',20, pass_fmt)
    worksheet.set_column('C:C',9, pass_fmt)
    worksheet.set_column('D:D',9, pass_fmt)
    worksheet.set_column('E:E',12, pass_fmt)
    worksheet.set_column('F:J',9, pass_fmt)
    worksheet.set_column('K:K',15,pass_fmt)
    worksheet.set_column('O:P',10, pass_fmt)
    worksheet.set_column('Q:Q',80,pass_fmt)
    
    
    lines = len(dataframe)+1
    condrange = 'L2:L' + str(lines)
    worksheet.conditional_format(condrange, {'type': 'cell', 'criteria': '==', 'value': '"FAIL"','format': format1})
    worksheet.conditional_format(condrange, {'type': 'cell', 'criteria': '==', 'value': '"PASS"','format': format2})   
    
    condrange = 'M2:M' + str(lines)
    worksheet.conditional_format(condrange, {'type': 'cell', 'criteria': '==', 'value': '"FAIL"','format': format1a})
    worksheet.conditional_format(condrange, {'type': 'cell', 'criteria': '==', 'value': '"PASS"','format': format2a})   
    
    condrange = 'N2:N' + str(lines)
    worksheet.conditional_format(condrange, {'type': 'cell', 'criteria': '==', 'value': '"FAIL"','format': format1a})
    worksheet.conditional_format(condrange, {'type': 'cell', 'criteria': '==', 'value': '"PASS"','format': format2a})   
    
    footformat = workbook.add_format({'font_size':10})
    footformat2 = workbook.add_format({'font_size':10, 'italic':True})
    ftst = lines+2
    ftcol = 0       
    if (includefooter):
   #     worksheet.write(ftst,ftcol, 'Reader', footformat)
    #    worksheet.write(ftst,ftcol+1, dataframe.Reader, footformat2)
    #    worksheet.write(ftst+1,ftcol, 'LUT',footformat)
    #    worksheet.write(ftst+1,ftcol+1, allstats.LUT,footformat2)
       # worksheet.write(ftst+1,ftcol, 'ProcDate',footformat)
       # worksheet.write(ftst+1,ftcol+1, dataframe.date,footformat2)
        worksheet.write(ftst+2,ftcol,'ProcDate',footformat)  
        worksheet.write(ftst+2,ftcol+1, time.strftime('%Y%m%d'), footformat2 )                            
    writer.save()
    return 
    
    
def volume_ana(voldelta,vdiff,criteria):
    fitmean = vdiff.params['center'].value
    fitfwhm = vdiff.params['fwhm'].value
    fwhmlim = criteria['fwhmlim']
    std = voldelta.std()
    passedQC = True
    passdict = {}
    for k in ['FWHM','RANGE','MEAN']:
        passdict[k] = 'Pass'
    if (fitfwhm > fwhmlim):
        passdict['FWHM'] = 'Fail' 
        passedQC = False
    if (fitfwhm < std ):
        passdict['FWHM'] = 'Fail'
        passedQC = False
    if ( voldelta.min() < criteria['minvoldelta'] ) :
        passedQC = False
        passdict['RANGE'] = 'Fail'
    if ( voldelta.max() > criteria['maxvoldelta'] ) :    
        passedQC = False
        passdict['RANGE'] = 'Fail'
    if ( abs(voldelta.mean()) > criteria['meanvoldelta'] )  :        
        passedQC = False
        passdict['MEAN'] = 'Fail'
    return passedQC, fitmean, fitfwhm, passdict        

def conc_ana(concdelta,cdiff, impbased=False):
    if (impbased) :
        fwhm = 0.125
        mean = 0.1
        minmax = 0.15
    else:
        fwhm = 4.1
        minmax = 5.5
        mean = 4.0    
    fitmean = cdiff.params['center'].value
    fitfwhm = cdiff.params['fwhm'].value
    std = concdelta.std()
    passedQC = True
    passdict = {}
    for k in ['FWHM','MEAN']:
        passdict[k] = 'Pass'
    if (fitfwhm < std ):
        passedQC = False
  #  if ( concdelta.min() < fitmean-minmax ) :
  #      passedQC =  False
  #  if ( concdelta.max() > fitmean+minmax ) :    
  #      passedQC = False
    if ( fitfwhm > fwhm):
        passdict['FWHM'] = 'Fail'
        passedQC = False
    if ( abs(concdelta.mean()) > mean )  :        
        passdict['MEAN'] = 'Fail'
        passedQC = False
    return passedQC, fitmean, fitfwhm, passdict
        
def getTitle(barcode, runid):
    bc = barCodes.BarCodes()        
    gentype = bc.decodeBarCode(barcode)
    titl = gentype['PlateType'] + '_'
    style = gentype['FillStyle']
    titl += gentype['FillStyle'] 
    ftype = gentype['FluidType'] 
    fconc = gentype['Concentration'] 
    fvol = gentype['Volume'] 
    version = gentype['Version'] 
    mfgdate = gentype['MFGDate']
    sn = gentype['SN']
    LOC = gentype['LOC'] 
    if ( (style != 'UCP') or (style=='ICP') ):
       titl += ' '
       titl += ftype
       titl += ' '
       titl += fconc
       if ( style == 'FF' ):
          titl += ' '
          titl += fvol
    titl += ' v'
    titl += version
    titl += ' ' 
    titl += mfgdate
    titl += ' #'
    titl += str(sn)
    titl += ' '
    titl += LOC
    titl += ' RunID: '
    titl += str(runid)
    return titl   
      
    