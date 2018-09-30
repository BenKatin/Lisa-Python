# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 21:56:15 2016

@author: avandenbroucke
"""


import sys
import getopt
import os
import pandas
from lxml import etree
if __package__ is None or __package__ == '':
    from pyCyte.PlateQC import barCodes
    from pyCyte.PlateQC import EPA_Ana
else:
    from ..PlateQC import barCodes
    from ..PlateQC import EPA_Ana
# from shutil import copyfile

def main(argv):
   epadir = ''
   try:
      opts, args = getopt.getopt(argv,"hr:d:",["RunID=","wdir="])
   except getopt.GetoptError:
      print( 'processEPA.py -r <RunID> -d <workdir>')
      sys.exit(2)
      
   for opt, arg in opts:
      print(' opt: ' ,opt)
      if opt == '-h':
         print( 'processEPA.py -r <RunID> -d <workdir>')
         sys.exit()
      elif opt in ("-r", "--RunID"):
         runID = arg
         print(' using runID : ', runID)
      elif opt in ("-d", "--wdir"):
         epadir = arg
         print(' using epadir : ', epadir)
   print(' processing EPA data in folder ', epadir)      
   if (epadir == ''):
       epadir = 'C:\Labcyte\Echo\Reports\Labcyte Echo Plate Audit\\' + str(runID)
   if not os.path.exists(epadir):
       print(' *** ERROR **** FOLDER ', epadir, ' not found !')
       return -1
   thisdir = os.getcwd()   
   rundir = 'C:\Labcyte\Tempo\Logs'
   inboxfolder = 'C:\Labcyte\Tempo\Logs\Scheduler\Inbox'

   print(' processing EPA data in folder ', epadir)
   os.chdir(epadir)  
#   print('dir content:', os.listdir())
   res = EPA_Ana.processEPAFolder(runID)
#   print(' EPA Results: ' )
#   print(res)
   return
   platesdf = pandas.read_csv(rundir + '\Run_' + str(runID) + '\PlateData_' + str(runID) + '.csv', skipinitialspace=True) 
   platesxml = etree.parse(rundir + '\Run_' + str(runID) + '\Plates' + str(runID) + '.xml') 
   plates = platesxml.getroot()
   # here I have access to all plate locations but no barcodes 
   for plate in plates:
       plateid = plate.attrib['id']
       print(' looking for plateid : ', plateid)
       bc = platesdf['Plate Barcode'][platesdf['Plate ID'] == int(plateid)].iloc[0]
       print(' barcode for plate ', plate, ' : ', bc)
       epa_results = [ r for r in res if r['barcode'] == bc ]
       passed = epa_results[0]['Pass']
       if passed:
           plates.remove(plate)
  
   nplates = len(plates)     
        
   rdef = etree.parse(os.path.dirname(sys.argv[0]) + '/Move_plates.rundef')
    
   # find platemap::
   platemap = rdef.findall('//PlateMap')[0]
   # remove all existing plates in platemap:
   for p in platemap:
        platemap.remove(p)
    
    
    
    #add plates that need to be moved:
    # note:: I might need to change the attrib
    # plate.attrib['finalLocation'] =     
   for plate in plates:
        loc = plate.attrib['finalLocation']
        plate.attrib['finalLocation'] = loc.replace('Deck/2','Deck/3')
        rdef.findall('//PlateMap')[0].append(plate)
    
   rdef.findall('//numofplate')[0].text = str(nplates)
    
#   xmloutstring = etree.tostring(rdef)
   with open(rundir + '\Run_' + str(runID) + './EPA_Move.rundef', 'w') as file_handle:
        file_handle.write(etree.tostring(rdef, pretty_print=True, encoding='utf8').decode('utf-8')) 
   print(' writing output to :: ' , inboxfolder + './EPA_Move.rundef') 
   with open(inboxfolder + './EPA_Move.rundef', 'w') as file_handle:
        file_handle.write(etree.tostring(rdef, pretty_print=True, encoding='utf8').decode('utf-8'))   
       
     
   return   
       
if __name__ == "__main__":
   main(sys.argv[1:])      