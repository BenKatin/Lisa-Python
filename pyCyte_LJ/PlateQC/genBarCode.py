# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 09:10:07 2016

@author: avandenbroucke


H:\>python.exe \\fserver\people\Arne\PYTHON\pyCyte\PlateQC\genBarCode.py --RunID 14 --PlateType 1536LDV_DMSO --FillStyle FT --NSets 2 --Venue B --PlateLot 0 --C
avity 0
"""

import sys
import getopt
import datetime
import pandas
import os
import csv
if __package__ is None or __package__ == '':
    from pyCyte.PlateQC import barCodes
else:
    from ..PlateQC import barCodes


def main(argv):
   outdir = 'C:\Temp\\'
   SNFile = outdir + 'PlateMaking_SN.csv'
   indexfile = outdir + 'Tempo__barcodes_idx.csv'
   InfoFile = os.path.dirname(sys.argv[0]) + '/SolutionsPlateLotVenue.csv'
   date =  datetime.datetime.now().strftime('%Y%m%d')
   lutdate = ''
   cavity = '0'
   lot = '0'
   loc = 'B' 
   plastic = ''
   desc = False
   dummyRun = False
   nsets = 1
   concentration = '-'
   volume = '-'
   version = 2
   sorting = True
   reducedSet = False
   cavityDefined = False
   lotDefined = False
#prepopulate venue, platelot and lutdate 
   print(' Looking for file: ',  InfoFile)
   
   if ( os.path.isfile(InfoFile) ):
       Meta = {}
       for index, row in enumerate(csv.reader(open(InfoFile))):
        #print(row[0], row[1])
           Meta[row[0]] = row[1]
#skip first 10 rows 
           if (index > 9):
               break
       for field in Meta.keys():
           print(' field: ', field, ', val: ', Meta[field])
           if field.lower() == 'venue' :
               loc = Meta[field][0].upper()           
           if field.lower() == 'lutdate' :
               lutdate = Meta[field]
       PlateLotDF =  pandas.read_csv(InfoFile,skiprows=9)     



   else:
      print(' Unable to find file ', InfoFile)
      print(' Exiting')
      sys.exit(2)            
   try:
      opts, args = getopt.getopt(argv,"DhRr:p:f:n:v:c:l:L:P:d:C:V:U:",["RunID=","PlateType=","FillStyle=","NSets=","Venue=","Cavity=","PlateLot=","LUTDate=","Plastic=","Descending","Conc=","Version=","Vol="])
   except getopt.GetoptError:
      print( 'Unknown argument .. please specify: ') 
      print( 'genBarCode.py -r <RunID> -p <PlateType> -f <FillStyle> -n <NSets> -v <Venue> -c <Cavity> -l <PlateLot> -L <LUTDate> -P <Plastic> -C <Conc> -V <Version> -d -U <Vol>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print(' Help function .. ')
         print( 'genBarCode.py -r <RunID> -p <PlateType> -f <FillStyle> -n <NSets> -v <Venue> -c <Cavity> -l <PlateLot> -L <LUTDate> -P <Plastic> -C <Conc> -V <Version> -d -U <Vol>')
         print( ' -D : Dummy Run')
         print( ' -R : Reduced Set ')
         sys.exit()
      elif opt in ("-r", "--RunID"):
         runID = arg
      elif opt in ("-p", "--PlateType"):
         platetype = arg
      elif opt in ("-f", "--FillStyle"):
         fillstyle = arg
      elif opt in ("-n", "--NSets"):
         nsets = int(arg)
      elif opt in ("-v", "--Venue"):
         loc = arg   
      elif opt in ("-c", "--Cavity"):
         cavity = arg      
         cavityDefined = True
      elif opt in ("-L", "--LUTDate"):
         lutdate = arg   
      elif opt in ("-P", "--Plastic"):
         plastic = arg
      elif opt in ("-l", "--PlateLOT"):
         lot = arg    
         lotDefined = True
      elif opt in ("-d", "--Descending"):
          desc = True
      elif opt in ("-V", "--Version"):
          version = int(arg)
          print(' Using fill version ', version)
      elif opt == '-D':
          dummyRun = True
          print('Dummy Run -- Serial numbers not being updated')
      elif opt in ("-C","--Conc"):
          concentration = arg
          print(' concentration = ', concentration)
      elif opt in ("-U","--Vol"):
          volume = arg
          print(' volume = ' ,volume)
      elif opt in ("-R"):
          reducedSet = True
   print(' Looking for file: ',  InfoFile)      
   bc = barCodes.BarCodes()
     
   # need to do argument checking here
   try:  
       nextRunID = int(runID) # + 1
   except:
       print(' Please specify RunID ! ')
       sys.exit(2)
       
   outputfileBC = str(nextRunID) + '__barcodes.csv'
   outputfileHR = str(nextRunID) + '__barcodes_HR.csv'   
   ToutputfileBC = 'Tempo__barcodes.csv'
   ToutputfileHR = 'Tempo__barcodes_HR.csv'   
   print(' Plastic : ' , plastic)

   try:
       platetype
   except:
       print(' Please specify platetype  ( -- PlateType ) !')
       sys.exit(2)
       
   try:
       fillstyle
   except:
       print(' Please specify fillstyle ( -- FillStyle )  !')
       sys.exit(2)  
       
   if (plastic == 'PPG' ) or (plastic == 'PPL'):
       if ( 'PP_' in platetype):
           platetype = platetype.replace('PP_',plastic+'_')
           print(' working with platetype : ', platetype)
   
   
   platestyle = platetype.split('_')[0]
   print('platestyle: ', platestyle)
   print('PlateLotDF: ' , PlateLotDF)
   if not lotDefined:
       lots = PlateLotDF['PlateLot'][PlateLotDF['Plate'] == platestyle].values
       if len(lots) > 0:
           lot = lots[0]
   if not cavityDefined:
      cavities =  PlateLotDF['Cavity'][PlateLotDF['Plate'] == platestyle].values      
      if len(cavities) > 0:
          cavity = str(cavities[0])
   
   if  not bc.validate(lot,bc.plateLot['Codes']) :
       print(' Invalid platelot ', lot, ' please update definitions in barCodes.py ' )
       sys.exit(2)
   if not bc.validate(loc,bc.Loc['Codes'])  :
       print(' Invalid location ', loc, ' please update definitions in barCodes.py ' )
       sys.exit(2)
   if not bc.validate(cavity,bc.cavity['Codes'])  :
       print(' Invalid cavity ', cavity, ' please update definitions in barCodes.py ' )
       sys.exit(2)             
   print( 'Generating barcodes for plate type ', platetype) 
   print( 'Output files are ', outputfileBC, ' and ' , outputfileHR)
    # reset Hamilton index file 
   idxdict ={}
   idxdict['currindex'] = 0
   idxdf = pandas.DataFrame(idxdict, index=[0])
   idxdf.T.to_csv(indexfile, index=True, header=False)
   
   if  ( os.path.isfile(SNFile)) and  ( not dummyRun ):
      allSN  = pandas.read_csv(SNFile)   
      prevsn = allSN[ (allSN['FillStyle'] == fillstyle ) & (allSN['PlateType'] == platetype) & (allSN['Date'] == int(date))]
      if prevsn.empty:
          lastSN = 0
      else :
          lastSN = prevsn['LastSN'].iloc[-1]
   else:
       lastSN = 0    
 #  lastSN = getLastSN

 #  bc = barCodes.BarCodes()
 #  allmaps = '\\\\seg\\data\\PlateMaps\AllMaps.csv'
   allmaps = os.path.dirname(sys.argv[0]) + '\\PlateMaps\\AllMaps.csv'
   
   allM = pandas.read_csv(allmaps)
   if concentration == '-' :
       platestmp = allM[(allM['Style']==fillstyle) & ( allM['PlateType'] == platetype) & ( allM['Version'] == version)].apply(lambda x: pandas.to_numeric(x, errors='ignore'))
       if (reducedSet):
           if 'DMSO' in platetype:
               sel = ( platestmp['Conc'] == 70 ) | ( platestmp['Conc'] == 80 ) | ( platestmp['Conc'] == 90 ) | ( platestmp['Conc'] == 100 )       
           else:
               sel = ( platestmp['Conc'] == 0 ) | ( platestmp['Conc'] == 10 ) | ( platestmp['Conc'] == 20 ) | ( platestmp['Conc'] == 30 ) | ( platestmp['Conc'] == 40 ) | ( platestmp['Conc'] == 50 )
           platestmp = platestmp[ sel ]    
           #else:    
   else:
       platestmp = allM[(allM['Style']==fillstyle) & ( allM['PlateType'] == platetype) & (allM['Conc'] == concentration )  & ( allM['Version'] == version)].apply(lambda x: pandas.to_numeric(x, errors='ignore'))

#   print(' sytle:: ', fillstyle, 'PLATES:: ', platestmp)    
       
   if volume != '-' :
       platestmp = platestmp[(platestmp['Vol']==int(volume))]
    
   if (platetype.endswith('BP2GP2')):
       plate1 = platetype.replace('BP2GP2','BP2')
       platestmp = allM[(allM['Style']==fillstyle) & ( allM['PlateType'] == plate1)  & ( allM['Version'] == version) ].apply(lambda x: pandas.to_numeric(x, errors='ignore'))
       plate1 = platetype.replace('BP2GP2','GP2')
       platestmp = platestmp.append(allM[(allM['Style']==fillstyle) & ( allM['PlateType'] == plate1)  & ( allM['Version'] == version)].apply(lambda x: pandas.to_numeric(x, errors='ignore')))
   
   if (platetype.endswith('SP2CP')):
       plate1 = platetype.replace('SP2CP','SP2')
       platestmp = allM[(allM['Style']==fillstyle) & ( allM['PlateType'] == plate1)  & ( allM['Version'] == version) ].apply(lambda x: pandas.to_numeric(x, errors='ignore'))
       plate1 = platetype.replace('SP2CP','CP')
       platestmp = platestmp.append(allM[(allM['Style']==fillstyle) & ( allM['PlateType'] == plate1)  & ( allM['Version'] == version)].apply(lambda x: pandas.to_numeric(x, errors='ignore')))
       sorting = False
   
   if ('CP' in platetype):
       platestmp = platestmp[platestmp.Fluid != 'MPD']
   
   if (sorting):
       if (desc):
           plates = platestmp.sort_values(by=['Conc'],ascending=False)
       else:    
           plates = platestmp.sort_values(by=['Conc'],ascending=True)
   else:
      plates = platestmp
   
#   print(' PLATES::', platestmp)    
        
   it=0
   allbarcodes = []
   allhrlabels = []
   for n in range(0,nsets):
       it = lastSN + n
       for i,r in plates.iterrows():
           barcode = r['BarCode']
           fluid = r['Fluid']
           specificbc = bc.genRunSpecificBarCode( c=cavity, lot=lot, LUTDATE=lutdate, MFGDATE=date[2:], SN=it, LOC=loc)
           labeledbarcode = barcode[:7] + specificbc
           
           hrfield0 = platetype.upper() + ' ' + fillstyle + ' '
           if not ((fillstyle == 'UCP') or ( fillstyle == 'ICP') ):
               hrfield0 += (str(r['Conc']) + '% ')
               hrfield0 +=  fluid + ' '
               if ( fillstyle == 'FF') or (fillstyle == 'DD'):
                   hrfield0 += str(r['Vol']) + 'uL'
           if (fillstyle == 'UCP')   and ( fluid != 'DMSO'):
               hrfield0 += (str(r['Conc']) + '% ')
               hrfield0 +=  fluid      
           if (fillstyle == 'UCP') and (fluid == 'DMSO' ) and ( platetype.startswith('96TR')):
               hrfield0 += (str(r['Conc']) + '% ')
               hrfield0 +=  fluid
           hrfield1 = lutdate + 'LUT'
           hrfield1 += ' LOT: ' + lot
           hrfield1 += ' C: ' + cavity          
           hrfield2 =  date
           hrfield2 += ' #' + str(it)
           hrfield2 += ' ' + loc 
           hrfield3 = 'Run: '
           hrfield3 += str(runID)
           barc = {}
           label = {}
           barc['Field0'] = labeledbarcode
           label['Field1'] = hrfield0
           label['Field0'] = hrfield1
           label['Field2'] = hrfield2
           label['Field3'] = hrfield3
           print(labeledbarcode, ' ', hrfield0, '\t\t', hrfield1, '\t', hrfield2)
           allbarcodes.append(barc)
           allhrlabels.append(label)
   if not dummyRun:        
       if not ( os.path.isfile(SNFile)):
           with open(SNFile, "w+") as myfile:
               myfile.write('PlateType,FillStyle,Date,LastSN\n')
       with open(SNFile, "a") as myfile:        
               myfile.write(platetype+ "," + fillstyle + "," + date + "," +str(it+1) + "\n")       
      
   allbarcodesdf = pandas.DataFrame(allbarcodes)
   allhrlabelsdf = pandas.DataFrame(allhrlabels)
   allbarcodesdf.to_csv(outdir + outputfileBC, index=False)  
   allhrlabelsdf.to_csv(outdir + outputfileHR, index=False) 
   allbarcodesdf.to_csv(outdir + ToutputfileBC, index=False)  
   allhrlabelsdf.to_csv(outdir + ToutputfileHR, index=False)
   return
 #  genBarCode(platetype=platetype, style=style, ftype='DMSO', conc='-', vol= '-', v='0', c=cavity, lot=lot, LUTDATE=lutdate ,MFGDATE=date[2:], SN='1')

if __name__ == "__main__":
   main(sys.argv[1:])