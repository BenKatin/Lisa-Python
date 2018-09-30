# -*- coding: utf-8 -*-

"""
Created on Wed Oct 14 12:16:26 2015


How to run this:

e.g. :

 runfile('H:/2015/Q4/PythonScripts/Coupled_input.py', wdir='N:\\PROD_INSTRUMENTS\\2015_UNITS\\E5XX-1552\\TBW')
 allfitdat = processall() 

@author: avandenbroucke
"""
from scipy.fftpack import fft
from scipy.optimize import curve_fit
from lmfit.models import LinearModel, LorentzianModel, GaussianModel
from scipy import signal
import numpy as np
import matplotlib.pyplot as plt
import csv
import os

# Number of samplepoints
N = 250
# sample spacing
T = 2.0e-9

# Master folder
MasterDir='\\\\fserver\\picodocs\\Projects_2016-17\\Transducer_Swap\\Instruments'

def processall(folders=['./Diff_Freq','./Diff_Freq'], plotnames=['TX','50Ohm'], filename='TBW', yrange=[0.90,1.05], verbose=False):
    """Compares at least two folders that contain frequency responses for single frequencies.
The folders need to be passed as a list. plotnames are the names for the legend in the graph, filename is the outputfilename.    
    """
   # folders=['./Diff_Freq', './Diff_Freq_resistor_after_matching_circuit', './Diff_Freq_resistor_before_matching_circuit']
     
  #  folders=['./Diff_Freq','./Diff_Freq']#,'./Diff_Freq']
    #plotnames=('TX','PreMatch','PostMatch')
    if (len(folders) < 2 ):
        print('due to poor programming, minimum number of folders required is 2. You only gave me ', len(folders))
        return

    for k, val in enumerate(folders):
        filelist = processfolder(val)
        allfits=[]
        for s in filelist:
           fitvals = processfile(s[0],s[1], verbose)
           allfits.append(fitvals)
        allfitsnp = np.array(allfits,dtype='float')    
        if k==0:
            allfitdat = allfitsnp
        else:
            allfitdat = np.dstack((allfitdat,allfitsnp))
    plot3(allfitdat, plotnames, filename, yrange, len(folders))        
    savefitdat(allfitdat, plotnames, filename + '.txt' )
    return allfitdat

def savefitdat(fitdata, plotnames, filename='TBW.txt'):
    'Solution suggested by http://stackoverflow.com/questions/3685265/how-to-write-a-multidimensional-array-to-a-text-file'
    # shape of array:
    header=['#Frequency','FWHM','FWHM-SE','MEAN','MEAN-SE','AMPLITUDE','AMPLITUDE-SE','\n']
    arshape = fitdata.shape
    entries = 1
    for i in arshape:
        entries *= i
#    data = np.arange(entries).reshape(arshape)  
    # Write the array to disk
    with open(filename, 'wb') as outfile:
    # I'm writing a header here just for the sake of readability
    # Any line starting with "#" will be ignored by numpy.loadtxt
        outfile.write(bytes('# Array shape: {0}\n'.format(fitdata.shape),'UTF-8'))

        # Iterating through a ndimensional array produces slices along
        # the last axis. This is equivalent to data[i,:,:] in this case
        for i in range(0,arshape[2]):
             text = '# ' + plotnames[i] + '\n'
             outfile.write(bytes(text,'UTF-8'))
             for ii,hdr in enumerate(header):
                 if ii==0:
                     hdrtext = hdr
                 else:   
                     hdrtext= ' ' + hdr 
                 outfile.write(bytes(hdrtext,'UTF-8'))
                 
#             for ii in range(0,arshape[1]):
             np.savetxt(outfile, fitdata[:,:,i] )
    return

def plot3(dd,plotnames, ti='TBW', ylim=[0.90,1.05], ndatasets = 3):
    fig = plt.figure()
    #ndatasets = 1
    nrows = 3
    fig, axes = plt.subplots(nrows=nrows, ncols=1, figsize=(8,12))
    parameternames=['fwhm', 'center', 'AUC']
    markerlist=['o','s','^','v','<','>']
    markercolor=['b', 'g', 'r', 'c', 'm', 'y', 'k']
    # turn off all axes:
    print(" plotname: ", plotnames)    
    for k in range(0,nrows):
       off = k*2 
       for kk in range(0,ndatasets):
           if (k==2):
                # we are scaling the 'AUC' relative to the value at 9 MHz
               # index of 9MHz in array
               idx = np.argmin(np.abs(dd[:,0,kk] - 9))
               scale= 1/dd[idx,off+1,kk]
           else:
               scale=1
           axes[k].errorbar(dd[:,0,kk], dd[:,off+1,kk]*scale, yerr=dd[:,off+2,kk]*scale, ls='None',marker=markerlist[kk],color=markercolor[kk],label=plotnames[kk])
       axes[k].set_title(parameternames[k])
       if k==0:
           box = axes[k].get_position()
           axes[k].set_position([box.x0, box.y0, box.width * 0.8, box.height])
            # Put a legend to the right of the current axis
           axes[k].legend(numpoints=1, loc='center left', bbox_to_anchor=(1, 0.5))
        
       axes[k].grid()  
#        axes[rowcount,colcount].set_ylim(ylo,yhi)
       ymin = np.min(dd[:,off+1,:])*scale
       ymax = np.max(dd[:,off+1,:])*scale
       yrange = ymax-ymin
       ymin -= 0.1*yrange
       ymax += 0.1*yrange
       axes[k].set_ylim(ymin,ymax)
       axes[k].set_xlim(np.min(dd[:,0,0])-0.5,np.max(dd[:,0,0])+0.5)
       axes[k].set_xlabel('Frequency (MHz)')
       axes[k].set_ylabel('FitVal')
       if k==2:
           axes[k].set_ylabel('FitVal/FitVal@9MHz')
           axes[k].set_ylim(ylim[0],ylim[1] )               
              
    fig.subplots_adjust(hspace=0.6, wspace=0.4)
#    ax.legend()
    #plt.show()
    fi = plt.gcf()
    print("Current working dir: ", os.getcwd())
    basedir = os.getcwd()
    file = basedir + "\\" + ti + '.png'
    fi.savefig(file,bbox_inches='tight')
    file = basedir + "\\" + ti + '.svg'
    fi.savefig(file,bbox_inches='tight')
    plt.show()
    return

def processfolder(folder="."):
    refdir = os.path.abspath(os.getcwd())
    udir = os.path.abspath(os.path.join(os.getcwd(), folder, ''))
    filelist = []
    for i in os.listdir(udir):
        path = udir + "\\" + i
        #print(path)
        os.chdir(path)
        if path.endswith("50"):
            for ii in os.listdir(os.getcwd()):
                #print(ii)
                if ii.endswith("coupled_input.csv"):
                    file = path + "\\" + ii
                    filelist.append([file, path])
            os.chdir(udir)     
    os.chdir(refdir)
    return filelist    
        
        
def processfile(filename, filepath, verbose=False):        
    folder = os.path.basename(os.path.normpath(filepath))
    frequency = folder.split('MHz')[0]
    fitdat = coupled_input(filename, verbose)
    fitpar = fitdat.params
    parameternames=['fwhm', 'center', 'amplitude']
    fitvals = [frequency]
    for k in parameternames:
         val = [fitpar[k].value, fitpar[k].stderr]
         for kk in range(0,2):
             fitvals.append(val[kk])     
 #       mean = fitpar('center')       
    return fitvals

def coupled_input(filename='2015-10-13_16-20-22_coupled_input.csv', verbose=False):
    xval = []
    gausfit = GaussianModel()
    with open(filename, newline='') as csvfile:
        csv_f = csv.reader(csvfile)
        nlines = 0
        start = 0
        for row in csv_f:
            if (len(row) > 0):
                if (row[0] == '0'):
                    if (verbose):
                        print(row[1])
                        print(" *********")
                    start = 1
                if (start == 1):
                    nlines = nlines + 1
                    xval.append(row[1])
        if (verbose):            
            print(" read %d lines from file %s" % (nlines, filename))
        xnp = np.array(xval, dtype='double')
#        print(xnp)
        xf = np.arange(0.0, 8196, 1.0e-6/(8196*T))
#        print(xf)
        yf = fft(xnp, 8196)
#        print(yf)
        yy = np.abs(yf[0:250])
        maxindex = yy.argmax()
        lim2 = maxindex + 20
        lim1 = maxindex - 20
        pars = gausfit.guess(yy[lim1:lim2], xf[lim1:lim2])
#       out = mod.fit(np.abs(yf[0:250]), pars, x=xf[0:250])
        out = gausfit.fit(yy[lim1:lim2], pars, x=xf[lim1:lim2])
        if (verbose):
            print(out.fit_report(min_correl=0.25))
            fig, ax = plt.subplots()
            ax.plot(xf[0:250],  yy[0:250]) 
            plt.plot(xf[lim1:lim2], out.best_fit, 'r-')
    return out        
   #     peakind = signal.find_peaks_cwt(yy[0:250], np.arange(1,5))
    #    peakind, xf[peakind], np.abs(yf[peakind])
     #   print(peakind)
   


#filelist = []
#for i in os.listdir(os.getcwd()):
#if i.endswith(".csv"):
#filelist.append(i)
#for s in filelist:
#coupled_input(s)
