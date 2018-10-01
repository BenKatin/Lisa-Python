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
import subprocess
if __package__ is None or __package__ == '':
    from pyCyte.PlateQC import barCodes
else:
    from ..PlateQC import barCodes

def main(argv):
    HamiltonFile = ""
    BarCode = ""
    try:
      opts, args = getopt.getopt(argv,"hH:b:",["HamiltonFile=","BarCode="])
    except getopt.GetoptError:
      print( 'Unknown argument .. please specify: ') 
      print( 'philPlate.py -H <HamiltonFile> -b <BarCode> ')
      sys.exit(2)
    for opt, arg in opts:
      if opt == '-h':
         print(' Help function .. ')
         print( 'philPlate.py -H <HamiltonFile> -b <BarCode>')
         sys.exit()
      elif opt in ("-H", "--HamiltonFile"):
         HamiltonFile = arg
      elif opt in ("-b","--BarCode"):
         BarCode = arg
    if HamiltonFile == "":
        print('Please specify hamiltonfile !' )
        sys.exit()
    # first thing to do is to generate the through file for the hamilton
    # FIXME this shouldn't be harcoded
    print(' Launching genHamilton using barcode :: ', BarCode)
    #commandline = "C:/Labcyte/PYTHON/pyCyte/PlateQC/genHamilton.py -b \"" + BarCode + "\""
    commandline = "C:/Labcyte/PYTHON/pyCyte/PlateQC/genHamilton.py"
  #  theproc = subprocess.Popen([sys.executable, commandline])
    theproc = subprocess.check_call(["C:\Program Files\Anaconda3\python.exe",commandline,"-b",BarCode])
    # now we are engaging the hamilton itself     
    print(' Launching HxRun using HamiltonFile : ', HamiltonFile)
    theproc = subprocess.check_call(["C:\Program Files\HAMILTON\Bin\HxRun.exe",HamiltonFile,"-t"])
    return
   
if __name__ == "__main__":
   main(sys.argv[1:])   