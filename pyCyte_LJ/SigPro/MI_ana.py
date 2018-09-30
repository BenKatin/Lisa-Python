# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 14:11:54 2016

@author: avandenbroucke
"""


import matplotlib.pyplot as plt
import numpy as np
#from mmSpy import MedManSpy as ms
from mmSpy.v2_5_x import MedManSpy as ms
from scipy import signal
import h5py

class MI_ana():
    
    def __init__(self, filename=None):
        self.MI = ms.MoundEchoAnalysis()
        if (filename):
            self.openfile(filename)
        return

# instantiate MoundEchoAnalysis class
#MI = ms.MoundEchoAnalysis()

# open h5 file
    
    def openfile(self,filename= './2016-03-18_07-14-32_384PP_AQ_CP__AQ_FT.h5', filepath=''):
        self.h5file = h5py.File(filepath + filename,'r')
        self.getMIparams()
        return

    def getMIparams(self):
        # load MISettings from h5file
        MiSettings_G = self.h5file['MISettings/General Settings']
        MiSettings_O = self.h5file['MISettings/OverPower Analysis']
        MiSettings_P = self.h5file['MISettings/Preamble']
        MiSettings_TX = self.h5file['MISettings/Transducer Properties']
        self.overpowermethod = 0
        
        # Set MoundEchoAnalysis parameters. Rather than explicit getters/setters, 
        # I tried to use struct like accessors to the MoundEchoAnalysis class parameters
        self.MI.mi_param.TargetFreqStartMhz = float(MiSettings_G['targFreqStartMHz'][0])
        self.MI.mi_param.TargetFreqStopMhz  = float(MiSettings_G['targFreqEndMHz'][0])
        self.MI.mi_param.FFTStartMhz        = float(MiSettings_G['fftStartFreqMHz'][0])
        self.MI.mi_param.FFTStopMHz         = float(MiSettings_G['fftEndFreqMHz'][0])
        self.MI.mi_param.MinGoodWidth       = float(MiSettings_G['minGoodMoundWidthCycles'][0])
        self.MI.mi_param.MoundStartUs       = float(MiSettings_G['moundStartUs'][0])
        self.MI.mi_param.MoundStopUs        = float(MiSettings_G['moundStopUs'][0])
        self.MI.mi_param.MaxGoodNullMHz     = float(MiSettings_G['maxGoodNullSpacingMHz'][0])
        self.MI.mi_param.MoundAdjustedStop  = int(MiSettings_G['moundAdjustedStop'][0])
        self.MI.mi_param.minPeakFactor      = float(MiSettings_G['minPeakFactor'][0])
        self.MI.mi_param.maxPeakFactor      = float(MiSettings_G['maxPeakFactor'][0])
        self.MI.mi_param.ImpedanceBasedTPF  = bool(MiSettings_G['impedanceBasedTPF'][0])
        self.MI.mi_param.ImpedanceToTPFFactor = float(MiSettings_G['impedancetoTPFFactor'][0])
        self.MI.mi_param.MinTargetPeakHeight = int(MiSettings_G['minTargetPeakHeight'][0])
        
        self.MI.mi_param.MatrixStartCycles  = float(MiSettings_O['MatrixStartCycles'][0])
        self.MI.mi_param.MatrixWidthCycles  = float(MiSettings_O['MatrixWidthCycles'][0])
        self.MI.mi_param.MinVrms            = float(MiSettings_O['minVrms'][0])
        self.MI.mi_param.RingAmplitudeThreshold = float(MiSettings_O['ringingFreqThreshMHz'][0])
        self.MI.mi_param.RingFreqThresholdMHz   = float(MiSettings_O['ringingAmpThreshVpp'][0])
        self.MI.mi_param.TransducerFreqMhz  = float(MiSettings_TX['transducerFrequencyMHz'][0])
        self.MI.mi_param.SampleRateMhz      = float(MiSettings_TX['sampleRateMHz'][0])
        # not in h5 file
        self.MI.mi_param.ProcessSize4FFT    = 0  
        
        # Here we're setting the preamble 
        self.MI.mi_param.EnablePreamblePace = False
        self.MI.mi_param.EnablePreambleFFT = False
        self.MI.mi_param.EnablePremablePrePing = False
        preambletype = MiSettings_P['preambleType'][0].decode('utf-8')
        if 'FFT' in preambletype:
            self.MI.mi_param.EnablePreambleFFT = True
            self.MI.mi_param.SweptFFTResolutionMHz = float(MiSettings_P['fftPreambleResMHz'][0]) 
            self.MI.mi_param.SweptFFTAlgoType = int(MiSettings_P['fftPreambleAlg'][0])
        else:
          if 'PACE' in preambletype:
            self.MI.mi_param.EnablePreamblePace = True
          else:
            self.MI.mi_param.EnablePreamblePrePing = True
            self.MI.mi_param.PrePingRHilbMaxCycles = float(MiSettings_P['prePingPreambleRHilbertMaxCycles'][0])
         
        return 
        
    # Note that I need to work on methods dealing with the PreamblePrePing method, as these are handled slightly differently
    # Would have to extract and set a fixed preamble through preambleAdjust  ::  0
    # I need in any case the ability of fixing the preamble
        
    
    def getMISequence(self,wellcombo='A1-A1',tier=0):
        mipsequence = self.h5file['Transfer/' + wellcombo + '/RTMIP-T' + str(tier) + '/PowerSweep']
        return mipsequence

    # NEED to add impedance here.    
    def processMoundEcho(self,wellcombo='A1-A1',i=-1, tier=0 ):
        # get mipsequence from file
        mipsequence = self.getMISequence(wellcombo,tier)
        # get waveform i from sequence
        wav = mipsequence[i][0][:]
        totaliterations = 0 
        sh = np.shape(mipsequence)
        totaliterations = sh[0] 
        if (i==-1):
            thisiteration = totaliterations
        else:
            thisiteration = i
        # convert to list of float
        wavL = [ float(r) for r in wav ]
        # perfrom MoundImage Analysis via MedManSpy
        miana = self.MI.MoundImageAnalysis(wavL)
        # get the fft from MedManSpy
        fft = self.MI.GetFFT()
        # make little plot 
        fig, ax = plt.subplots(nrows=1,ncols=2,figsize=(15,3))       
        ax[0].plot(wavL) ; 
        ax[0].axvline(miana['Preamble'], color='k', linewidth=2); 
        ax[0].axvline(miana['Preamble']+miana['PeakSeparation']*self.MI.mi_param.SampleRateMhz/self.MI.mi_param.TransducerFreqMhz, color='r', linewidth=2  )
        if (len(fft) > 0 ):
            freqax = np.arange( self.MI.mi_param.FFTStartMhz, self.MI.mi_param.FFTStopMHz,(self.MI.mi_param.FFTStopMHz-self.MI.mi_param.FFTStartMhz)/len(fft) )
            ax[1].plot(freqax,fft)
        fig.suptitle(' Well : ' + wellcombo + ' iteration ' + str(thisiteration) + '/' + str(totaliterations),fontsize=14)
        fig.subplots_adjust(top=0.8)
        return wavL, miana
    

    def EnableSweptFFT(self,algtype=1,resolutionMHz=0.240):
        self.MI.mi_param.EnablePremblePace = False
        self.MI.mi_param.EneablePreamblePrePing = False
        self.MI.mi_param.EnablePreambleFFT = True
        self.MI.mi_param.SweptFFTResolutionMHz = resolutionMHz
        self.MI.mi_param.SweptFFTAlgoType = algtype
        return

    def SweptFFTDebug(self,wellcombo='A1-A1',iteration=-1,tier=0,nsamples=600):
        wav, miana = self.processMoundEcho(wellcombo,iteration,tier)
        sweptFFTDebugInfo = self.MI.GetSweptFFTDebug()
        self.plotSweptFFTDebug(sweptFFTDebugInfo,wav, miana, nsamples)
        return
        

    def plotSweptFFTDebug(self,sweptfftdict, wav, miana, nsamples=600):
        fig,ax = plt.subplots(4,1,figsize=(15,9))
        ax[0].plot(wav[::2][0:nsamples])
        ax[0].axvline(x=sweptfftdict['FFTPreamble'],color='black')
        # divide by 2 here because the debug waveforms are downsampled by 2 
        ax[0].axvline(x=miana['P1Position']/2,color='blue')
        ax[0].axvline(x=miana['HilbertMaxIndex']/2,color='hotpink')
        hilbertenv = np.abs(signal.hilbert(wav[::2][0:nsamples]))
        ax[0].plot(hilbertenv,color='green')
        ax[1].plot(sweptfftdict['FFTMag'][0:nsamples])
        ax[1].axhline(y=sweptfftdict['FFTMagThresh'],color='r') 
        ax[2].plot(sweptfftdict['FFTDMag'][0:nsamples])
        ax[2].axhline(y=sweptfftdict['FFTDMagThres'],color='r')
        ax[3].plot(sweptfftdict['FFTFreq'][0:nsamples])
        ax[3].axhline(y=sweptfftdict['FFTFreqThresh'],color='r')
        ax[3].axvline(x=sweptfftdict['FFTPreamble'],color='black')
        return 

    def isOverPower(self, miana):
        # For 55X
        if (self.overpowermethod == 0) :
            c1 = (miana['RingFrequency'] > self.MI.mi_param.RingFreqThresholdMHz) and \
                 (miana['RingAmplitude'] > self.MI.mi_param.RingAmplitudeThreshold) and \
                 ( miana['PeakSeparation'] >= self.MI.mi_param.minPeakSeparation)
            c2 = (miana['RingFrequency'] > (self.MI.mi_param.RingFreqThresholdMHz + 2.0)) and \
                 (miana['PeakSeparation'] > (self.MI.mi_param.minPeakSeparation + 1.0)) and \
                 (miana['RingAmplitude'] >= 20.0) 
            c3 = (miana['PeakSeparation'] > (self.MI.mi_param.minPeakSeparation + 3.0)) and \
                 (miana['Vrms'] > self.MI.mi_param.MinVrms )
            #c3 = (miana['Vrms'] > self.MI.mi_param.MinVrms ) 
            c4 = (miana['PeakSeparation'] >= (self.MI.mi_param.minPeakSeparation + 1.2)) and \
                 (miana['MoundWidth'] > (self.MI.mi_param.minPeakSeparation + 1.2)) and \
                 (miana['RingDecay'] > 4.5) ;
        elif (self.overpowermethod == 1):
            c1 = (miana['RingFrequency'] > self.MI.mi_param.RingFreqThresholdMHz) and \
                 (miana['RingAmplitude'] > self.MI.mi_param.RingAmplitudeThreshold) and \
                 ( miana['PeakSeparation'] >= self.MI.mi_param.minPeakSeparation)
            c2 = (miana['RingFrequency'] > (self.MI.mi_param.RingFreqThresholdMHz + 2.0)) and \
                 (miana['PeakSeparation'] > (self.MI.mi_param.minPeakSeparation + 1.0)) and \
                 (miana['RingAmplitude'] >= 20.0) 
            c3 = (miana['Vrms'] > self.MI.mi_param.MinVrms ) 
            c4 = (miana['PeakSeparation'] >= (self.MI.mi_param.minPeakSeparation + 1.2)) and \
                 (miana['MoundWidth'] > (self.MI.mi_param.minPeakSeparation + 1.2)) and \
                 (miana['RingDecay'] > 4.5) ;
        else:
            print(' Unknown overpower analysis method #', self.overpowermethod)
            return 1
        overpower = 0 
        overpower |= ( c1 << 3)
        overpower |= ( c2 << 2)
        overpower |= ( c3 << 1)
        overpower |=  ( c4 )
        return overpower
        

        
# helpder function that displays compound dataset:
    def listCompoundDataSetFields(self,dataset, index=0, verbose=False):
        keys = []    
        for ee in dataset.dtype.descr:
            keys.append(ee[0])
        if (verbose):    
            for entry in keys:
                print( entry, ' :: ', dataset[entry][index])    
        return keys
    
    def printMIparams(self):
        print('TargFreqRangeMHz    : ',self.MI.mi_param.TargetFreqStartMhz, ' - ', self.MI.mi_param.TargetFreqStopMhz )
        print('FFTRangeMHz         : ',self.MI.mi_param.FFTStartMhz, ' - ', self.MI.mi_param.FFTStopMHz )
        print('MoundRangeUs        : ',self.MI.mi_param.MoundStartUs, ' - ', self.MI.mi_param.MoundStopUs )
        print('PeakFactorRange     : ', self.MI.mi_param.minPeakFactor, ' - ',  self.MI.mi_param.maxPeakFactor )  
        print('Mtrx Start - Range  :', self.MI.mi_param.MatrixStartCycles, ' - ', self.MI.mi_param.MatrixWidthCycles )
        print('Ringing Amp - Freq  :',  self.MI.mi_param.RingAmplitudeThreshold, ' - ', self.MI.mi_param.RingFreqThresholdMHz )
        print('TxFreq - SampleRate :', self.MI.mi_param.TransducerFreqMhz, ' - ', self.MI.mi_param.SampleRateMhz)
        print('MinGoodWidth        :', self.MI.mi_param.MinGoodWidth)
        print('MaxGoodNullMhz      :', self.MI.mi_param.MaxGoodNullMHz)
        print('MoundAdjustedStop   :', self.MI.mi_param.MoundAdjustedStop)
        print('EnablePreamblePace  :', self.MI.mi_param.EnablePreamblePace)
        print('EnablePreambleFFT   :', self.MI.mi_param.EnablePreambleFFT)
        print('EnablePreamlePrePing:', self.MI.mi_param.EnablePreamblePrePing)
        print('SweptFFTAlgoType    :', self.MI.mi_param.SweptFFTAlgoType)
        print('PrepingRHilbMaxCycl :', self.MI.mi_param.PrePingRHilbMaxCycles)
        
# compare with data in h5file:
# Get the MI Analysis from file
    # process last waveform in Tier 1
    def scratch(self):
        miana = self.processMoundEcho(-1,1)
        print(miana)
        wellcombo = 'A1-A1'
        tier = 1    
        mipanalysis = self.h5file['Transfer/' + wellcombo + '/RTMIP-T' + str(tier) + '/MIPAnalysis']
        keys = self.listCompoundDataSetFields(mipanalysis,True)
        return