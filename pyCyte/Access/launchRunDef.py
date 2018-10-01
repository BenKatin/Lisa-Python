# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 20:28:53 2017

@author: lchang
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 08:15:06 2016

@author: lchang
"""

import sys, getopt
#import argparse
import os
import shutil
import tkinter
import tkinter.filedialog as FD
import errno
import pandas as pd
import datetime
import time
import subprocess
import fnmatch
from ..ToolBox import SimpleTools as st


def main(argv):
    
    file1 = 'C:\\Labcyte\\Tempo\\Protocols\\LilianC\\LC_readMatech_5x.rundef'
    file2 = 'C:\\Labcyte\\Tempo\\Protocols\\LilianC\\LC_readMatech_1x.rundef'
    destination = 'C:\\Labcyte\\Tempo\\Logs\\scheduler\\inbox'
    matechlock = 'C:\\Labcyte\\Tempo\\MatechInProgress.lock'
            
    try:
        opts, args = getopt.getopt(argv,"r",["Run="])
    except getopt.GetoptError:
        print( 'Unknown argument .. please specify: ') 
        sys.exit(2)
        
    for opt, arg in opts:
        if opt == '-h':
            print(' Help function .. ')
            sys.exit()
        elif opt in ("-r", "--Run"):
            run = arg
            print(run)
            
    if 'read' in run:
        if run == 'read':
            source = file1
        elif run == 'read1':
            source = file2
        else:
            print('Command not recognized')
            return
                
        if os.path.exists(matechlock):
            print('Another instance of ReadMatech is in progress...')
            return
        
        else:
            matechdir = 'C:\\temp\\'
            matechlog = matechdir+'matechlog.txt'
    #    if not os.path.exists(matechlog):
    #        os.makedirs(matechlog)
            os.chdir(matechdir)
            file = fnmatch.filter(os.listdir(),'matechlog.txt',)
        
            runEnd = datetime.datetime.now()
            runEndtime = time.time()
            de = pd.DataFrame([runEnd])
            de.columns=['Timestamp']
        
            if len(file) == 0:
                de.to_csv(matechlog, index = False)
            df = pd.read_csv(matechlog)
            
            pRun = datetime.datetime.strptime(str(df['Timestamp'].iloc[-1].split('.')[0]), '%Y-%m-%d %H:%M:%S')
            prevRun = time.mktime(pRun.timetuple())
            
            #    runStrt = time.mktime(runS.timetuple())
            delta = runEndtime - prevRun
            if delta >= 1800:
                shutil.copy(source, destination)
                mfile = open(matechlock, 'w+')
                mfile.close()    
                print('<< File:  '+source+' copied to '+destination)
                
            df = df.append(de, ignore_index=True)
            df.to_csv(matechlog, index = False)
        
        return
    
    elif run == 'finish':
        if os.path.exists(matechlock):
            os.remove(matechlock) 
            print('File: '+matechlock+' deleted...')
            return
        else:
            print('File:'+matechlock+' not found... Exiting...')
            return
        
    else:
        print('Not a valid command')
        return


if __name__ == "__main__":
   main(sys.argv[1:])
