# -*- coding: utf-8 -*-
"""
Created on Thu Jan 25 17:18:43 2018

@author: ljungherr
"""

def getResSig(well):

    if well == 'A1':  
        sigCoeff = [0.355657407, 	-0.093024597,	-1.20429982, 	2.331422154]
    if well == 'A2':         
        sigCoeff = [0.714425024,	-0.801134724,	-0.727611252,	2.236405249]             
    if well == 'A3':         
        sigCoeff = [0.816684375,	-1.019986518,	-0.524085623,	2.159416875]
    if well == 'B1':  
        sigCoeff = [0.364676671,	-0.148459757,	-1.149318968,	2.319150281]
    if well == 'B2':         
        sigCoeff = [-0.092116654,	0.744128234	,     -1.641415809,	2.38270494]             
    if well == 'B3':         
        sigCoeff = [0.455136988,	-0.402959687,	-0.834682898,	2.18960012]
  
    sig = np.poly1d(sigCoeff)
    return (sig)
      
#    FluidImped  = numpy.polyval(sigCoeff, TBR)
#    return (sigCoeff, FluidImped)
    

def  M2Gly(Imped): 
    
    M2GlyCoeff = [18.951,	24.889,	-78.018]
    
    M2Gly = np.poly1d (M2GlyCoeff)
    
    GlyConc = numpy.polyval(M2Gly, Imped)
    
    if GlyConc < 0:
        GlyConc = 0
    
    return (GlyConc)
    
    
    xpoints = np.linspace (0.30, 0.9 ,50)
    plt.ylim (-0.05,40) ; plt.xlim (0.3, 0.9)
    for well in ['A1', 'A2', 'A3', 'B1', 'B2', 'B3']:
        sigC = getResCoeff(well) 
        sig = np.poly1d(sigC)
        plt.plot(xpoints, M2Gly(sig(xpoints)), color = col)
    