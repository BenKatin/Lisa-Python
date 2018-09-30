# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 13:39:11 2016
Modified Mon 31 Jan 2017 by Stan Rothwell - Added 'Proto2' as option in self.plateLot
@author: avandenbroucke
"""
import pandas
import os

class BarCodes():
    def __init__(self):
       self.barcodelength = 15
       self.asciioffset = 48
       self.monthMap = {
        'JAN' : '1',
        'FEB' : '2',
        'MAR' : '3',
        'APR' : '4',
        'MAY' : '5',
        'JUN' : '6',
        'JUL' : '7',
        'AUG' : '8',
        'SEP' : '9',
        'OCT' : 'A',
        'NOV' : 'B',
        'DEC' : 'C'}
       
       self.plateMap = {
        'Loc' : 0,
        'Length' : 2,
        'Codes' : {}
          }
       self.plateMap['Codes'] = self.__readMapFromCSV('./plateMap.csv', fieldlength=self.plateMap['Length'] ) 
       
       self.fillStyle = {
         'Loc' : 2,
         'Length' : 1,
         'Codes' : {}  
         }
       self.fillStyle['Codes'] = self.__readMapFromCSV('./fillStyle.csv', fieldlength = self.fillStyle['Length'])
       
       self.fluidType = {
         'Loc' : 3,
         'Length' : 1,
         'Codes' : {}
           }
       self.fluidType['Codes'] = self.__readMapFromCSV('./fluidType.csv',fieldlength =self.fluidType['Length'])
       
       self.fluidConc = {
          'Loc' : 4,
          'Length' : 1,
          'Codes': {}
          }
       self.fluidConc['Codes'] = self.__readMapFromCSV('./fluidConc.csv',fieldlength = self.fluidConc['Length'])
       
       self.fillVol = {
          'Loc' : 5,
          'Length' : 1,
          'Codes': {}
          }
       self.fillVol['Codes'] = self.__readMapFromCSV('./fillVol.csv', fieldlength = self.fillVol['Length'])
          
       self.mapVersion = {
          'Loc' : 6,
          'Length' : 1,
          'Codes': {}
          }
       self.mapVersion['Codes'] = self.__readMapFromCSV('./mapVersion.csv', fieldlength = self.mapVersion['Length'])       
       
       self.cavity = {
       'Loc' : 7,
       'Length' : 1,
       'Codes' : {}
             }
       self.cavity['Codes'] = self.__readMapFromCSV('./cavity.csv', fieldlength= self.cavity['Length'])
       
       self.LUTDate = {
       'Loc' : 9,
       'Length' : 2
       }
       
       self.plateLot = {
       'Loc' : 8,
       'Length' : 1,
       'Codes' :{}
       }
       self.plateLot['Codes'] = self.__readMapFromCSV('./plateLot.csv', fieldlength=self.plateLot['Length'])
       
       self.MFGDate = {
       'Loc' : 11,
       'Length' : 3
       }
       
       self.SN = {
       'Loc' : 14,
       'Length' : 1}
       
       self.Loc = {
       'Loc' : 15,
       'Length' :1 ,
       'Codes' : {}
       }
       self.Loc['Codes'] = self.__readMapFromCSV('./Loc.csv', fieldlength=self.Loc['Length'])
          
    def __readMapFromCSV(self,variable_file, fieldlength=1):
        ''' Helper function that reads the barcode maps from csv into dict 
        Note that imports happen from the folder Barcodes relative to the path of the module '''
        with open(os.path.dirname(__file__) + './BarCodes' + variable_file, 'r') as f:
            thisdict = {}
            for line in f:
                vals = line.split('\n')[0].split(',')
                thisdict[vals[0]] = self.__cropOrExpand(vals[1],fieldlength=fieldlength)
        return thisdict
    
    def __cropOrExpand(self,val, fieldlength=1):
        ''' Helper function that either crops or pads a certain value to make sure the string 'val' is exactly of length 'fieldlength'.
            This method is needed as the barcode is a fixed field map, e.g. exactly 2 characters describe the plateMap'''
        if len(val) < fieldlength:
             value = ''
             for i in range(0, fieldlength):
                value += '0'
             vallist = list(value) 
             print(' value: ', value, 'vallist: ', vallist, 'len(val): ', len(val), 'fieldlentgth = ', fieldlength)  
             vallist[fieldlength-len(val):fieldlength] = val
             value = ''.join(vallist)
        elif len(val) > fieldlength:
             value = val[len(val)-fieldlength::]
        else:
             value = val
         
        return value
    
    def __writeDictToCSV(filename, d):
        ''' Helper function that writes a dict to files, will order on the values '''
        fout = filename
        fo = open(fout, "w")

        for key, value in sorted(d.items(), key=lambda item: (item[1], item[0])):
            fo.write(str(key) + ','+ str(value) + '\n')

        fo.close()
        return
    
    def encodeNumber(self, number):
        return chr(self.asciioffset+int(number))
        
    def decodeNumber(self, code):
        return ord(code)-self.asciioffset
   
    def yearToCode(self,year):
        y = int(year)%100
        return self.encodeNumber(y)
    
    def decodeYear(self, code):
        return self.decodeNumber(code)
    
    def dayToCode(self,day):
        return chr(self.asciioffset+day)    
    
    def decodeDay(self, code):
        return ord(code)-self.asciioffset

    def monthToCode(self, month):
        return self.monthMap[month]
        
    def decodeMonth(self, code):
        invMonthMap = dict((v,k) for k, v in self.monthMap.items())
        if code in invMonthMap:
            return invMonthMap[code]
        else:
            return '-'    
        
    def encodePlateType(self,platetype='384PP_DMSO2'):
        return self.genericDecode(platetype,self.plateMap['Codes'], self.plateMap['Length'])
    
    def encodeFillStyle(self,style='SIG'):
        return self.genericDecode(style,self.fillStyle['Codes'], self.fillStyle['Length'])
        
    def encodeFluidType(self, ftype='DMSO'):
        return self.genericDecode(ftype, self.fluidType['Codes'], self.fluidType['Length'])        
        
    def encodeFluidConc(self, conc='70'):
        return self.genericDecode(conc, self.fluidConc['Codes'], self.fluidConc['Length'])
        
    def encodeFillVol(self, vol='40'):
        return self.genericDecode(vol, self.fillVol['Codes'], self.fillVol['Length'])        
        
    def encodeMapVersion(self, version='0'):
        return self.genericDecode(version, self.mapVersion['Codes'], self.mapVersion['Length'])    
        
    def encodeCavity(self, cavity='1'):
        return self.genericDecode(cavity, self.cavity['Codes'], self.cavity['Length'])  
        
    def encodePlateLot(self, lot='0'):
        return self.genericDecode(lot, self.plateLot['Codes'], self.plateLot['Length'])
        
    def encodeSN(self, SN='1'):
        return self.encodeNumber(int(SN)%150)
    
    def encodeLocation(self, lot='0'):
        return self.genericDecode(lot, self.Loc['Codes'], self.Loc['Length']) 
        
    def decodeLocation(self, barcode):
        code, invmap = self.invCode(barcode, self.Loc)
        return self.genericDecode(code, invmap)
    
    def decodeSN(self, barcode):
        c = barcode[self.SN['Loc']]
        return self.decodeNumber(c)
        
    def encodeMFGDate(self, year='16', month='1', day='1'):
        cday = self.encodeNumber(day)
        cmonth = self.encodeNumber(month)
        cyear = self.yearToCode(year)
        return cyear+cmonth+cday          
        
    def encodeLUTDate(self, month='JAN', year='16'):
        cmonth = self.monthToCode(month)
        cyear = self.yearToCode(year)        
        return cmonth+cyear
        
    def decodeLUTDate(self, barcode):
        cmonth = barcode[self.LUTDate['Loc']]
        cyear = barcode[self.LUTDate['Loc'] + 1]
        month = self.decodeMonth(cmonth)
        year = "{0:0>2}".format(self.decodeYear(cyear))
        return month + year
 
    def decodeMFGDate(self, barcode):
        cyear = barcode[self.MFGDate['Loc']]
        cmonth = barcode[self.MFGDate['Loc']+1]
        cday = barcode[self.MFGDate['Loc']+2]
        year = "{0:0>2}".format(self.decodeYear(cyear))
        month = "{0:0>2}".format(self.decodeNumber(cmonth))
        day = "{0:0>2}".format(self.decodeNumber(cday))
        return year + month +day
    
    def decodePlateLot(self, barcode):
        code, invmap = self.invCode(barcode, self.plateLot)
        return self.genericDecode(code,invmap)
        
    def decodeCavity(self, barcode):
        code, invmap  = self.invCode(barcode, self.cavity)
        return self.genericDecode(code, invmap)
        
    def decodeVersion(self, barcode):
        code, invmap = self.invCode(barcode, self.mapVersion)
        return self.genericDecode(code, invmap)
        
    def decodeFluidConc(self, barcode):
        code, invmap = self.invCode(barcode, self.fluidConc)
        return self.genericDecode(code, invmap)
        
    def decodeFillVol(self, barcode):
        code, invmap = self.invCode(barcode, self.fillVol)
        return self.genericDecode(code, invmap)        
        
    def decodeFluidType(self, barcode):
        code, invmap = self.invCode(barcode,self.fluidType)
        return self.genericDecode(code, invmap)
        
    def decodeFillStyle(self, barcode):
        code, invmap = self.invCode(barcode, self.fillStyle)
        fillstyle = self.genericDecode(code,invmap)
        return fillstyle
        
    def decodePlateType(self, barcode):
        platetypecode, invMap = self.invCode(barcode, self.plateMap)
        platetype = self.genericDecode(platetypecode,invMap)
        return platetype      
   
    def invCode(self, barcode, prop):
        mmap = prop['Codes']
        loc = prop['Loc']
        length = prop['Length']
        code = barcode[loc:(loc+length)]
        invMap = dict((v,k) for k, v in mmap.items())
        return code, invMap
    
    def genericDecode(self,code,mmap,length=None): 
        c = '-'
        if ( self.validate(code,mmap)):
            c = mmap[code]
        else: 
            print(' WARNING: code ', code, ' not defined in map ' , mmap)
        if (length):
           if len(c) != length:
               for i in range(len(c),length):
                   c.append('-')
        return c
        
        
    def validate(self, key,dictionary):
        if key not in dictionary :
            return False
        else:
            return True
    
    def genBarCode(self, platetype='384PP_DMSO2', style='FT', ftype='DMSO', conc='-', vol= '-', v='0', c='1', lot='0', LUTDATE='SEP16' ,MFGDATE='161014', SN='1', LOC='B'):
         cplatetype = self.encodePlateType(platetype)
         cstyle = self.encodeFillStyle(style)
         cftype = self.encodeFluidType(ftype)
         cconc = self.encodeFluidConc(conc)
         cvols = self.encodeFillVol(vol)
         cvn = self.encodeMapVersion(v)
         cc  = self.encodeCavity(c)
         cl = self.encodePlateLot(lot)
         cLUTDATE = self.encodeLUTDate(LUTDATE[0:3],LUTDATE[3:5])
         cMFGDATE = self.encodeMFGDate(MFGDATE[0:2],MFGDATE[2:4],MFGDATE[4:6])
         cSN = self.encodeSN(SN)
         cLOC = self.encodeLocation(LOC)
         return cplatetype + cstyle + cftype + cconc + cvols + cvn +cc + cl + cLUTDATE + cMFGDATE + cSN + cLOC

    def genGenericBarCode(self, mapdict):
        cplatetype = self.encodePlateType(mapdict['PlateType'])
        cstyle = self.encodeFillStyle(mapdict['Style'])
        cftype = self.encodeFluidType(mapdict['Fluid'])
        cconc = self.encodeFluidConc(mapdict['Conc'])
        cvols = self.encodeFillVol(mapdict['Vol'])
        cvn  = self.encodeMapVersion(mapdict['Version'] )
        return cplatetype + cstyle + cftype + cconc + cvols + cvn + '#########'
        
    def genRunSpecificBarCode(self, c='1', lot='0', LUTDATE='SEP16' ,MFGDATE='161014', SN='1', LOC='T'):
         cc  = self.encodeCavity(c)
         cl = self.encodePlateLot(lot)
         cLUTDATE = self.encodeLUTDate(LUTDATE[0:3],LUTDATE[3:5])
         cMFGDATE = self.encodeMFGDate(MFGDATE[0:2],MFGDATE[2:4],MFGDATE[4:6])
         cSN = self.encodeSN(SN)
         cLOC = self.encodeLocation(LOC)
         return cc + cl + cLUTDATE + cMFGDATE + cSN + cLOC
         
    def decodeBarCode(self,barcode, verbose=False):
        platetype = self.decodePlateType(barcode)
        style = self.decodeFillStyle(barcode)
        ftype = self.decodeFluidType(barcode)
        fconc = self.decodeFluidConc(barcode)
        fvol = self.decodeFillVol(barcode)
        fvn = self.decodeVersion(barcode)
        fcav = self.decodeCavity(barcode)
        flot = self.decodePlateLot(barcode)
        LUTDate = self.decodeLUTDate(barcode)
        MFGDate = self.decodeMFGDate(barcode)
        SN = self.decodeSN(barcode)
        LOC = self.decodeLocation(barcode)
        if (verbose):
            print( platetype, ' ', style, ' ' , fconc , '% ', ftype, ' Vol:', fvol, ' V', fvn, ' C', fcav)
            print( 'lot: ', flot, ' LUT: ', LUTDate, ' mfgdate: ' , MFGDate, '#', SN)
        gentype = {}
        gentype['PlateType'] = platetype
        gentype['FillStyle'] = style
        gentype['FluidType'] = ftype
        gentype['Concentration'] = fconc
        gentype['Volume'] = fvol
        gentype['Version'] = fvn   
        gentype['Cavity'] = fcav
        gentype['PlateLot'] = flot
        gentype['LUTDate'] = LUTDate
        gentype['MFGDate'] = MFGDate
        gentype['SN'] = SN
        gentype['LOC'] = LOC
      #  return platetype, style, ftype, fconc, fvn, fcav, flot, LUTDate, MFGDate, SN,  LOC
        return gentype 

        
    def decodeBarCodeType(self,barcode, verbose=False):
        platetype = self.decodePlateType(barcode)
        style = self.decodeFillStyle(barcode)
        ftype = self.decodeFluidType(barcode)
        fconc = self.decodeFluidConc(barcode)
        fvol = self.decodeFillVol(barcode)
        fvn = self.decodeVersion(barcode)
        if (verbose):
            print( platetype, ' ', style, ' ' , fconc , '% ', ftype, ' Vol:', fvol, ' V', fvn)
        gentype = {}
        gentype['PlateType'] = platetype
        gentype['FillStyle'] = style
        gentype['FluidType'] = ftype
        gentype['Concentration'] = fconc
        gentype['Volume'] = fvol
        gentype['Version'] = fvn
        return gentype
        
    def genDocs(self):
        ''' Deprecated method to generate a mapping of all barcode fields '''
        types = ['plateLot', 'plateMap', 'fluidConc', 'fluidType', 'fillStyle', 'fillVol', 'mapVersion', 'LUTDate', 'MFGDate', 'cavity', 'SN', 'Loc']
        alldict = []
        for p in types:
            print(p)
            a = getattr( self, p )
            a['Name'] = p
            alldict.append(a)
        barcodefields =  pandas.DataFrame(alldict)    
        print(barcodefields[['Length','Loc','Name']].sort_values(by='Loc'))
        for p in types:
            a = barcodefields['Codes'][barcodefields['Name']==p]
            if not a.isnull().iloc[0]:
                b = a.to_dict()
           #     print(b.keys())
                for key, value in b.items():
            #        print('k: ', key)
            #        print('v: ', value)
                    d = pandas.DataFrame(value, index=[0])
                    print( p,'Codes')
                    print(d.T)
                    print()