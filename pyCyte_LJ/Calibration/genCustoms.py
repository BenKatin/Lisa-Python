# -*- coding: utf-8 -*-
"""
Created on Fri Jun 23 14:39:25 2017

@author: avandenbroucke
"""

if __package__ is None or __package__ == '':
    from pyCyte.ToolBox import SimpleTools
    from pyCyte.Calibration import editEPC
else:
    from ..ToolBox import SimpleTools
    from ..Calibration import editEPC

import os, shutil

def createCustom(customfolder='\\\\fserver\\people\\Arne\\2016\\Lemonade\\MFG_Lemonade\\CUSTOM',srcfolder='../EPC/Calibration/Miscellaneous'):
    if not os.path.exists(customfolder):
       print('Folder ', customfolder, ' does not exists !')
       print('Exiting')
       return
    os.chdir(customfolder)
    epcfiles = SimpleTools.getFileList('*.epc')
    for file in epcfiles:
        folder = os.path.dirname(file)
        outputfolder = folder + './Miscellaneous'
        if not os.path.exists(outputfolder):
            os.mkdir(outputfolder)
        epc = editEPC.parseEPC(file)
        miscfiles = epc.getAllFiles()    
        for filename in miscfiles:
            src = srcfolder + './' + filename
            dest = outputfolder + './' + filename
            if os.path.exists(src):
                shutil.copyfile(src,dest)
            else:
                print(' -- ERROR ---  file ', src, ' does not exist !' )
        zipfoldername = os.path.join(os.getcwd(),folder)    
  #      print( ' zipfoldername : ', zipfoldername, ' os.getcwd() = ' , os.getcwd())
        SimpleTools.zipfolder(folder=zipfoldername)        
        # now delete the miscellaneous folder
        shutil.rmtree(os.path.join(os.getcwd(),outputfolder))
    return 

            