import os
import csv
import pyodbc
import pickle
import xml.etree.ElementTree as ET

# Analysis
import numpy as np
import lmfit as lm
import pandas as pd
import matplotlib.pyplot as plt

#from scipy.interpolate import griddata
from scipy import interpolate


#\\seg\transducer\Instruments\E5XX_1476\TBW_50Ohm_Amp_12MHz
#\\seg\transducer\Instruments\E5XX_1419\TBW_50Ohm_Amp_12MHz
# unsatgain, satslope, switchpoint
DefaultAmpDetails = {'E1419':[54.00671407,50.65038935,1.955707633],
                     'E1476':[53.58584776,50.15981854,2.227800034]}

plateIDs = {  '384PPG_DMSO2' :  0,
              '384PP_DMSO2'  :  0,
              '384PPL_DMSO2' :  1,
              '384LDV_DMSO'  :  2,
              '384LDVS_DMSO' :  2,
              '1536LDV_DMSO' :  3,
              '1536LDVS_DMSO':  3,
              '384LDVS_AQ_B2':  4,
              '384PPG_AQ_BP2':  5,
              '384PPG_AQ_CP' :  6,
              '384PPG_AQ_GP2':  7,
              '384PPG_AQ_SP2':  8,
              '384PPL_AQ_BP2':  9,
              '384PPL_AQ_CP' : 10,
              '384PPL_AQ_GP2': 11,
              '384PPL_AQ_SP2': 12,
              '384LDVS_AQ_P2': 13  
              }

# Seems ot be best for functions to use their own connections... particularly
# around the dicy asyncronous backup/restore operations.
def getCursor(server='localhost', db=None):
    cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';Trusted_Connection=yes;')
    cnxn.autocommit = True  
    c = cnxn.cursor()
  
    if db:
        c.execute("USE " + db)
        
    return c

def unpackXMLTBW(data, plotAx=False):
    root = ET.fromstring(data) # Unpack XML
    TBWData = next(root.iter('TransducerBandwidth')).iter('sample')
    freq, mag = [], []
    for sample in TBWData: # pull two lists of data from attributes in xml "sample" tags
        freq.append(float(sample.attrib["freq"]))
        mag.append(float(sample.attrib["mag" ]))

    if plotAx:
        plotAx.plot(freq, mag, '+')
    
    return freq, mag

def unpackMeanXMLTBW(TBWs, plotAx=False):
    first = True
    i = 1

    for TBW in TBWs:
        
        root = ET.fromstring(TBW[0]) # Unpack XML
        TBWData = next(root.iter('TransducerBandwidth')).iter('sample')
        freq, mag = [], []
    
        for sample in TBWData: # pull two lists of data from attributes in xml "sample" tags
            freq.append(float(sample.attrib["freq"]))
            mag.append(float(sample.attrib["mag" ]))
              
        minCheck = pd.DataFrame(mag, index = freq)[7:17].min(axis=1).min()
        maxCheck = pd.DataFrame(mag, index = freq)[7:17].max(axis=1).max()
        
        # Scrub outliers
        if minCheck < 3 or maxCheck > 18:
            print('omitting wild TBW measurment')
            continue

        if doPlots:
            plt.plot(freq, mag, '+')
            
        if first:
            df = pd.DataFrame(mag, index = freq, columns=[i])
            first = False
        else:
            i+=1
            df[i] = pd.DataFrame(mag, index = freq)
   
    if doPlots:
        if plotAx:
            plotAx.plot(df.index, df.mean(axis=1), 'k-', label='Most recent 2wk mean')
        else:
            plt.plot(df.index, df.mean(axis=1), 'k-', label='Most recent 2wk mean')
            plt.show()

        
    return df.index.values, df.mean(axis=1).values

def doubleGaussFit(tx, freq, mag, plotAx = False):
    a = pd.DataFrame({'Frequency(MHz)':freq,'Frequency Response(dB)':mag})
    gCombined = (    lm.models.GaussianModel(prefix = "low_" )  # Double-Gaussian for fit
                   + lm.models.GaussianModel(prefix = "high_")) 

    pars = gCombined.make_params(low_amplitude  = 10,
                                 low_sigma      =  1,
                                 low_center     =  7.68, #8,
                                 high_amplitude = 10,
                                 high_sigma     =  1,
                                 high_center    = 12.21 ) #14)

    varyPeakPositions = True
    pars.get('low_center').set(vary=varyPeakPositions)
    pars.get('high_center').set(vary=varyPeakPositions)


    fitDat = a[(a['Frequency(MHz)'] > tx['TransducerBandwidthTwinGaussianFitRange'][0]) & (a['Frequency(MHz)'] < tx['TransducerBandwidthTwinGaussianFitRange'][1])]
    xFitDat = list(fitDat['Frequency(MHz)'])
    yFitDat = list(fitDat['Frequency Response(dB)'])

    out = gCombined.fit(yFitDat, pars, x=xFitDat)

    if doPlots:
        if plotAx:
            plotAx.plot(xFitDat, gCombined.eval(out.params, x=np.asarray(xFitDat)),'y-', linewidth=2.0)
        else:
            plotAx.plot(freq, mag, '+')
            plt.plot(xFitDat, gCombined.eval(out.params, x=np.asarray(xFitDat)),'y-', linewidth=2.0)
            plt.show()

    return out.best_values

def linearFit(tx, freq, mag, plotAx=False):
    a = pd.DataFrame({'Frequency(MHz)':freq,'Frequency Response(dB)':mag})
    m = lm.models.LinearModel() 
    
    pars = m.make_params( m = 0, b = 0)
   
    fitDat = a[(a['Frequency(MHz)'] > tx['TransducerBandwidthLinearFitRange'][0]) & (a['Frequency(MHz)'] < tx['TransducerBandwidthLinearFitRange'][1])]
    xFitDat = list(fitDat['Frequency(MHz)'])
    yFitDat = list(fitDat['Frequency Response(dB)'])

    out = m.fit(yFitDat, pars, x=xFitDat)

    if doPlots:
        if plotAx:
           plotAx.plot(xFitDat, m.eval(out.params, x=np.asarray(xFitDat)),'r-', linewidth=2.0)
        else:
           plotAx.plot(freq, mag, '+')
           plt.plot(xFitDat, m.eval(out.params, x=np.asarray(xFitDat)),'r-', linewidth=2.0)
           plt.show()
        
    return out.best_values

def getEODetails(tx, plate):
    dat = pd.DataFrame({'imp':tx['plateSpecific'][plateIDs[plate]]['rawEO'][:,0],'thick':tx['plateSpecific'][plateIDs[plate]]['rawEO'][:,1],'eo':tx['plateSpecific'][plateIDs[plate]]['rawEO'][:,2]})
   # dat = dat[(dat['imp']!=1.63) & (dat['imp']!=1.83) & (dat['imp']!=1.67) &(dat['imp']!=1.81)]
    dat = dat[(dat['imp']==1.75)]
    mn = dat[dat['eo'] == dat[(dat['thick']>0.5)&(dat['thick']<2)].min()['eo']]
    mx = dat[dat['eo'] == dat.max()['eo']]
    
    return {'thicknessAtMin':mn['thick'].values[0], 'ejOffAtMin':mn['eo'].values[0], 'thicknessAtMax': mx['thick'].values[0],'ejOffAtMax':mx['eo'].values[0]}

kDMSO_EO_IMP          = 1.75
kDMSO_EO_THICK_RANGE  = [1.1,3.3]

def getSmoothEODetails(tx, plate):
    global dat, outEO, mnn
    dat = pd.DataFrame({'imp':tx['plateSpecific'][plateIDs[plate]]['rawEO'][:,0],'thick':tx['plateSpecific'][plateIDs[plate]]['rawEO'][:,1],'eo':tx['plateSpecific'][plateIDs[plate]]['rawEO'][:,2]})
   # dat = dat[(dat['imp']!=1.63) & (dat['imp']!=1.83) & (dat['imp']!=1.67) &(dat['imp']!=1.81)]

    dat = dat[(dat['imp']==kDMSO_EO_IMP) & (dat['thick'] >= kDMSO_EO_THICK_RANGE[0]) & (dat['thick'] <= kDMSO_EO_THICK_RANGE[1])]
   
    m = lm.models.PolynomialModel(4) 
    pars = m.make_params( c0 = 0, c1 = 0, c2 = 0, c3 = 0, c4 = 0)
    outEO  = m.fit(dat['eo'], pars, x=dat['thick'])
    
    from scipy.optimize import minimize as mmnn

    minResult =  mmnn(lambda val : outEO.eval(x=val), 2.,      bounds=[[1.4, 2.0]] )
    maxResult =  mmnn(lambda val : -1 * outEO.eval(x=val), 2., bounds=[[2.0, 3.3]] )
    
    return {'thicknessAtMin':minResult.x[0], 'ejOffAtMin':minResult.fun[0], 'thicknessAtMax':maxResult.x[0], 'ejOffAtMax': -1 * maxResult.fun[0], 'polyCoefs':outEO.best_values,'polyRange':kDMSO_EO_THICK_RANGE, 'polyImp':kDMSO_EO_IMP}

def throwIfSmoothEOBad(tx):
    if tx['PolynomialExtremaOf384LDVEO']['thicknessAtMin'] <= kDMSO_EO_THICK_RANGE[0]:
        raise Exception('Something is wrong with ejection offset.  Can''t find '
                        'lower local extremum in 384LDV_DMSO.') 

    if tx['PolynomialExtremaOf384LDVEO']['thicknessAtMax'] >= kDMSO_EO_THICK_RANGE[1]:
        raise Exception('Something is wrong with ejection offset.  Can''t find '
                        'upper local extremum in 384LDV_DMSO.') 

def getInterp(d):
    dims = d.shape[1]-1
    return interpolate.LinearNDInterpolator(d[:,:dims].astype('float64'), d[:,dims].astype('float64'))

def resample(resampledName, plate, coords):
    # 2D Luts of impedence x thickness
    reSFTTE   = getInterp(plate['rawSFTTE'])(coords)
    reT2T     = getInterp(plate['rawT2T'])(coords)
    reEO      = getInterp(plate['rawEO'])(coords)

    # 1D Luts of impedence
    reToneXCF1 = interpolate.interp1d(plate['rawToneX']['CF1'    ][:,0], plate['rawToneX']['CF1'    ][:,1])(coords[:,0])
    reToneXCF3 = interpolate.interp1d(plate['rawToneX']['CF3'    ][:,0], plate['rawToneX']['CF3'    ][:,1])(coords[:,0])
    reToneXRA1 = interpolate.interp1d(plate['rawToneX']['RelAmp1'][:,0], plate['rawToneX']['RelAmp1'][:,1])(coords[:,0])
    reToneXRA3 = interpolate.interp1d(plate['rawToneX']['RelAmp3'][:,0], plate['rawToneX']['RelAmp3'][:,1])(coords[:,0])
    reToneXW1  = interpolate.interp1d(plate['rawToneX']['Width1' ][:,0], plate['rawToneX']['Width1' ][:,1])(coords[:,0])
    reToneXW2  = interpolate.interp1d(plate['rawToneX']['Width2' ][:,0], plate['rawToneX']['Width2' ][:,1])(coords[:,0])
    reToneXW3  = interpolate.interp1d(plate['rawToneX']['Width3' ][:,0], plate['rawToneX']['Width3' ][:,1])(coords[:,0])    

    plate[resampledName] = {}

    p = plate[resampledName] 

    for i, XY in enumerate(coords):
         p[tuple(XY)] = {}
         p[tuple(XY)]['SFTTE'] = reSFTTE[i]
         p[tuple(XY)]['T2T']   = reT2T[i]
         p[tuple(XY)]['EO']    = reEO[i]
         p[tuple(XY)]['CF1']   = reToneXCF1[i]
         p[tuple(XY)]['CF3']   = reToneXCF3[i]
         p[tuple(XY)]['RA1']   = reToneXRA1[i]
         p[tuple(XY)]['RA3']   = reToneXRA3[i]
         p[tuple(XY)]['W1' ]   = reToneXW1[i]
         p[tuple(XY)]['W2' ]   = reToneXW2[i]
         p[tuple(XY)]['W3' ]   = reToneXW3[i]  

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def color_y_axis(ax, color):
    """Color your axes."""
    for t in ax.get_yticklabels():
        t.set_color(color)
    return None

def plotEO(tx):
    fig, q = plt.subplots(1,1)
    
    ax = {2:q}
    
    for plateId in tx['plateSpecific']:
        rawEO = tx['plateSpecific'][plateId]['rawEO'] 

        imps = list(reversed(sorted(list( set(rawEO[:,0])))))
        
        for k, v in plateIDs.items():
            if v == plateId:
                plateName = k
                break
        
        if plateName != '384LDV_DMSO' and plateName != '384LDVS_DMSO':
            continue
    
        for imp in imps:
            keepRows = np.asarray([i for i in rawEO if i[0] == imp])
            ax[plateId].plot(keepRows[:,1], keepRows[:,2], '', label=str(imp), linewidth=0.75)
       
        xvals = np.linspace(tx['PolynomialExtremaOf384LDVEO']['polyRange'][0],tx['PolynomialExtremaOf384LDVEO']['polyRange'][1],100)
        m = lm.models.PolynomialModel(4) 
        pars = m.make_params( **tx['PolynomialExtremaOf384LDVEO']['polyCoefs'] )
        yvals = m.eval(pars, x = xvals)

        ax[plateId].plot(xvals, yvals, 'k--', label=str(tx['PolynomialExtremaOf384LDVEO']['polyImp']) +  ' (poly)')

        ax[plateId].set_ylim([0,np.max(yvals) * 1.2])

        ax[plateId].plot(tx['PolynomialExtremaOf384LDVEO']['thicknessAtMin'],tx['PolynomialExtremaOf384LDVEO']['ejOffAtMin'],'ro')
        ax[plateId].plot(tx['PolynomialExtremaOf384LDVEO']['thicknessAtMax'],tx['PolynomialExtremaOf384LDVEO']['ejOffAtMax'],'ro')

        ax[plateId].set_xlabel('Thickness [mm]')       
   
        ax[plateId].legend(title='Imp. [MRayl]')
        
        fig.set_size_inches(8,5)
        

#####################################################        
##  The folloing is for processing RF Amp data
##  from healthcheck
        
def XMLInfo(data):

    global frame
    
    root = ET.fromstring(data) # Unpack XML
    
    TBWData = next(root.iter('RFHealthCheck'))

    loadType = TBWData.attrib['loadType']
    
    captures=next(TBWData.iter('Captures'))
    
    frame = None
    
    for v in captures:
        tag = v.tag
        
        freq = tag.split('_')[1]
        v = tag.split('_')[2]
        
    return { 'load':loadType, 'frequency': float(freq[:-3]), 'volts': float(v[:-1])}

def unpackXMLRFAmp(data):

    global frame#, iii
    
    root = ET.fromstring(data) # Unpack XML
    
    TBWData = next(root.iter('RFHealthCheck'))
    
    captures=next(TBWData.iter('Captures'))
    
    frame = None
    
    for v in captures:
        samples = []

        tag = v.tag
        
        for vv in v:
           samples.append(float(vv.text))
    
        if frame is None:
            frame = pd.DataFrame({tag[-1:]:samples})
        else:
            frame = pd.concat([frame,pd.DataFrame({tag[-1:]:samples})],axis=1)
    
    return frame.mean(axis=1).max() - frame.mean(axis=1).min()

def generateDataMatrix(inList):
    if inList == {}:
        return None, None, None
    
    fList = sorted(list(inList.keys()))
    vList = sorted(list(inList[fList[0]].keys()))

    data = np.empty([len(fList), len(vList)])

    for idx_f, f in enumerate(fList):
        for idx_a, a in enumerate(vList):
            data[idx_f,len(vList)-idx_a-1] = inList[f][a]
    
    return data, vList, fList

def measurementToNPCs( PCs, eDat, n ):
    v = eDat['mean'] + (sum( [np.real(PCs[i] * eDat['eVecs'][i]) for i in range(n) ])  )
    return v

def squareErrorNPCs(dat, PCs, eDat, n):
    delta =  dat  - (measurementToNPCs( PCs, eDat, n ) ) 
    return np.mean(delta**2)

# Let's get set up for PCA for RFAMp data        
def expressInPC(dat):
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'PCA_3-26-18.pkl'), 'rb') as f:
        RFAmpPCA = pickle.load(f)
        
        PCs = np.asarray([ (dat.flatten() - RFAmpPCA['mean']) @ eVec for eVec in RFAmpPCA['eVecs'] ])
        
        errors = [squareErrorNPCs(dat.flatten(), PCs, RFAmpPCA,  n)**0.5 for n in range(len(PCs)+1)]
        
        return (PCs, errors) 

def getRFAmp(server,db):
    c = getCursor(server=server,db=db)

    data = c.execute("SELECT MeasuredData FROM TransducerBandwidth WHERE Type = 'RFAmp'").fetchall()
    
    outRawTX    = {}
    outRaw50Ohm = {}

    for d in data:    
        i = XMLInfo(d[0])

        out = outRawTX if i['load'] == 'Transducer' else outRaw50Ohm
        
        if i['frequency'] not in out:
           out[i['frequency']] = {}
           
        out[i['frequency']][i['volts']] = unpackXMLRFAmp(d[0])
    
    outRawMatrixTX,    outRawVListTX,    outRawFListTX    = generateDataMatrix(outRawTX)   
    outRawMatrix50Ohm, outRawVList50Ohm, outRawFList50Ohm = generateDataMatrix(outRaw50Ohm)   

    # Sometimes the raw data is sampled more finely.  Down-sample to get on an equal
    # footing with other measurements.
    standardAmp  = np.linspace(0.2,5,25)
    standardFreq = np.linspace(5,14,10)
    
    outTX    = {}
    out50Ohm = {}
    
    for d in data:    
        i = XMLInfo(d[0])

        out = outTX if i['load'] == 'Transducer' else out50Ohm
        
        if np.any(np.isclose(i['frequency'], standardFreq)):
           if i['frequency'] not in out: 
               out[i['frequency']] = {}
           if np.any(np.isclose(i['volts'], standardAmp)):
               out[i['frequency']][i['volts']] = unpackXMLRFAmp(d[0])
    
    outMatrixTX,    outVListTX,    outFListTX    = generateDataMatrix(outTX)   
    outMatrix50Ohm, outVList50Ohm, outFList50Ohm = generateDataMatrix(out50Ohm)              
    
    if type(outMatrixTX) != type(None):
        PCADat, PCAError = expressInPC(outMatrixTX)
    else:
        PCADat, PCAError = (None, None)
    
    return { 'TX'    : { 'raw'      : { 'dat': outRawTX ,   'matrix': outRawMatrixTX ,    'fList': outRawFListTX,    'vList': outRawVListTX },
                         'standard' : { 'dat': outTX ,      'matrix': outMatrixTX ,       'fList': outFListTX,       'vList': outVListTX,  'PCA': PCADat, 'PCAError' : PCAError } },
             '50Ohm' : { 'raw'      : { 'dat': outRaw50Ohm, 'matrix': outRawMatrix50Ohm , 'fList': outRawFList50Ohm, 'vList': outRawVList50Ohm },
                         'standard' : { 'dat': out50Ohm,    'matrix': outMatrix50Ohm ,    'fList': outFList50Ohm,    'vList': outVList50Ohm } } }

def plotPCAError(data):
    plt.plot(range(len(data['PCAError'])), data['PCAError'])
    plt.xlim([0,12])
    plt.xlabel('Number of principal components', fontsize=14)
    plt.ylabel(r'Error [V]: $\sqrt{\left<\sum_{bins}\left(v_{pca} - v_{meas}\right)^2\right>}$', fontsize=12)

def plotAmp(inputData, lab):
    out = inputData['dat']
    fig, ax = plt.subplots(1,1)  
    
    for f, dat in out.items():
        vins  = sorted(list(dat))
        vouts = [dat[v] for v in vins] 
        
        plt.xlabel('input volts')
        plt.ylabel('output volts')
        plt.plot(vins, vouts, label=f)
        plt.legend(title='Frequency [MHz]')
        plt.title(lab)
        
    fig.set_size_inches([9,7])

def plotFreq(inputData, lab):
    out = inputData['dat']
 
    fig, ax = plt.subplots(1,1)  
    
    vins = []
 
    freqs = sorted(list(out))
    
    for f in freqs:
        vins = list(sorted(set(vins + list(out[f]))))

    vins = reversed(vins)

    for v in vins:
        freqouts = []
        vouts = []
    
        for f in freqs:
            if v in out[f]:
                freqouts.append(f)
                vouts.append(out[f][v])
        
        plt.plot(freqouts, vouts, label=v)

    plt.xlabel('frequency [MHz]')
    plt.ylabel('output volts')
    plt.title(lab + ' for input voltages from 0.2 to 5.0.')
    plt.legend(title='Out amp/in amp')
    fig.set_size_inches([9,7])  
    
def PlotRF2D(dat):  
    fig,ax = plt.subplots(1,1)
    plt.imshow(np.flip(np.flip(dat['matrix'], axis=0),axis=1),interpolation = 'none', cmap='viridis')
    plt.yticks(np.arange(len(dat['fList'])),reversed(np.int8(dat['fList'])))
    plt.xticks(np.arange(len(dat['vList'])),dat['vList'])
    bar = plt.colorbar(orientation ='horizontal')
    bar.set_label('coupled input [V]',size=18)
    plt.ylabel(r'input freqeuncy [MHz]', fontsize=18)
    plt.xlabel(r'input amplitude [v]', fontsize=18)

    fig.set_size_inches(9,6)
    
def plotFreqWPCA(inputData):
    out = inputData['dat']
    PCA = inputData['PCA']   

    with open(os.path.join(os.path.dirname(__file__),'PCA_3-26-18.pkl'), 'rb') as f:
            RFAmpPCA = pickle.load(f)

    colors=plt.cm.flag
    #colors=plt.cm.brg
    
    
    fig, ax = plt.subplots(1,1)  
    
    vins = []
 
    freqs = sorted(list(out))
    
    for f in freqs:
        vins = list(sorted(set(vins + list(out[f]))))

    vins = reversed(vins)

    for vi, v in enumerate(vins):
        freqouts = []
        vouts = []
    
        for f in freqs:
            if v in out[f]:
                freqouts.append(f)
                vouts.append(out[f][v])
        
        plt.plot(freqouts, vouts, label=v, c=colors(vi/25))
        
        n = 6
        for i in range(n):
            y = measurementToNPCs(PCA, RFAmpPCA,i).reshape(10,25)
            plt.plot(np.array(freqouts)-0.5+(0.5/n)*(i+1) , y[:,vi],'d', ms=4, c=colors(vi/25))
        
    plt.xlabel('frequency [MHz]')
    plt.ylabel('output volts')
    plt.title('TX input voltages from 0.2 to 5.0.  Up to ' + str(n) + ' orders of principal coponents overlayed.' )
    plt.legend(title='Out amp/in amp')
    fig.set_size_inches([12,9])  

####### End of RF Amp functions ##############################

## Perform the focla sweep analysis
def analyzeFocalSweep(focalSweepPath, AmpDetails=None, makePlots=False, plotSaveDir=None, showPlots=True):
    tx = {}
    tx['focalSweepPath'] = focalSweepPath
    
    
    
    with open(tx['focalSweepPath']) as f:
        reader = csv.reader(f, delimiter=',' )    

        names = {}
        vals = {}
        for row in reader:
    
            if len(row)==3 and not is_number(row[0]):
                for idx, val in enumerate(row):
                    names[idx] = val
                    if val:
                        vals[val] = []
    
            if len(row)==4 and is_number(row[0]):
                for idx, val in enumerate(row):
                    if val:
                       vals[names[idx]].append(float(val))
       
        tx['FocalSweepRaw'] = vals
    
        a = pd.DataFrame(vals)          
        
        m = lm.models.QuadraticModel() 
        pars = m.make_params( a = 0, b = 0, c = 0 )
        outAmp  = m.fit(list(a['Amp (Vpp)']), pars, x=list(a['ToF (us)']))
    
        tx['FocalSweepNewQuadAmpToFFit'] = outAmp.best_values
        v = outAmp.best_values
    
        tx['FocalSweepNewBestAmp'] =  - (v['b']*v['b'])/(4 * v['a']) + v['c']
        tx['FocalSweepNewBestToF'] = -1 * v['b']/(2 * v['a'])
    
        ax = None
    
        if makePlots:
            print('Focal Sweep - the right way - ToF = '+str(tx['FocalSweepNewBestToF']))
            fix, ax = plt.subplots()
            ax.set_ylabel('Amplitude [V]')
            ax.set_xlabel(r'ToF [$u$s]')
            ax.plot(list(a['ToF (us)']), list(a['Amp (Vpp)']), '+')
            ax.plot(list(a['ToF (us)']), m.eval(outAmp.params, x=np.asarray(list(a['ToF (us)']))),'r-', linewidth=2.0)
            if plotSaveDir:
                plt.savefig(os.path.join(plotSaveDir, 'FocalSweep.png'), bbox_inches='tight')    
            plt.show() if showPlots else plt.close()
        
        m = lm.models.QuadraticModel() 
        pars = m.make_params( a = 0, b = 0, c = 0 )
        outAmp  = m.fit(list(a['Amp (Vpp)']), pars, x=list(a['TransducerZ (um)']))
    
        tx['FocalSweepQuadAmpFit'] = outAmp.best_values
        v = outAmp.best_values
    
        tx['FocalSweepBestZ'] = -1 * v['b']/(2 * v['a'])
        tx['FocalSweepBestAmp'] =  - (v['b']*v['b'])/(4 * v['a']) + v['c']

#        if doPlots:
#            print('Focal Sweep:')
#            fix, ax = plt.subplots()
#            ax.set_ylabel('Amplitude [V]')
#            ax.set_xlabel(r'Transducer z-position [$u$m]')
#            ax.plot(list(a['TransducerZ (um)']), list(a['Amp (Vpp)']), '+')
#            ax.plot(list(a['TransducerZ (um)']), m.eval(outAmp.params, x=np.asarray(list(a['TransducerZ (um)']))),'r-', linewidth=2.0)
#            color_y_axis(ax, 'r')
        
        m = lm.models.LinearModel() 
        pars = m.make_params( slope = 0, intercept  =  0 )
        outTOF  = m.fit(list(a['ToF (us)']), pars, x=list(a['TransducerZ (um)']))
    
        tx['FocalSweepLinToFFit'] = outTOF.best_values
    
        tx['FocalSweepBestToF'] = outTOF.best_values['intercept'] + outTOF.best_values['slope'] * tx['FocalSweepBestZ']
    
    
#        if doPlots:
#            ax2 = ax.twinx()
#            ax2.set_ylabel(r'ToF [$u$s]')
#            ax2.plot(list(a['TransducerZ (um)']), list(a['ToF (us)']), '+')
#            color_y_axis(ax2, 'b')
#            ax2.plot(list(a['TransducerZ (um)']), m.eval(outTOF.params, x=np.asarray(list(a['TransducerZ (um)']))),'b-', linewidth=2.0)
#            plt.show()
        
    return tx

## Perform the database analysis
def analyzeDatabase(databaseServer, dbName, AmpDetails=None, Instrument=None, TransducerId=None, makePlots=False, plotSaveDir=None, showPlots=True):

    cursor = getCursor(databaseServer)
    cursor.execute("USE " + dbName)

    global doPlots
    
    doPlots = makePlots

    tx = {}
    
    tx['TransducerBandwidthLinearFitRange']       = [8,14]
    tx['TransducerBandwidthTwinGaussianFitRange'] = [7,17]

    if Instrument:
        tx['Instrument_SN'] = Instrument
    else:
        tx['Instrument_SN'] = cursor.execute("SELECT 'E'+SUBSTRING(ParameterValue, 6, 5) FROM Parameter WHERE GroupName = 'General' AND ParameterName LIKE '%SerialNumber%'").fetchall()[0][0]

    if TransducerId:
        tx['TX_SN'] = TransducerId
    else:
        tx['TX_SN'] = cursor.execute("SELECT SerialNumber FROM Transducer").fetchall()[0][0]
    
    if AmpDetails:
        tx['AmpDetails'] = AmpDetails
    elif tx['Instrument_SN'] in DefaultAmpDetails:
        tx['AmpDetails'] = DefaultAmpDetails[tx['Instrument_SN']]
    else:
        raise Exception('No amplifier details provided and no default value abailable for ' + tx['Instrument_SN'] + '.')   


    # Gather healthckeck RFAmp data if available
    tx['RFAmp'] = getRFAmp(databaseServer,dbName)

    if doPlots:
        if len( tx['RFAmp']['50Ohm']['standard']['dat']):
            plotAmp( tx['RFAmp']['50Ohm']['standard'], r'50$\Omega$')
            if plotSaveDir:
                plt.savefig(os.path.join(plotSaveDir, 'RFAmpVolts50Ohm.png'), bbox_inches='tight')
            plt.show() if showPlots else plt.close()
            plotFreq(tx['RFAmp']['50Ohm']['standard'], r'50$\Omega$')
            if plotSaveDir:
                plt.savefig(os.path.join(plotSaveDir, 'RFAmpHz50Ohm.png'), bbox_inches='tight')
            plt.show() if showPlots else plt.close()
            
        if len(tx['RFAmp']['TX']['standard']['dat']):
            plotAmp( tx['RFAmp']['TX']['standard'], r'Transducer')
            if plotSaveDir:
                plt.savefig(os.path.join(plotSaveDir, 'RFAmpVoltsTX.png'), bbox_inches='tight')
            plt.show() if showPlots else plt.close()
            plotFreq(tx['RFAmp']['TX']['standard'], r'Transducer')
            if plotSaveDir:
                plt.savefig(os.path.join(plotSaveDir, 'RFAmpHzTX.png'), bbox_inches='tight')
            plt.show() if showPlots else plt.close()
            
            PlotRF2D(tx['RFAmp']['TX']['raw'])
            if plotSaveDir:
                plt.savefig(os.path.join(plotSaveDir, 'RFAmp2DTX.png'), bbox_inches='tight')
            plt.show() if showPlots else plt.close()
            
            if type(tx['RFAmp']['TX']['standard']['PCA'])!=type(None):
                plotPCAError(tx['RFAmp']['TX']['standard'])
                if plotSaveDir:
                    plt.savefig(os.path.join(plotSaveDir, 'RFAmpPCAError.png'), bbox_inches='tight')    
                plt.show() if showPlots else plt.close()
            
                plotFreqWPCA(tx['RFAmp']['TX']['standard'])
                if plotSaveDir:
                   plt.savefig(os.path.join(plotSaveDir, 'RFAmpHzTXPCA.png'), bbox_inches='tight')
                plt.show() if showPlots else plt.close()
            
    
    #  Let's establish plate-independant stuff
    plateType     = '384LDVS_DMSO' # We're going to use one BB/TBToFCorrection as a characterization of the transducer.
                                   # Choice of plateType arbitrary, but needs to be the same for each instrument.
    plateTypeAlt  = '384LDV_DMSO'    
    
    tx['thePlate'] = plateType
           
    outPT =  cursor.execute("SELECT * FROM PlateType WHERE PlateUse ='HID' AND PlateTypeName = '" + tx['thePlate'] + "'").fetchall()

    if not outPT:
        tx['thePlate'] = plateTypeAlt

        outPT =  cursor.execute("SELECT * FROM PlateType WHERE PlateUse ='SRC' AND PlateTypeName = '" + tx['thePlate'] + "'").fetchall()

        if not outPT:
                raise Exception(dbName + ' has no ' + plateType + ' and no ' + plateTypeAlt + '. Stopping.')

    print(tx['TX_SN'] + ' (' + dbName + ')' +' has a ' + tx['thePlate'] + '.')
        
    focalDat = cursor.execute("SELECT ToFFocus FROM FocalSweep WHERE Type='REF'").fetchall()
    tx['DBFocus'] = focalDat[0][0]

    ax = [None, None]
    if doPlots:
        print('Transducer Bandwidth:')
        fig, ax = plt.subplots(1,2, sharey=True)
        ax[0].set_xlim([5,18])
        ax[0].set_ylim([8,17])
        ax[0].set_xlabel('Frequency [MHz]')
        ax[0].set_ylabel('TBW Amplitude Ratio')
        ax[0].set_title('Most recent measurement')
        ax[1].set_xlim([5,18])
        ax[1].set_ylim([8,17])
        ax[1].set_xlabel('Frequency [MHz]')
        ax[1].set_title('Mean recent two-weeks')
        plt.tight_layout()
        
    # Get most recent TBW and compute fits
    TBWSingleDat = cursor.execute("SELECT TOP 1 MeasuredData FROM TransducerBandwidth \n\
                                    ORDER BY MeasurementDate DESC").fetchall()[0][0]
          
    tx['TransducerBandwidthSingle'] = {'Frequency(MHz)':[],'Frequency Response(dB)':[]}
    tx['TransducerBandwidthSingle']['Frequency(MHz)'],   tx['TransducerBandwidthSingle']['Frequency Response(dB)'] = unpackXMLTBW(TBWSingleDat, plotAx = ax[0])
    tx['TransducerBandwidthSingleFit']       = doubleGaussFit( tx, tx['TransducerBandwidthSingle']['Frequency(MHz)'],
                                                                   tx['TransducerBandwidthSingle']['Frequency Response(dB)'],  plotAx = ax[0])
    tx['TransducerBandwidthSingleLinearFit'] = linearFit     ( tx, tx['TransducerBandwidthSingle']['Frequency(MHz)'],
                                                                   tx['TransducerBandwidthSingle']['Frequency Response(dB)'],  plotAx = ax[0] )
           
       
    # Get several recent TBWs and compute fits from mean
    
    q = "SELECT MeasuredData\
           FROM TransducerBandwidth a,\
                (SELECT MAX(MeasurementDate) MeasurementDate\
                   FROM TransducerBandwidth\
                  WHERE (Type = 'CAL' OR Type = 'REF')) b\
           WHERE DATEDIFF(week, a.measurementDate,b.measurementDate) < 8\
             AND (a.Type = 'CAL' OR a.Type = 'REF')"
    
    TBWFullDat = np.asarray(cursor.execute(q).fetchall())
    
    tx['TransducerBandwidthMean'] = {'Frequency(MHz)':[],'Frequency Response(dB)':[]}
    tx['TransducerBandwidthMean']['Frequency(MHz)'],   tx['TransducerBandwidthMean']['Frequency Response(dB)'] = unpackMeanXMLTBW(TBWFullDat, plotAx = ax[1])       
    tx['TransducerBandwidthMeanFit'] = doubleGaussFit( tx,  tx['TransducerBandwidthMean']['Frequency(MHz)'],
                                                            tx['TransducerBandwidthMean']['Frequency Response(dB)'], plotAx = ax[1])
    tx['TransducerBandwidthMeanLinearFit'] = linearFit( tx, tx['TransducerBandwidthMean']['Frequency(MHz)'],
                                                            tx['TransducerBandwidthMean']['Frequency Response(dB)'], plotAx = ax[1] )

    if doPlots:
        f = plt.gcf()
        f.set_size_inches(10, 4)
        if  plotSaveDir:
            plt.savefig(os.path.join(plotSaveDir, 'TBW.png'), bbox_inches='tight')    
        plt.show() if showPlots else plt.close()

    ## Get TB/BB ToF ratios and fit for one specific plate type as a characterization of acoustic field.
    tx['rawBBToF'] = np.asarray(cursor.execute("SELECT X, Y FROM LUT \
                        WHERE LUTName = 'BBToFCorrection' AND PlateTypeName = '"+tx['thePlate']+"' ORDER BY X").fetchall())
    tx['rawTBToF'] = np.asarray(cursor.execute("SELECT X, Y FROM LUT \
                        WHERE LUTName = 'TBToFCorrection' AND PlateTypeName = '"+tx['thePlate']+"' ORDER BY X").fetchall())

    
    def fitToFCorrection(dat, label, col):    
        m = lm.models.QuadraticModel() 
        pars = m.make_params( a = 0, b = 0, c = 0 )
        best_fit  = m.fit(list(dat[:,1]), pars, x=list(dat[:,0])).best_values
            
        xmin =  np.min(dat[:,0])
        xmax =  np.max(dat[:,0])
        x = np.linspace(xmin - 0.05 * (xmax-xmin), xmax + 0.05 * (xmax-xmin), 100) 
        pars = m.make_params(**best_fit)
        y = m.eval(params=pars, x=x)
        plt.plot(x, y, c=col)
        plt.plot(*zip(*dat),'.', c=col, label=label)
    
        return best_fit

    tx['BBToFQuadFit'] = fitToFCorrection(tx['rawBBToF'], 'BB', 'blue')
    tx['TBToFQuadFit'] = fitToFCorrection(tx['rawTBToF'], 'TB', 'green')

    plt.legend()
    plt.title(tx['thePlate'] + ' TB/BB ToF Correction (quadratic fits overlaid)')
    plt.xlabel('ToF Ratio')
    plt.ylabel('Peak Amplitude [V]')
    plt.gcf().set_size_inches([7,5]) 
    if doPlots:
        if plotSaveDir:
           plt.savefig(os.path.join(plotSaveDir, 'BBTBToF.png'), bbox_inches='tight')
    
        plt.show() if showPlots else plt.close()


    #########################################
    ## Now we do the plate-specific stuff
    
    if tx['thePlate'] == plateType: # We're on a lemonaded system, select from plateUse='HID' plates.
        out = cursor.execute("SELECT PlateTypeName FROM PlateType WHERE PlateUse = 'HID'").fetchall()
        platesAvailable = [i[0] for i in out if i[0] in list(plateIDs)]
    else: # We're not on a lemonaded system, select from plateUse='SRC' plates.
        out = cursor.execute("SELECT PlateTypeName FROM PlateType WHERE PlateUse = 'SRC'").fetchall()
        platesAvailable = [i[0] for i in out if i[0] in list(plateIDs)]
    
    tx['plateSpecific'] = {}
    
        
    for plate in platesAvailable:
        tx['plateSpecific'][plateIDs[plate]] = {}

        tx['plateSpecific'][plateIDs[plate]]['plateTypeName'] = plate

        ## LUT
        tx['plateSpecific'][plateIDs[plate]]['rawToneX'] = {}
       
        tx['plateSpecific'][plateIDs[plate]]['rawToneX']['CF1']     = np.asarray(cursor.execute("SELECT X, Y FROM LUT \
                            WHERE LUTName = 'ToneX_CF_MHz' AND Description = '1' \
                            AND PlateTypeName = '"+plate+"' ORDER BY X").fetchall())

        tx['plateSpecific'][plateIDs[plate]]['rawToneX']['CF3']     = np.asarray(cursor.execute("SELECT X, Y FROM LUT \
                            WHERE LUTName = 'ToneX_CF_MHz' AND Description = '3' \
                            AND PlateTypeName = '"+plate+"' ORDER BY X").fetchall()) 

        tx['plateSpecific'][plateIDs[plate]]['rawToneX']['RelAmp1'] = np.asarray(cursor.execute("SELECT X, Y FROM LUT \
                            WHERE LUTName = 'ToneX_RelAmp' AND Description = '1' \
                            AND PlateTypeName = '"+plate+"' ORDER BY X").fetchall())

        tx['plateSpecific'][plateIDs[plate]]['rawToneX']['RelAmp3'] = np.asarray(cursor.execute("SELECT X, Y FROM LUT \
                            WHERE LUTName = 'ToneX_RelAmp' AND Description = '3' \
                            AND PlateTypeName = '"+plate+"' ORDER BY X").fetchall())
    
        tx['plateSpecific'][plateIDs[plate]]['rawToneX']['Width1' ] = np.asarray(cursor.execute("SELECT X, Y FROM LUT \
                            WHERE LUTName = 'ToneX_Width_us' AND Description = '1' \
                            AND PlateTypeName = '"+plate+"' ORDER BY X").fetchall())
    
        tx['plateSpecific'][plateIDs[plate]]['rawToneX']['Width2' ] = np.asarray(cursor.execute("SELECT X, Y FROM LUT \
                            WHERE LUTName = 'ToneX_Width_us' AND Description = '2' \
                            AND PlateTypeName = '"+plate+"' ORDER BY X").fetchall())
    
        tx['plateSpecific'][plateIDs[plate]]['rawToneX']['Width3' ] = np.asarray(cursor.execute("SELECT X, Y FROM LUT \
                            WHERE LUTName = 'ToneX_Width_us' AND Description = '3' \
                            AND PlateTypeName = '"+plate+"' ORDER BY X").fetchall())
    
        ## LUT2D
        tx['plateSpecific'][plateIDs[plate]]['rawSFTTE'] = np.asarray(cursor.execute("SELECT X, Y, Z FROM LUT2D \
                            WHERE LUT2DName = 'SolventFluidThickThreshEnergy' AND PlateTypeName = '"+plate+"' ORDER BY X, Y").fetchall()) 

        tx['plateSpecific'][plateIDs[plate]]['rawT2T'] = np.asarray(cursor.execute("SELECT X, Y, Z FROM LUT2D \
                            WHERE LUT2DName = 'Thresh2XferdB' AND PlateTypeName = '"+plate+"' ORDER BY X, Y").fetchall())

        tx['plateSpecific'][plateIDs[plate]]['rawEO'] = np.asarray(cursor.execute("SELECT X, Y, Z FROM LUT2D \
                            WHERE LUT2DName = 'EjectionOffset' AND PlateTypeName = '"+plate+"' ORDER BY X, Y").fetchall())
        
        #  Characterize EO while we're here:
        if 'DMSO' in plate: # possibly not implemented generally enough for some plate types beyond DMSO.
            tx['plateSpecific'][plateIDs[plate]]['EODetails'] = getEODetails(tx, plate) 

       
    ##########################
    ## Compute positions and values of extrema of ejection offset for 384LDV_DMSO as a characterization of acoustic field    

    tx['PolynomialExtremaOf384LDVEO'] = getSmoothEODetails(tx, '384LDV_DMSO')
        
  
    if doPlots:
        print('Ejection Offset:')
        plotEO(tx)
        if plotSaveDir:
            plt.savefig(os.path.join(plotSaveDir, 'EO.png'), bbox_inches='tight')
        plt.show() if showPlots else plt.close()

    throwIfSmoothEOBad(tx)     

    ##########################    
    ## Resample LUTs at standardized positions - use SFTTE here since we'd like to predict it.
    for plateID, plate in tx['plateSpecific'].items():
        if 'DMSO' in plate['plateTypeName']:
            # Fixed thickness of 1.5mm
            where = np.asarray([[imp,1.5] for imp in set([i[0] for i in plate['rawSFTTE']])])
            resample('resampledLUTsAtImpSFTTE_Thick1.5mm', plate, where)           
                
    return tx

def analyzeInstrument(databaseServer, dbName, focalSweepPath, AmpDetails='feature_deprecated', Instrument=None, TransducerId=None, makePlots=False, showPlots=True, plotSaveDir=None):

    txFocus    = analyzeFocalSweep(focalSweepPath, makePlots=makePlots, showPlots=showPlots)
    txDatabase = analyzeDatabase(databaseServer, dbName, AmpDetails=AmpDetails, Instrument=Instrument, TransducerId=TransducerId, makePlots=makePlots, showPlots=showPlots, plotSaveDir=plotSaveDir)
    
    return {**txFocus, **txDatabase}

#analyzeInstrument('Lighthouse',
#                'TX1046600_MC3436143_E1419_7a0c6759a8ba28c7c6f22da344e79834',
#                 r'\\seg\transducer\Transducers\TX1046600_MC3436143\Calibration_E1419\Data\384LDVS_DMSO\Impedance\TransducerFocalSweep\FocalSweep_2017-03-15_10-47-44.csv',
#                 'E1419',
#                 TransducerId='1046600',
#                 makePlots=True,
#                 plotSaveDir = r'c:\Users\jrubin\Desktop\PlotOutput'
#                )

#analyzeDatabase('localhost', 'A_525_18018', makePlots=True, plotSaveDir = r'c:\Users\jrubin', AmpDetails='Peanut')

#analyzeDatabase('lighthouse', 'a_1092498', makePlots=True, plotSaveDir = r'c:\Users\jrubin')

#analyzeDatabase('localhost', 'a_1085686', makePlots=True, plotSaveDir = r'c:\Users\jrubin')
#analyzeDatabase('lighthouse', 'a_1092498', makePlots=True)