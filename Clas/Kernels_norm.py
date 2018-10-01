# -*- coding: utf-8 -*-
"""
Created on Mon Sep 12 15:03:21 2016

@author: ljungherr
"""
from Clas import Classification as clas
from Clas import Kernels as kern
from Clas import PlateProfile as plate
import numpy as np

#to determine a kernel by averaging profile lists:
#Input list of files (flist) and type of profile ('BBV' or 'Thk')
def findKernelN(flist, Ptype):
    AvgList = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    numfiles = 0
    if not (Ptype == 'BBV' or Ptype == 'Thk' or Ptype == 'BBV_Comp'):
#        print ('Profile type not recognized.  Type is \'BBV\' or \'Thk' or \'BBV_Comp')
        return None
    for f in flist:
        if len(f) < 215:
            sdata = clas.ReadEchoPlateSurveyLisa(f,checkfilename=False)
            if Ptype == 'BBV':
                lis = plate.profile(sdata)
            elif Ptype == 'Thk':
                lis = plate.profile_Thk(sdata)
            elif Ptype == 'BBV_Comp':
                lis = plate.profile_corrBBVpp (sdata, PPL_fit, PPL_xlimits)
            if (len(lis) == 24):
                numfiles += 1
                for l in range (0,len(lis)):
                    AvgList[l]+=lis[l]
                    
# divide by length of List:
    for l in range (0,len(AvgList)):
        AvgList[l] = AvgList[l]/numfiles
#    return (AvgList) 
        
#normalize list to mean = 1:
    listAve = np.mean(AvgList)
    for l in range (0,len(AvgList)):
        AvgList[l] = AvgList[l]/listAve
        AvgList[l] = (round(AvgList[l],4))
    return (AvgList) 
	
def findKernelN (flist, Ptype):
	li = kern.findKernel(flist, Ptype)
	
	return normList(li)

 
    
def normList(lis):
    AvgList = []
    listAve = np.mean(lis)
    for i in range (0,len(lis)):
        AvgList.append (lis[i]/listAve)
        AvgList[i] = (round(AvgList[i],4))
    return AvgList


if __name__ == "__main__":
    #Profile BBV for PPL
    PPL_BBV = [2.2940, 2.2473, 2.2167, 2.1791, 2.1488, 2.1224, 2.0863, 2.0675, 2.0589, 2.0480, 2.0471, 2.0682,
         2.0432, 2.0386, 2.0433, 2.0457, 2.0471, 2.0675, 2.0932, 2.1122, 2.1263, 2.1557, 2.1799, 2.2161]
    #Profile Thk for PPL
    PPL_Thk = [0.6098, 0.6242, 0.6293, 0.6316, 0.6331, 0.6345, 0.6359, 0.6366, 0.6379, 0.6380, 0.6370, 0.6370,
          0.6342, 0.6364, 0.6368, 0.6370, 0.6360, 0.6348, 0.6337, 0.6322, 0.6308, 0.6282, 0.6229, 0.6104]

    #Profile BBV for PPG
    PPG_BBV = [2.4918, 2.4278, 2.4384, 2.3434, 2.2418, 2.3278, 2.3027, 2.2230, 2.3199, 2.4322, 2.4107, 2.4309,
               2.4323, 2.3886, 2.4107, 2.3152, 2.2105, 2.2901, 2.2776, 2.1901, 2.2481, 2.3479, 2.3231, 2.3496]

    #Profile Thk for PPG
    PPG_Thk = [0.5986, 0.5986, 0.6018, 0.5994, 0.5930, 0.5858, 0.5869, 0.5951, 0.6023, 0.6012, 0.6032, 0.6030,
    0.6030, 0.6042, 0.6023, 0.6046, 0.5977, 0.5902, 0.5878, 0.5948, 0.6012, 0.6032, 0.5996, 0.5979]

    #E525 Profile BBV for PPL
    PPL_525BBV = [2.5859, 2.5156, 2.4844, 2.4531, 2.4297, 2.4219, 2.3984, 2.3828, 2.3672, 2.3516, 2.3516, 2.3672,
                  2.4063, 2.3516, 2.3516, 2.3594, 2.3750, 2.3906, 2.4063, 2.4141, 2.4219, 2.4375, 2.4688, 2.5625]

    #E525 Profile Thk for PPL
    PPL_525Thk = [0.6040, 0.6150, 0.6180, 0.6190, 0.6190, 0.6190, 0.6190, 0.6190, 0.6190, 0.6200, 0.6190, 0.6210,
                  0.6180, 0.6180, 0.6180, 0.6180, 0.6180, 0.6170, 0.6170, 0.6170, 0.6180, 0.6170, 0.6140, 0.6040 ]

    #E525 Profile BBV for PPG
    PPG_525BBV = [2.6563, 2.5391, 2.5000, 2.4688, 2.4922, 2.6250, 2.6406, 2.4766, 2.4375, 2.4922, 2.5313, 2.6094,
                   2.6484, 2.5313, 2.4922, 2.4375, 2.4688, 2.5938, 2.6406, 2.4844, 2.4688, 2.4844, 2.5234, 2.6484]

    #E525 Profile Thk for PPG
    PPG_525_Thk = [0.6160, 0.6170, 0.6140, 0.6100, 0.6040, 0.5950, 0.5940, 0.6000, 0.6030, 0.6130, 0.6120, 0.6140,
                   0.6110, 0.6120, 0.6160, 0.6100, 0.6050, 0.5990, 0.5990, 0.6080, 0.6100, 0.6170, 0.6200, 0.6150]
    PPL_BBV_Comp = [2.4094, 2.4125, 2.4413, 2.4207, 2.4077, 2.3859, 2.3631, 2.35030, 2.3318, 2.323, 2.3265, 2.3539,
                    2.3486, 2.3206, 2.3308, 2.3391, 2.3493, 2.3649, 2.3823, 2.3943, 2.4069, 2.4106, 2.4038, 2.4026]

    Kernel_Access = [2.1863, 2.1663, 2.1926, 2.2029, 2.215, 2.2071, 2.2002, 2.1976,
                     2.1945, 2.1891, 2.1899, 2.2204, 2.215, 2.1817, 2.1899, 2.1955, 2.2077, 2.2169,
                     2.2308, 2.2367, 2.2374, 2.2357, 2.2228, 2.2092]


    newK =  [2.952, 2.8794, 2.8723, 2.8529, 2.8446, 2.8168, 2.7961, 2.7855, 2.7784, 2.7697, 2.7692, 2.8061, 2.7994,
             2.7586, 2.768, 2.7761, 2.7951, 2.8132, 2.8401, 2.862, 2.8836, 2.9092, 2.9295, 2.9434]

    PPL_BBV_12 = PPL_BBV[0:12]
    PPG_BBV_12 = PPG_BBV[0:12]
    PPG_Thk_12 = PPG_Thk[0:12]
    PPL_525BBV_12 = PPL_525BBV[0:12]
    PPG_525BBV_12 = PPG_525BBV[0:12]

    PPL_Thk_12 = PPL_Thk[0:12]

    #plt.plot(newK)
    #plt.plot(Kernel_Access)

