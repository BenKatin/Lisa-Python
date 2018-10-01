# -*- coding: utf-8 -*-
"""
Created on Sat Jan 30 22:00:13 2016

@author: avandenbroucke
"""

import numpy as np
from lmfit.models import GaussianModel
import matplotlib.pyplot as plt
from scipy.fftpack import fft
import os
import fnmatch
import zipfile

def plotMatrix(matrix, title='title', range=None, savedir=None, fileappendix='', ax=None, displayVal = False):
    """ Plots a 2d numpy array. """
    if (  ax == None  ):
        fig, ax = plt.subplots(figsize=(40,8), nrows=1, ncols=1);
    if range:
        img = ax.imshow(matrix, interpolation='None', vmin=range[0], vmax=range[1]); 
    else:
        img = ax.imshow(matrix, interpolation='None'); 
    ax.set_title(title)
    ax.set_xlabel('Row')
    ax.set_ylabel('Col')
    plt.colorbar(img, ax=ax);
    plt.subplots_adjust(hspace=.6,top=.85)
    #plt.suptitle(title,size=16,x=.5,y=.999)
    if (displayVal):
        for (j,i),label in np.ndenumerate(matrix):
#            ax.text(i,j,label,ha='center',va='center',color='white')
            ax.text(i,j,"{0:.1f}".format(label),ha='center',va='center',color='white', fontsize=8)

#        ax2.text(i,j,label,ha='center',va='center')
    if savedir != None:
        if (fileappendix != []):
            filename = title + '_' + fileappendix
        else:
            filename = title
        pngfilename = os.path.join(savedir, filename)
        pngfilename += '.png'
        plt.savefig(pngfilename,dpi=200,bbox_inches='tight')   
    #plt.show()    
    return;    
    

def getFileList(pattern='*platesurvey.csv', wdir='.'):
     """Finds all files in all subfolders of cwd that match the pattern in folder `wdir`. Returns list"""      
     printfilelist = []
     for root, dirs, files in os.walk(wdir):
         for k in fnmatch.filter(files, pattern):
             printfilelist.append(os.path.join(root,k))  
     return printfilelist     

def fitSimpleHist(array, title='E5XX', nbins=25, xlabel='mytit',  verbose=False, savedir=None, fileappendix = '', ax=None):
    """ Simple Gaussian fit to an array of datapoints. Output can be saved to file if wanted 
    Input Argument:
        array        -- np.array of input points
        title        -- title of graph. Will also be the filename
        nbins        -- number of histogram bins
        xlabel       -- label on x-axis
        verbose      -- T/F print the fit report
        savedir      -- Directory to save output to, if not specified nothing will be saved. Suggest os.getcwd() or '.'
        fileappendix -- will add "_fileappendix" to the filename specified by title.
    """    
    gausfit = GaussianModel()
    if (ax == None) :
        fig, ax = plt.subplots(figsize=(15,3), nrows=1, ncols=1);    
    redarray = array[array >= (array.mean()- 5*array.std())] # and array<= (array.mean()+ 5*array.std())]
    n, bins, patches = ax.hist( redarray[redarray <= array.mean() + 5*array.std()] , nbins )
    cbins = np.zeros(len(bins)-1)
    for k in (range(0,len(bins)-1)):
        cbins[k] = (bins[k]+bins[k+1])/2
    pars = gausfit.guess(n,x=cbins)    
    fitresult = gausfit.fit(n, pars, x=cbins)
    if (verbose):
        print(fitresult.fit_report())
    ax.plot(cbins,fitresult.best_fit,'r-', linewidth=2)
    mean = fitresult.best_values['center']
    fwhm = 2.35*fitresult.best_values['sigma']
    textstring = ' Mean : ' + '{:4.3f}'.format(mean) + '\n'
    textstring += ' FWHM : ' + '{:4.3f}'.format(fwhm)
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.05, 0.95, textstring, transform=ax.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)    
    ax.set_xlabel(xlabel)
    ax.set_ylabel('Frequency')
    ax.set_title(title) 
    if savedir != None:
        filename = os.path.join(savedir, title)
        if (fileappendix != '' ):
            filename += '_' + fileappendix
        filename += '.png'
        plt.savefig(filename,dpi=200,bbox_inches='tight')
 #   plt.show()  
 #   return    
    return fitresult
    
    
def simpleFFT(xval,samplerate=500e6,resolution=8192):
    """ Simple Fast Fourier Transform. Returns xf, yy with xf the frequency axis and yy the strength of each frequency
    Simple plotting is done using plt.plot(xf[0:250],  yy[0:250]) for example
    Input Arguments:
        xval       -- list of time domain values, a simple list, not a list of lists !
        samplerate -- time domain sample rate in Hz
        resolution -- resolution of the fft
    """    
    xnp = np.array(xval, dtype='double')
#   print(xnp)
    T = 1/samplerate
    xf = np.arange(0.0, 8196, 1.0e-6/(resolution*T))
#        print(xf)
    yf = fft(xnp, 8196)
#        print(yf)
    yy = np.abs(yf)
    return xf, yy    
    
def zipfolder(folder= None, zipFileFolder = None, zipFileName= None, verbose=False, mode="w"):
    if not folder:
        folder = os.getcwd()
    if not zipFileName:
        zipFileName = os.path.basename(folder) + '.zip'
  #  zipF = os.path.join(folder,zipFileName)    
    if not zipFileFolder:
        zipFileFolder = folder
    print(' Creating ZIP archive', zipFileName, ' in folder ', zipFileFolder)    
    if not os.path.exists(zipFileFolder):
        print(folder, ' does not exist -- EXITING')
        return
    thisdir = os.getcwd() 
    if zipFileFolder == folder:
        os.chdir(folder)    
        tfolder = './'
    else:
        tfolder = './' + folder
    zipFile = zipfile.ZipFile(os.path.join(zipFileFolder,zipFileName), mode)    
    for root,dirs,file in os.walk(tfolder):
        for name in file:
            if (verbose):
                print(' Adding ', os.path.join(root,name))
            if not name.endswith('.zip'):
                zipFile.write(os.path.join(root,name))
    zipFile.close()
    os.chdir(thisdir)
    return        