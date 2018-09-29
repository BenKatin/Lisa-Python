# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 14:20:42 2016

@author: ljungherr
"""
#fl = getListOfPlateSurveyFiles()
#       load and run Classification.py before this file.

#calculate profile for BB Vpp by averaging Col H & I
def profile(sdata):
    
     li = []; pctDeltaList = []
     for col in range (1,25):
         Hwell = 'H' + str(col)
         Iwell = 'I' + str(col)

         Hdata = findRowByWellName(Hwell, sdata)
         Idata = findRowByWellName(Iwell, sdata)
         
         H_Vpp = getBBValue (Hdata)
         I_Vpp = getBBValue (Idata)
#   print (H_Vpp, I_Vpp)   Test because not all platesurvey files contain all wells
         if H_Vpp and I_Vpp:
             avgVpp = round((H_Vpp + I_Vpp)/2,4)
             pctDelta = abs((H_Vpp - I_Vpp)/avgVpp); pctDeltaList.append (pctDelta)
             li.append(avgVpp)
         if H_Vpp and not I_Vpp:
              avgVpp = H_Vpp
              li.append(avgVpp)
#     maxPctDelta = max(pctDeltaList)  #;   print ("%.4f"%maxPctDelta, f)
     return li       #, maxPctDelta 
     
def profile_TBV(sdata):
    
     li = []
     for col in range (1,25):
         Hwell = 'H' + str(col)
         Iwell = 'I' + str(col)

         Hdata = findRowByWellName(Hwell, sdata)
         Idata = findRowByWellName(Iwell, sdata)
         
         H_Vpp = getTBValue (Hdata)
         I_Vpp = getTBValue (Idata)
#   print (H_Vpp, I_Vpp)   Test because not all platesurvey files contain all wells
         if H_Vpp and I_Vpp:
             avgVpp = round((H_Vpp + I_Vpp)/2,4)
             li.append(avgVpp)
     return li
     
def profile_rows(sdata,rows):
     li = []
     for col in range (0,12):
         li.append(0)
         for row in range (0, len(rows)):
             wellname = rows[row] + str(col+1)
             welldata = findRowByWellName(wellname, sdata)
             if welldata:
                 value = getBBValue(welldata)
                 li[col] += value
         li[col] = round (li[col]/len(rows),3)
     return li
     

def profile_exclude_outliers(sdata,rows):
     li = []
     for col in range (0,12):
         li.append ([])
         for row in range (0, len(rows)):
             wellname = rows[row] + str(col+1)
             welldata = findRowByWellName(wellname, sdata)
             if welldata:
                 value = getBBValue(welldata)
                 li[col].append (value)
         wellMean = numpy.mean(li[col])
         fivesig = 5* numpy.std(li[col])
         if fivesig > wellMean:
             print (wellMean, f)
             li[col].remove(min(li[col]))
         for v in li[col]:             
                 oneError = abs((v - wellMean)/wellMean)
                 if oneError > (0.10):
#                     print (col, v)
                     li[col].remove(v)
         li[col] = numpy.mean(li[col])
#         li[col] = round (li[col]/len(rows),3)
     return li
     
""" anyprofile arguements are (filename, surveydata dictionary, 
    list of rows to average, and profile type ('BBV', 'Thk' or 'ToF')
   'BBV' gives BB Vpp. ToF gives BB Tof. Thk gives menbrane thickness.  
    Rows are string; capital letters; such as ['H','I']   """
    
def anyprofile(f, sdata, rows, Ptype):
     li = []
     for col in range (0,12):
         li.append(0)
         for row in range (0, len(rows)):
             wellname = rows[row] + str(col+1)
             welldata = findRowByWellName(wellname, sdata)
             if Ptype == 'BBV':
                 value = getBBValue(welldata)
             elif Ptype == 'Thk':
                 value = getMembraneThickness(welldata)
             elif Ptype == 'ToF':
                 value = getBBToF(welldata)
             elif Ptype == 'TBV':
                 value = getTBValue(welldata)
             else:
                 print ('profile type must be \'BBV\' or \'TBV\' or \'Thk\' or \'ToF\'  ')                 
                 return None
             if not value:
#                 print('missing data for ', Ptype, ' in file ', f)
                 return []
             li[col] += value
         li[col] = round (li[col]/len(rows),3)
     return li
            
#calculate profile for membrane thickness by averaging Col H & I
def profile_Thk_12(sdata):
     li = []
     for col in range (1,13):
         Hwell = 'H' + str(col)
         Iwell = 'I' + str(col)

         Hdata = findRowByWellName(Hwell, sdata)
         Idata = findRowByWellName(Iwell, sdata)
         
         H_val = getMembraneThickness (Hdata)
         I_val = getMembraneThickness (Idata)
 #   print (H_Vpp, I_Vpp)  Test because not all platesurvey files contain all wells
         avgval = 0
         if H_val and I_val:
             avgval = round((H_val + I_val)/2,3)
         elif H_val:
             avgval = H_val
         elif I_val:
             avgval = I_val
         li.append(avgval)
     return li
     
def profile_Thk(sdata):
     li = []
     for col in range (1,25):
         Hwell = 'H' + str(col)
         Iwell = 'I' + str(col)

         Hdata = findRowByWellName(Hwell, sdata)
         Idata = findRowByWellName(Iwell, sdata)
         
         H_val = getMembraneThickness (Hdata)
         I_val = getMembraneThickness (Idata)
 #   print (H_Vpp, I_Vpp)  Test because not all platesurvey files contain all wells
         avgval = 0
         if H_val and I_val:
             avgval = round((H_val + I_val)/2,3)
         elif H_val:
             avgval = H_val
         elif I_val:
             avgval = I_val
         li.append(avgval)
     return li

#calculate profile for BB ToF by averaging Col H & I
def profile_ToF_12(sdata):
     li = []
     for col in range (1,13):
         Hwell = 'H' + str(col)
         Iwell = 'I' + str(col)

         Hdata = findRowByWellName(Hwell, sdata)
         Idata = findRowByWellName(Iwell, sdata)
         
         H_val = getBBToF (Hdata)
         I_val = getBBToF (Idata)
 #   print (H_Vpp, I_Vpp)  Test because not all platesurvey files contain all wells
         if H_val and I_val:
             avgval = round((H_val + I_val)/2,3)
             li.append(avgval)
         if H_val and not I_val:
             li.append(H_val)
     return li
     
def profile_ToF(sdata):
     li = []
     for col in range (1,25):
         Hwell = 'H' + str(col)
         Iwell = 'I' + str(col)

         Hdata = findRowByWellName(Hwell, sdata)
         Idata = findRowByWellName(Iwell, sdata)
         
         H_val = getBBToF (Hdata)
         I_val = getBBToF (Idata)
         if H_val and I_val:
             avgval = round((H_val + I_val)/2,3)
             li.append(avgval)
     return li   

def profile_imped(sdata):
    li = []
    for col in range (1,25):
         Hwell = 'H' + str(col)
         Iwell = 'I' + str(col)

         Hdata = findRowByWellName(Hwell, sdata)
         Idata = findRowByWellName(Iwell, sdata)
         
         H_num = getTBValue (Hdata)
         I_num = getTBValue (Idata)
         H_denom = getBBValue(Hdata)
         I_denom = getBBValue(Idata)
         if (H_num and I_num and H_denom and I_denom):           
             H_ratio = H_num/H_denom
             I_ratio = I_num/I_denom
             avgval = round((H_ratio + I_ratio)/2,3)
             li.append(avgval)
    return li

#calculate profile for BB Vpp corrected for ToF; average Col H & I     
def profile_corrBBVpp (sdata, fitFunction, xLimits):

    li = []
    scaleFactor = fitFunction(xLimits[1])

    for col in range (1,25):
        Hwell = 'H' + str(col)
        Iwell = 'I' + str(col)
        
        Hdata = findRowByWellName(Hwell, sdata)
        Idata = findRowByWellName(Iwell, sdata)
        
        if Hdata and Idata:        
        
            H_BBToF = (getBBToF (Hdata))
            I_BBToF = (getBBToF (Hdata))
               
            HFactor = fitFunction(H_BBToF)
            IFactor = fitFunction(I_BBToF)
        
            Hraw = getBBValue (Hdata)
            Iraw = getBBValue (Idata)
        
            Hcorr = Hraw * scaleFactor/HFactor
            Icorr = Iraw * scaleFactor/IFactor
#       print (Hwell, Hraw, H_BBToF, scaleFactor, HFactor, Hcorr)
            avg_corr = round((Hcorr + Icorr)/2,4)
            li.append(avg_corr)
    return li
    
    