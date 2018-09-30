# -*- coding: utf-8 -*-
"""
Created on Tue Nov  8 21:38:49 2016

@author: Avandenbrourcke
"""

import sys
import getopt
import pandas
import os
import csv
if __package__ is None or __package__ == '':
    from pyCyte.PlateQC import barCodes
else:
    from ..PlateQC import barCodes


def main(argv):
   thisbarcode = ""
   try:
      opts, args = getopt.getopt(argv,"hb:",["BarCode="])
   except getopt.GetoptError:
      print( 'Unknown argument .. please specify: ') 
      print( 'genHamilton.py -b <BarCode> ')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print(' Help function .. ')
         print( 'genHamilton.py  -b <BarCode>')
         sys.exit()
      elif opt in ("-b","--BarCode"):
         print(' User defined barcode: ', arg)
         thisbarcode = arg
   throughdict = {
                   '70': 1,
                   '75': 2,
                   '80': 3,
                   '85': 4,
                   '90': 5,
                   '95': 6,
                   '100': 7,
                   '00' : 1,
                   '10' : 2,
                   '20' : 3,
                   '30' : 4,
                   '40' : 5,

                   '50' : 6,
				   '45' : 7,
				   '55' : 8,
                   } 
   fluidthroughdict = {
      'PBS5' : 1,
      'PBS14' : 2,
      'PBS200' : 3,
      'AQ' : 4,
      '2.4M-HEPES' :5,
      'PEG-3350' :6
   }                
   outdir = 'C:\Temp\\'
   barcodefile = outdir + 'Tempo__barcodes.csv'
   startidx = 0
   indexfile = outdir + 'Tempo__barcodes_idx.csv'
   hamiltonfile = outdir + 'Tempo__Hamilton.csv'
   
   if thisbarcode == "" :
       print( ' Looking for index file ')
       if ( os.path.isfile(indexfile) ):
           for index, row in enumerate(csv.reader(open(indexfile))):
               if row[0] == 'currindex' :
                   startidx = int(row[1])
       print(' Looking for barcode file')
       if not (os.path.isfile(barcodefile)):
           print('Error reading barcodefile')
       else:
           barcodes_df = pandas.read_csv(barcodefile)
       print(' barcodes :: ' , barcodes_df)    
       thisbarcode = barcodes_df.iloc[startidx].values[0]  
   
   print(' Using barcorde ', thisbarcode) 
   bc = barCodes.BarCodes()
   thisruninfo  = bc.decodeBarCodeType(thisbarcode)
   hamiltoninfo = {}
   hamiltoninfo['Through'] = 1
   if (('CP' in thisruninfo['PlateType']) or ( 'SP' in thisruninfo['PlateType'] ) ):
       fluidbased = True
   else:
       fluidbased = False
   if ((thisruninfo['FillStyle'] != 'ICP' ) or (thisruninfo['FillStyle'] != 'UCP')):
       if (fluidbased):
           if thisruninfo['FluidType'] in fluidthroughdict:
               hamiltoninfo['Through'] = fluidthroughdict[thisruninfo['FluidType']]
       else:    
           if thisruninfo['Concentration'] in throughdict:
               hamiltoninfo['Through'] = throughdict[thisruninfo['Concentration']]
   hamiltoninfo['Plate'] = thisruninfo['PlateType'].split('_')[0]
   hamiltoninfo['Liquid'] = thisruninfo['FluidType']
   hamiltoninfo['fillPattern'] = thisruninfo['FillStyle']
   hamiltoninfo['Volume'] = thisruninfo['Volume']
   hamiltoninfo_df = pandas.DataFrame(hamiltoninfo, index=[0])
   hamiltoninfo_df.to_csv(hamiltonfile, index=False, columns=['Through','Plate','Liquid','fillPattern','Volume'])
   print(hamiltoninfo)
   startidx += 1
   idxdict ={}
   idxdict['currindex'] = startidx
   idxdf = pandas.DataFrame(idxdict, index=[0])
   idxdf.T.to_csv(indexfile, index=True, header=False)
   return
   
if __name__ == "__main__":
   main(sys.argv[1:])   