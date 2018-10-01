# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 20:30:50 2017

@author: avandenbroucke
"""

import pandas
import time
import os
if __package__ is None or __package__ == '':
    from pyCyte.DropCV import ReaderDat
else:
    from ..DropCV import ReaderDat
import numpy as np

pandas.options.mode.chained_assignment = None

# \\seg\data\Lemonade\Rollout\
def lutdecode(myy='B16'):
    ctomonth = {
      '1' : '01',
      '2' : '02',
      '3' : '03',
      '4' : '04',
      '5' : '05',
      '6' : '06',
      '7' : '07',
      '8' : '08',
      '9' : '09',
      'A' : '10',
      'B' : '11',
      'C' : '12'}
      
    if myy[0] in ctomonth.keys():  
        lutmonth = ctomonth[myy[0]]       
    else:
        lutmonth='03'
    lutyear = str(2000 + int(myy[1:]))
    return lutmonth + lutyear

def plasticdecode(letter):
    plasticdict = {
       'L' : '384PPL',
       'G' : '384PPG' ,
       'D' : '384LDVS',
       'F' : '1536LDVS',
       'P' : '384PPL-Plus'
           }      
    if letter in plasticdict.keys():
        return plasticdict[letter]
    else:
        return 'Misc'

def fluiddecode(fluid):
    fluiddict= {
      'GP2' : 'BP/GP',
      'SP2' : 'SP',
      'DMSO2' : 'DMSO',
      'DMSO' : 'DMSO',
      'B2'   : 'AQ' ,
      'SP'   : 'SP',
      'GP'   : 'BP/GP'         }        
    if  fluid in fluiddict.keys():
        return fluiddict[fluid]
    else:
        return 'Misc'
        
def process525UCP(cal, r):
    allstats = []
    concs = [ 0, 14, 200  ]
    for i,m in enumerate( [0xFF,0x7F00,0x7F8000] ):
        stats = r.getPrintStats(cal, mask = m, rows=24, rowmask=False)
        c = concs[i]
        thisstats = stats._asdict()
        thisstats['Concentration'] = c
        thisstats['Fluid'] = 'SP' 
        allstats.append(thisstats)         
    alldf = pandas.DataFrame(allstats)
    #alldf.columns = r._PrintStats._fields    
    return alldf    
    
def process525PlusUCP(cal, r, fluid):
    allstats = []
    concs = [ 0, 14, 25  ]    
    if (fluid.startswith('00')):
        modfluid = 'GP00'
    elif (fluid.startswith('02')):
        modfluid = 'GP20'
    elif (fluid.startswith('05')):
        modfluid = 'GP50'
    else:
        modfluid = fluid
    for i,m in enumerate( [0xFF,0x7F00,0x7F8000] ):
        stats = r.getPrintStats(cal, mask = m, rows=24, rowmask=False)
        c = concs[i]
        thisstats = stats._asdict()
        thisstats['Concentration'] = c
        thisstats['Fluid'] = modfluid
        allstats.append(thisstats)         
    alldf = pandas.DataFrame(allstats)
    return alldf 
    
def processDMSOUCP(cal, r):
    allstats = [] 
    concs = [ 70, 90, 100, 80]
    for i, m in enumerate( [ 0xf, 0xf0, 0xf00, 0xf000 ] ):
        stats = r.getPrintStats(cal, mask = m)
        c = concs[i]
        # sdf = pandas.DataFrame(stats)
        thisstats = stats._asdict()
        thisstats['Concentration'] = c
        thisstats['Fluid'] = 'DMSO' 
        allstats.append(thisstats)         
    alldf = pandas.DataFrame(allstats)
    #alldf.columns = r._PrintStats._fields    
    return alldf    
    
def processSPUCP(cal, r):
    allstats = [] 
    concs = [ 14, 200 ]
    for i, m in enumerate( [ 0xff, 0xff00 ] ):
        stats = r.getPrintStats(cal, mask = m)
        c = concs[i]
        # sdf = pandas.DataFrame(stats)
        thisstats = stats._asdict()
        thisstats['Concentration'] = c
        thisstats['Fluid'] = 'SP' 
        allstats.append(thisstats)         
    alldf = pandas.DataFrame(allstats)
    #alldf.columns = r._PrintStats._fields    
    return alldf    
    
def processUCP(cal, r, conc=0, fluid='GP'):
    allstats = []
    stats = r.getPrintStats(cal)
    thisstats = stats._asdict()
    thisstats['Fluid']=fluid
    thisstats['Concentration'] = conc
    allstats.append(thisstats)
    return pandas.DataFrame(allstats)
    
def processInstrument(SN='1531', Region='EUR', plot=False):
    filelist = [ f for f in os.listdir() if SN in f and f.endswith('.csv') and 'Summary'  not in f]
    if len(filelist) == 0 :
        print('No valid files found for instrument ',SN, ' ( wdir = ', os.getcwd(), ')')
        return 
    return processFileList(filelist,SN=SN,Region=Region, plot=plot)    
 
def getInstrumentsByDate(path=os.getcwd()):
    return sorted([ f for f in os.listdir() if f.startswith('E5')],key=os.path.getctime,reverse=True)
    
def is525(SN, modellist):
    Model = modellist[modellist['Installed Product ID'].str.contains(SN)]['Product: Product Line'].values
    if len(Model) == 0:
        print('ERROR: SN ', SN,' not found in modellist ' )
        return 
    if len(Model) > 1:
        print('ERROR: duplicate entry for SN ', SN,' nin modellist ' )
        return
    if '525' in Model[0]:
        return True
    else:
        return False
        
   
def processFileList(filelist,SN,Region='EUR', plot=False):
    r = ReaderDat.ReaderDat()
    r.PMTCorrectionTolerance = 0.2
    r.EmptyThresh = 1.5
    nfiles = len(filelist)
    allstats = pandas.DataFrame()
    modellist = pandas.read_csv('//seg/data/Lemonade/Rollout/InstrumentInfo.csv')   
    E525 = is525(SN,modellist)
    printnr = 0
    if E525 == None:
        print('ERROR : Can\'t determine Product Line for Instrument', SN)
        return
    for f in filelist:
        print('Processing file ', f, ' E525: ', E525)
        if Region != 'EUR' : 
            if 'PlateBC_' not in f:
                print('invalid filename ', f)
                continue
            barcode = f.split('PlateBC_')[1].split('_Labcyte')[0]
            barcode = barcode.replace('-','_')
            if len(barcode.split('_')) == 2 :
                bc1 = barcode.split('_')[0]
                bc2 = barcode.split('_')[1]
                plastic = bc1[4]
                lut = bc2[-3:]
                fluidclass = bc2[:-6]
                conc = bc2[-6:-3]
                printnr = bc2[-4:-3]                
            elif len(barcode.split('_')) == 3 :  
                lut = 'B16'
                fluidclass = barcode.split('_')[2][:-2]
                printnr = barcode.split('_')[2][-4:-3]
                if 'DMSO' not in fluidclass:
                    conc = fluidclass[-2:]
                    fluidclass = fluidclass[:-2]
                plastic = 'L'
            else:
                print( ' invalid barcode ', barcode)
                continue 
            print('fluidclass: ' , fluidclass, ' conc: ', conc)
            LUT = lutdecode(lut)
            print(' Using LUT: ', LUT)
            READER = 'BMG-1619'
            if LUT in r.getCalibrations(READER, UseInternalStd = True):
                r.setStdCurve(lutdate=LUT,reader=READER, UseInternalStd = True)   
            else:
                print('Invalid LUT ', LUT, ' for reader ', READER)
                continue
        
            raw = r.processReaderFile(f)
            cal = r.applyCalCurve(raw)
            if (cal == None):
                continue
            if (plot):
                stats = r.getPrintStats(cal)
                r.plotReaderDat(cal,stats,title=f)
            if not E525:    
                if 'DMSO' in fluidclass:
                    stats = processDMSOUCP(cal,r)
                elif 'SP' in fluidclass:
                    stats = processSPUCP(cal,r)
                elif 'GP' in fluidclass:
                    stats = processUCP(cal,r, conc=conc,fluid=fluidclass)
                elif 'BP' in fluidclass:
                    stats = processUCP(cal,r, conc=conc,fluid=fluidclass)
                elif 'CP' in fluidclass:
                    stats = processUCP(cal,r, conc=conc,fluid=fluidclass)
                elif  (1):
                    stats = processUCP(cal,r,conc='CUST',fluid=fluidclass)
                else :
                    print(' unknown fluid class : ', fluidclass ,' -- skipping')
                    continue
            else:
                if plastic == 'L' :
                    if 'SP' in fluidclass:
                        stats = process525UCP(cal,r)
                    elif 'GP' in fluidclass:
                        stats = process525PlusUCP(cal,r,conc)
                    else:    
                        print(' unknown fluid class : ', fluidclass ,' -- skipping')
                        continue 
                elif plastic == 'P' :    
                    if ( 'GP' in fluidclass ) :
                        stats = process525PlusUCP(cal,r,conc)
                    else:
                        stats = process525PlusUCP(cal,r,'UNKNOWN')
                elif plastic == 'G' :
                    stats = process525UCP(cal,r)
                else:
                    print('unsupported plastic: ', plastic, ' -- assuming L' )
                    
            stats['LUT'] = lut
            stats['Plastic'] = plastic      
            stats['PrintNr'] = printnr
            allstats = allstats.append(stats)
            DATE = filelist[0].split('_')[4]
        else:
            READER = 'BMG-1305'
            barcode = f.split('Final Test')[1].split('.csv')[0] 
            B = barcode.replace(' ','_')
            parts = B.split('_')
            conc = '-' 
            #print( ' len(parts) = ' , len(parts))
            if len(parts) == 4 :
                DATE = parts[0]
                plastic = parts[2][4]
                printtype = parts[2][5]
                if ( printtype == 'E' ) :
                    print(' File ', f, ' identified as EjectSweep plate')
                    continue
                lut = parts[3][-3:].upper()
                if lut[0] not in '123456789ABC' :
                    print(' invalid lut ', lut, ' processing file ', f)
                    continue
                fluidclass = parts[3][:-6].upper()
                conc = parts[3][-6:-3]
                LUT = lutdecode(lut)
                printnr = parts[3][-4:-3]
                # JAN method
            elif len(parts) == 6:
                DATE = parts[0]
                LUT = '112016'
                plastic = 'L'
                fluidclass = parts[4].upper()
                conc = parts[5]    
            elif len(parts) > 4  :
                # DEC2016 method
                DATE = parts[0]
                LUT = '112016'
                plastic='L'
                fluidclass = parts[3].upper() 
            elif len(parts)   == 3:
                DATE = parts[0]
                LUT = '112016'
                plastic = 'L'
                fluidclass=parts[2][3:-3].upper()
            else:
                print('Invalid barcode for file ', f)
                continue
            if LUT in r.getCalibrations(READER, UseInternalStd = True):
                r.setStdCurve(lutdate=LUT,reader=READER, UseInternalStd = True)   
            else:
                print('Invalid LUT ', LUT, ' for reader ', READER)
                continue
            raw = r.processReaderFile(f)
            cal = r.applyCalCurve(raw)
            if  (cal == None):
                print(' No valid calibration found for file ', f)
                continue
            if (plot):
                stats = r.getPrintStats(cal)
                r.plotReaderDat(cal,stats,title=f)
            if not E525:     
                if 'GP' in fluidclass :
                   if conc == '-' : 
                       conc = fluidclass.split('GP')[1]
                   stats = processUCP(cal,r, conc=conc,fluid=fluidclass)             
                elif 'SP' in fluidclass:
                   stats = processSPUCP(cal,r)
                elif 'DMSO' in fluidclass:
                    stats = processDMSOUCP(cal,r)
                elif 'BP' in fluidclass:
                     stats = processUCP(cal, r, conc=0, fluid='GP')
                elif 'CP' in fluidclass:
                     stats = processUCP(cal, r, conc=conc, fluid='GP')
                else:
                    print('Error processing fluidclass ', fluidclass)
                    continue
            else:
                if plastic == 'L' :
                    if 'SP' in fluidclass:
                        stats = process525UCP(cal,r)
                    else:
                        print(' unknown fluid class : ', fluidclass ,' -- skipping')
                        continue 
                elif plastic == 'P' :    
                    if ( 'GP' in fluidclass ) :
                        stats = process525PlusUCP(cal,r,conc)
                    else:
                        stats = process525PlusUCP(cal,r,'UNKNOWN')
                else:
                    print('unsupported plastic: ', plastic, ' -- assuming L' )
                    plastic == 'L'
                    stats = process525PlusUCP(cal,r,'UNKNOWN')
            stats['LUT'] = LUT
            stats['Plastic'] = plastic
            stats['PrintNr'] = printnr
            allstats = allstats.append(stats)    
    if (allstats.empty):
        print(' no valid files found for echo ', SN )
        return
    allstats.Reader = READER
    allstats.date = DATE            
    allstats.LUT = LUT    
    allstats.SN = SN
    allstats.applyPMTCorr = r.applyPMTCorr
 #   allstats['Plastic'] = plastic
    if (E525):
        nomvol = 100
    else:
        nomvol = 50
    allstats.nomvol = nomvol    
    allstats['SN'] = SN
    allstats['Status'] = 'PASS'
    allstats['Status'][allstats['RawCV']>8] = 'FAIL'
    allstats['Status'][(abs(allstats['Mean']-nomvol) / nomvol )> 0.1 ] = 'FAIL'   
    allstats['Precision'] = 1
    allstats['Accuracy'] = 1
    allstats['Precision'][allstats['RawCV']>8 ] = 0
    allstats['Accuracy'][(abs(allstats['Mean']-nomvol) / nomvol )> 0.1 ] = 0
    return allstats            
    
def writeReport(allstats, xlfilebase='', maxcv=8, accuracy=0.1, crit=None):
    SN = allstats.SN
    if xlfilebase == '' :
        xlfilebase = SN
    xlfilename = xlfilebase + '.xlsx'
    picklefile = xlfilebase + '.pkl'
    allstats.to_pickle(picklefile)
    R = allstats.set_index(['SN','Fluid','Plastic','Concentration'])    
    if 'File' in R.columns:
        R = R[['N','Mean','CV','RawCV','Empties','Outlier','Reliability','PMTCorr','Status','PrintNr','LUT','File']]
        R.columns=['N','Mean(nL)','CV(%)','RawCV(%)','Empties','Outlier','Reliability','PMTCorr','Status','Print','LUT','FileName']
    else:
        R = R[['N','Mean','CV','RawCV','Empties','Outlier','Reliability','PMTCorr','Status','PrintNr','LUT']]
        R.columns=['N','Mean(nL)','CV(%)','RawCV(%)','Empties','Outlier','Reliability','PMTCorr','Status','Print','LUT']
    R = R.sortlevel(['Fluid','Plastic','Concentration'], sort_remaining=False )               
    R.Reader = allstats.Reader
    R.date = allstats.date
    R.nomvol = allstats.nomvol
    R.applyPMTCorr = allstats.applyPMTCorr
    LUT = allstats.LUT
    writeXLS(dataframe=R,xlfilename=xlfilename,maxcv=maxcv, accuracy=accuracy, crit=crit, LUT= LUT)
    return R

def writeXLS(dataframe, xlfilename='', maxcv=8, accuracy = 0.1, crit=None, includefooter=True, LUT='Undefined'):    
    writer = pandas.ExcelWriter(xlfilename,engine='xlsxwriter')
    dataframe.to_excel(writer, sheet_name='report')
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
    worksheet.set_column('F:H', 9, dec_fmt)
    worksheet.set_column('D:D',15,pass_fmt)
    worksheet.set_column('E:E',5)
    worksheet.set_column('L:L',10,pmt_fmt)
    worksheet.set_column('C:C',9)
    worksheet.set_column('K:K',12)
    worksheet.set_column('M:M',10, pass_fmt)
    worksheet.set_column('O:O',12,pass_fmt)
    worksheet.set_column('P:P',80,pass_fmt)
    worksheet.set_column('N:N',5,pass_fmt)
    
    lines = len(dataframe)+1
    
    if crit != None:
       accuracy =   crit['accuracy'] 
       dmsoaccuracy =  crit['dmsoaccuracy'] 
       cpaccuracy  = crit['cpaccuracy']
       cvpct = crit['cvpct'] 
       dmsocvpct = crit['dmsocvpct'] 
       cpcvpct = crit['cvpct']
       reliabilities =  crit['reliabilities'] 
       empties = crit['empties']
       pmtcorr = crit['pmtcorr']

    else:
       dmsoaccuracy = accuracy
       cpaccuracy = accuracy
       cvpct = maxcv
       dmsocvpct = maxcv
       cpcvpct = maxcv
       reliabiliteis = 1
       empties = 0
       pmtcorr = 0.05
       
    nomvol = dataframe.nomvol
    minvol = (1 - accuracy)*nomvol
    maxvol = (1 + accuracy)*nomvol    
    
    dmsominvol = (1 - dmsoaccuracy)*nomvol
    dmsomaxvol = (1 + dmsoaccuracy)*nomvol 

    fluidorder = dataframe.index.get_level_values(1).values
    predmso = -1
    postdmso = -1
    hasDMSO = False
    if 'DMSO' in fluidorder:
        hasDMSO = True
        # '2' because excel is indexed at 1, and we row 1 is a header, row 2 is the first data row
        firstdmso = np.where(fluidorder=='DMSO')[0][0] + 2
        lastdmso = np.where(fluidorder=='DMSO')[0][-1] + 2
        if firstdmso > 0:
            predmso = firstdmso - 1
        if lastdmso < len(fluidorder)  + 1 :
            postdmso = lastdmso + 1
        
    condrange = 'M2:M' + str(lines)
    worksheet.conditional_format(condrange, {'type': 'cell', 'criteria': '==', 'value': '"FAIL"','format': format1})
    worksheet.conditional_format(condrange, {'type': 'cell', 'criteria': '==', 'value': '"PASS"','format': format2})                                     
    condrange = 'I2:I' + str(lines)
    worksheet.conditional_format(condrange, {'type': 'cell', 'criteria': '>', 'value': empties, 'format' : format1a})
    
    condrange = 'L2:L' + str(lines)
    pmtmin= 1 - pmtcorr
    pmtmax = 1 + pmtcorr
    worksheet.conditional_format(condrange, {'type':'cell', 'criteria': 'not between', 'minimum' : pmtmin, 'maximum': pmtmax,'format':format1a}) 
    
    # CV Spec
    
    if (hasDMSO):    
        if firstdmso > 2:
             # There are some entries before DMSO::
            condrange = 'H2:H' + str(predmso)
            maxcv = cvpct
            print(' condrange: ', condrange, ' cv: ', maxcv)
            worksheet.conditional_format(condrange, {'type': 'cell', 'criteria': '>', 'value': maxcv,'format': format1a})
            condrange = 'F2:F' + str(predmso)
            worksheet.conditional_format(condrange, {'type':'cell', 'criteria': 'not between', 'minimum' : minvol, 'maximum': maxvol,'format':format1a}) 
           
        condrange = 'H' + str(firstdmso) + ':H' + str(lastdmso)
        maxcv = dmsocvpct
        print(' condrange: ', condrange, ' cv: ', maxcv)
        worksheet.conditional_format(condrange, {'type': 'cell', 'criteria': '>', 'value': maxcv,'format': format1a})
        condrange = 'F' + str(firstdmso) + ':F' + str(lastdmso)
        print(' condranga-a: ', condrange, ' min: ', dmsominvol)
        worksheet.conditional_format(condrange, {'type':'cell', 'criteria': 'not between', 'minimum' : dmsominvol, 'maximum': dmsomaxvol,'format':format1a}) 
        
        if postdmso >=0:
            # There are some entries after DMSO::
            condrange = 'H'  + str(postdmso) + ':H' + str(lines)  
            maxcv= cvpct     
            print(' condrange: ', condrange, ' cv: ', maxcv)
            worksheet.conditional_format(condrange, {'type': 'cell', 'criteria': '>', 'value': maxcv,'format': format1a})
            condrange = 'F' + str(postdmso) + ':F' + str(lines)
            worksheet.conditional_format(condrange, {'type':'cell', 'criteria': 'not between', 'minimum' : minvol, 'maximum': maxvol,'format':format1a}) 
    else:
       condrange = 'H2:H' + str(lines)
       maxcv = cvpct
       worksheet.conditional_format(condrange, {'type': 'cell', 'criteria': '>', 'value': maxcv,'format': format1a}) 
       condrange = 'F2:F' + str(lines)
       worksheet.conditional_format(condrange, {'type':'cell', 'criteria': 'not between', 'minimum' : minvol, 'maximum': maxvol,'format':format1a})    
    
    footformat = workbook.add_format({'font_size':10})
    footformat2 = workbook.add_format({'font_size':10, 'italic':True})
    ftst = lines+2
    ftcol = 0       
    if (includefooter):
        worksheet.write(ftst,ftcol, 'Reader', footformat)
        worksheet.write(ftst,ftcol+1, dataframe.Reader, footformat2)
        worksheet.write(ftst+1,ftcol, 'ProcDate',footformat)
        worksheet.write(ftst+1,ftcol+1, dataframe.date,footformat2)
        worksheet.write(ftst+2,ftcol,'Date',footformat)  
        worksheet.write(ftst+2,ftcol+1, time.strftime('%Y%m%d'), footformat2 )   
        worksheet.write(ftst+3,ftcol,'UsePMTCorr', footformat)
        worksheet.write(ftst+3,ftcol+1, dataframe.applyPMTCorr, footformat2)
        if (max(dataframe['N']) == 368) or (max(dataframe['N']) == 184) or (max(dataframe['N']) == 92):
            exclude16 = 'TRUE'
        elif (max(dataframe['N']) == 384) or (max(dataframe['N']) == 192) or (max(dataframe['N']) == 96):
            exclude16 = 'FALSE'
        else:
            exclude16 = 'Undefined'                          
        worksheet.write(ftst+4,ftcol,'ExcludeCol16', footformat)
        worksheet.write(ftst+4,ftcol+1, exclude16, footformat2) 
    writer.save()
    return 

def getwdir(Region='EUR', process = 'Lemonade'):
    if process == 'Lemonade':
        MASTERDIR = '\\\\seg\\data\\Lemonade\\Rollout'
    elif process == 'TSwap':
        MASTERDIR = '\\\\seg\\data\TransducerSwap'
    else:
        print ("Folder is undefined.  Please specify 'Lemonade' or 'TSwap'")
        return
    if Region == 'EUR':
        return MASTERDIR + '\\EUR' 
    elif Region == 'NA-EAST':
        return MASTERDIR + '\\NA-EAST' 
    elif Region == 'NA-WEST':
        return MASTERDIR + '\\NA-WEST' 
    elif Region == 'JAPAN':
        return MASTERDIR + '\\JAPAN' 
    elif Region == 'APAC' :
        return MASTERDIR + '\\APAC'
    else:
        print('Region ', Region, ' not supported yet')
        return    
    
def processInstrList(instrlist, Region='EUR', plot=False, Date=None, process = 'Lemonade'):
    WDIR = getwdir(Region, process)
    if (WDIR):
        os.chdir(WDIR)
    else:
        print('Invalid Region')
        return
    if (Date) :
        os.chdir(os.getcwd() + '\\' + Date)
    alldata = pandas.DataFrame()
    alldata_R = pandas.DataFrame()
    instrlist = [ f.replace('E55X','E5XX') for f in instrlist ]
    for echo in instrlist:   
        print('')
        print(' Processing echo ' ,echo, ', WDIR = ' , os.getcwd())

        if os.path.isdir(echo): 
            os.chdir(echo)
            print(os.listdir())
            if os.path.isdir('./CCT'):
                os.chdir('./CCT')
                if os.path.isdir('./ReaderResults/'):
                    os.chdir('./ReaderResults')
                    SN = echo.split('-')[1]
                    R = processInstrument(SN=SN,Region=Region, plot=plot)
                    if R is not None :
                        RR = writeReport(R)
                        alldata = alldata.append(R)
                        if not RR.empty:
                            alldata_R = alldata_R.append(RR)
                    os.chdir('../')
                os.chdir('../')                   
            else:
                os.mkdir('./CCT')
                os.mkdir('./CCT/ReaderResults')
                os.mkdir('./CCT/TransferFiles')    
              
            if os.path.isdir('./CCT2'):
                os.chdir('./CCT2')
                if os.path.isdir('./ReaderResults/'):
                    os.chdir('./ReaderResults')
                    SN = echo.split('-')[1]
                    R = processInstrument(SN=SN,Region=Region, plot=plot)
                    if R is not None :
                        RR = writeReport(R)
                        alldata = alldata.append(R)
                        if not RR.empty:
                            alldata_R = alldata_R.append(RR)
                    os.chdir('../')
                os.chdir('../') 
               
            
            if os.path.isdir('./CCT3'):
                os.chdir('./CCT3')
                if os.path.isdir('./ReaderResults/'):
                    os.chdir('./ReaderResults')
                    SN = echo.split('-')[1]
                    R = processInstrument(SN=SN,Region=Region, plot=plot)
                    if R is not None :
                        RR = writeReport(R)
                        alldata = alldata.append(R)
                        if not RR.empty:
                            alldata_R = alldata_R.append(RR)
                    os.chdir('../')
                os.chdir('../') 
            if os.path.isdir('./CCT4'):
                os.chdir('./CCT4')
                if os.path.isdir('./ReaderResults/'):
                    os.chdir('./ReaderResults')
                    SN = echo.split('-')[1]
                    R = processInstrument(SN=SN,Region=Region, plot=plot)
                    if R is not None :
                        RR = writeReport(R)
                        alldata = alldata.append(R)
                        if not RR.empty:
                            alldata_R = alldata_R.append(RR)
                    os.chdir('../')
                os.chdir('../')    
            os.chdir('../')    
        else:
            print('No data for Echo ', echo)
            if Region != 'EUR':
                os.mkdir(echo)
                os.mkdir(echo + '/CCT')
                os.mkdir(echo + '/CCT/ReaderResults')
                os.mkdir(echo + '/CCT/TransferFiles')
            continue    
        
    return  alldata, alldata_R  
    
def processRegion(Region='NA-EAST'):
    WDIR = getwdir(Region)
    if (WDIR):
        os.chdir(WDIR)
    else:
        print('Invalid Region')
        return
    files = [ f.replace('E55X','E5XX') for f in os.listdir() if 'X-' in f ]
    A, B = processInstrList(files, Region=Region)
    ofile = Region + '_' +  time.strftime('%Y%m%d') + '.xlsx'
    B.nomvol=50
    C = writeXLS(dataframe=B,xlfilename=ofile,includefooter=False)  
    printstats(A,B, Region=Region)
    return A,B
    
def printstats(A,B, Region='Mars'):    
    nfail = A[['SN','Fluid','Concentration','Mean','RawCV','PMTCorr']][(A['Status'] == 'FAIL') ].shape[0]
    npass = A[['SN','Fluid','Concentration','Mean','RawCV','PMTCorr']][(A['Status'] != 'FAIL') ].shape[0]       
    total = A.shape[0]
    print('')
    print(' Processed ', len(A['SN'].unique()), ' instruments in Region ', Region )
    print(npass,'/',total, ' CCTs pass (=', 100*npass/total,' %) ')
    print(' Here are the ', nfail, ' failure')
    print(B[['Mean(nL)','RawCV(%)','PMTCorr']][(B['Status'] == 'FAIL' )])
    return 