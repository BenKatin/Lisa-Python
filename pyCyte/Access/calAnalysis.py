# -*- coding: utf-8 -*-
"""
Created on Thu Jul 20 09:02:02 2017

@author: lchang
"""

import os
import fnmatch
import pandas as pd
import numpy as np
import time
import pyCyte.ToolBox.SimpleTools as st

class calAnalysis():
    def __init__(self):
        self.plateCal = ['384PPL_DMSO2','384PPL_AQ_CP','384PPL_AQ_GP2','384PPL_AQ_BP2','384PPL_AQ_SP2',
                    '384LDVS_AQ_B2','384LDVS_DMSO','1536LDVS_DMSO','1536LDVS_DMSO_HT']
        return
    
    def plateSpecs (self,platetype = 'DMSO2'):
        # MFG specifications
        # plate: [nomvol,vol%,CV,Reliability,Outlier,Empties,Outlier per plate,Reliability per plate]
        spec = {'CP':[50,  0.12,    8,  3/1000, 10/1000,    5/368,  368/368, 5/368],
                'BP2':[50, 0.08,    6,  3/1000, 10/1000,    5/368,  368/368, 5/368],
                'GP2':[50, 0.08,    6,  3/1000, 10/1000,    5/368,  368/368, 5/368],
                'SP2':[50, 0.08,    6,  3/1000, 10/1000,    5/368,  368/368, 5/368],
                'B2':[50,  0.08,    6,  3/1000, 20/1000,    5/368,  368/368, 5/368],
                'DMSO2':[50, 0.05,  5,  3/5000, 4/1000,     5/368,  2/368, 5/368],
                'DMSO':[50, 0.05,   5,  3/5000, 4/1000,     5/368,  2/368, 5/368],
                'HT': [50,  0.05,   5,  3/5000, 4/1000,    5/368,  2/368, 5/368]
    #            'LDV_DMSO':[5,5,3/5000,4/1000],
                }
        if platetype not in spec.keys():
            print(' *** ERROR -- Platetype not found ')
        for plate, values in spec.items():
            if plate == platetype:           
                v = values
        return v
    
    def calStatus(self):
        if (os.path.basename(os.getcwd()) != 'Calibration' ) :
            print (' **** ERROR ***, need to be in Calibration folder ')
            return
        thisdir = os.getcwd()
        TX=thisdir.split('\\')[-4]
        outfile = 'Calibration__Incomplete__'+TX+'.xlsx'
        sumFiles = st.getFileList('*Processed__DataSummary*.xlsx')
        writer = pd.ExcelWriter(outfile,engine='xlsxwriter')
        
        alldata = []
        finalCal = []
        for f in sumFiles:
            print('<< Processing' + f +' >> ')
            platetype = f.split('\\')[1]
            FT = f.split('\\')[-3]
            status = f.split('__')[-1].split('.xlsx')[0]
            alldata.append([platetype, FT, status])
            if 'FinalTest' in FT:
                ds = pd.read_excel(f)
                ds.to_excel(writer, sheet_name=platetype, index = False)
                workbook = writer.book
                worksheet = writer.sheets[platetype]
                lines = len(ds)+1
                ftst = lines+1
                self.applySheetFormat (platetype.split('_')[-1],workbook,worksheet,ds,lines,ftst)
                finalCal.append([platetype, FT, status])
        df = pd.DataFrame(alldata)
        dfinal0 = pd.DataFrame(finalCal)
        dfinal0.columns = ['Platetype', 'Test', 'Status']
        
        diff = set(dfinal0['Platetype']) & set(self.plateCal)
        for p in self.plateCal:
            if p not in diff:
                finalCal.append([p,'NULL','Incomplete'])
        
        dfinal = pd.DataFrame(finalCal)
        dfinal.columns = ['Platetype', 'Test', 'Status']
          
        dfinal.to_excel(writer,'Calibration_Summary')
        
        # Add a format. Light red fill with dark red text.
        format1 = workbook.add_format({'bg_color': '#FFC7CE',
                                   'font_color': '#9C0006'})                         
        # Add a format. Green fill with dark green text.
        format2 = workbook.add_format({'bg_color': '#C6EFCE',
                                   'font_color': '#006100'})
        # Add a format.  Yello fill with orange text.
        format3 = workbook.add_format({'bg_color': '#FFFF00',
                                   'font_color': '#FF4500	'})  
        
        ws = writer.sheets['Calibration_Summary']
        ws.set_column('A:D', 20)
        condrange = 'D2:D' + str(lines+5)
        ws.conditional_format(condrange, {'type': 'cell', 'criteria': '==', 'value': '"FAIL"','format': format1})
        ws.conditional_format(condrange, {'type': 'cell', 'criteria': '==', 'value': '"PASS"','format': format2}) 
        ws.conditional_format(condrange, {'type': 'cell', 'criteria': '==', 'value': '"Incomplete"','format': format3}) 
      
        workbook.worksheets_objs.sort(reverse = True, key=lambda x: x.name)
        writer.save()
        if len(dfinal['Platetype']) == len(self.plateCal):
            if not 'Incomplete' in dfinal['Status'].values:
                if not 'FAIL' in dfinal['Status'].values:
                    outfileFinal = outfile.replace('Incomplete','COMPLETE__'+time.strftime('%Y%m%d'))
                    os.rename(outfile,outfileFinal)
        return dfinal
        
        
    def anaFT (self):
        # Starts in the Analysis folder
        if (os.path.basename(os.getcwd()) != 'Analysis' ) :
            print (' **** ERROR ***, need to be in Analysis folder ')
            return
        
        thisdir = os.getcwd()
        if not (thisdir.split('\\')[-2] == 'FinalTest' or 'FT' in thisdir ):
            print('**** ERROR -- need to be in \' FinalTest \' folder')
            return
        else:
            if thisdir.split('\\')[-2] == 'FinalTest':
                platetype = thisdir.split('\\')[-3]
                
            elif 'FT' in thisdir.split('\\')[-2]:
                platetype = thisdir.split('\\')[-4]
                        
        spec = self.plateSpecs(platetype.split('_')[-1])
        nomvol = spec[0]
        volSpec = spec[1]
        CVSpec = spec[2]
        relSpec=spec[3]
        outSpec = spec[4]
        empSpec = spec[5]
        outPPSpec = spec[6]
        relPPSpec = spec[7]
        
        summary = fnmatch.filter(os.listdir(),'DataSummary*.csv*')
        df = pd.read_csv(summary[0])
        df.columns = df.columns.str.replace('Unnamed: 0','Conc')
        df['Status'] = 'PASS'
        df['Status'][df['CV'] > CVSpec] = 'FAIL'
        df['Status'][(abs(df['Mean']-nomvol) / nomvol) > volSpec ] = 'FAIL'
        df['Status'][df['Reliability']/df['N'] > relPPSpec] = 'FAIL'
        df['Status'][df['Outlier']/df['N'] > outPPSpec] = 'FAIL'
        df['Status'][df['Empties']/df['N'] > empSpec] = 'FAIL'
        
        self.writeReport(platetype,df,summary[0])
        return df
        
            
    def writeReport(self,platetype,df, filename):
        if 'FAIL' in df['Status'].values:
            xlout='Processed__'+filename.split('.csv')[0]+'__FAIL.xlsx'
        if not 'FAIL' in df['Status'].values:
            xlout='Processed__'+filename.split('.csv')[0]+'__PASS.xlsx'
        self.writeXLS(platetype,dataframe=df,xlfilename=xlout)
        return
    
    def writeXLS(self,platetype, dataframe, xlfilename=''):    
        
        spec = self.plateSpecs(platetype.split('_')[-1])
        relSpec = spec[3]
        outSpec = spec[4]
        
        if ((dataframe['Reliability'].values.sum()/dataframe['N'].values.sum()) > relSpec) or ((dataframe['Outlier'].values.sum()/dataframe['N'].values.sum()) > outSpec):
            xlfilename = xlfilename.replace('PASS','FAIL')
            
        writer = pd.ExcelWriter(xlfilename,engine='xlsxwriter')
        dataframe.to_excel(writer, sheet_name=platetype, index = False)
        workbook = writer.book
        worksheet = writer.sheets[platetype]
        dec_fmt = workbook.add_format({'num_format': '0.00'})
    #    pmt_fmt = workbook.add_format({'num_format': '0.00'})
        pass_fmt = workbook.add_format({'align': 'center'})
        
        worksheet.set_column('C:F', 9, dec_fmt)
        worksheet.set_column('G:I', 9)
        worksheet.set_column('J:J',9, dec_fmt)
        worksheet.set_column('K:K',10, pass_fmt)
        lines = len(dataframe)+1
     
        #Footer
        footformat = workbook.add_format({'bold':True})
        footformat2 = workbook.add_format({'font_size':10, 'italic':True})
        ftst = lines+1
        ftcol = 0       
        worksheet.write(ftst,ftcol, 'TOTAL', footformat)
        worksheet.write(ftst,ftcol+1, dataframe['N'].values.sum())
        worksheet.write(ftst,ftcol+6, dataframe['Reliability'].values.sum())
        worksheet.write(ftst,ftcol+7, dataframe['Outlier'].values.sum())
        if (dataframe['Reliability'].values.sum()/dataframe['N'].values.sum()) > relSpec:
            worksheet.write(ftst, ftcol+10, 'FAIL', pass_fmt)
        elif (dataframe['Outlier'].values.sum()/dataframe['N'].values.sum()) > outSpec:
            worksheet.write(ftst, ftcol+10, 'FAIL', pass_fmt)
        else:
            worksheet.write(ftst, ftcol+10, 'PASS', pass_fmt)
        worksheet.write(ftst+2,ftcol,'Date',footformat)  
        worksheet.write(ftst+2,ftcol+1, time.strftime('%Y%m%d'), footformat2)   
        
        self.applySheetFormat (platetype,workbook,worksheet,dataframe,lines,ftst)
            
        writer.save()
        return     
    
    def applySheetFormat (self,platetype,workbook,worksheet,dataframe,lines,ftst):
        
        spec = self.plateSpecs(platetype.split('_')[-1])
        nomvol = spec[0]
        volSpec = spec[1]
        minvol = (1-volSpec)*nomvol
        maxvol = (1+volSpec)*nomvol
        CVSpec = spec[2]
        relSpec = spec[3]
        outSpec = spec[4]
        empSpec = spec[5]
        outPPSpec = spec[6]
        relPPSpec = spec[7]
        
        # Add a format. Light red fill with dark red text.
        format1 = workbook.add_format({'bg_color': '#FFC7CE',
                                   'font_color': '#9C0006'})
        # Add a format.  crimson text.
        format1a = workbook.add_format({'font_color': '#DC143C'})                           
        # Add a format. Green fill with dark green text.
        format2 = workbook.add_format({'bg_color': '#C6EFCE',
                                   'font_color': '#006100'})
        
        condrange = 'K2:K' + str(lines+5)
        worksheet.conditional_format(condrange, {'type': 'cell', 'criteria': '==', 'value': '"FAIL"','format': format1})
        worksheet.conditional_format(condrange, {'type': 'cell', 'criteria': '==', 'value': '"PASS"','format': format2})     
        condrange = 'I2:I' + str(lines)
        worksheet.conditional_format(condrange, {'type': 'cell', 'criteria': '>', 'value': empSpec*dataframe['N'].values.mean(),'format': format1a})      
        condrange = 'H2:H' + str(lines)
        worksheet.conditional_format(condrange, {'type': 'cell', 'criteria': '>', 'value': outPPSpec*dataframe['N'].values.mean(),'format': format1a}) 
        condrange = 'G2:G' + str(lines)
        worksheet.conditional_format(condrange, {'type': 'cell', 'criteria': '>', 'value': relPPSpec*dataframe['N'].values.mean(),'format': format1a})                               
        condrange = 'F2:F' + str(lines)
        worksheet.conditional_format(condrange, {'type': 'cell', 'criteria': '>', 'value': CVSpec,'format': format1a})
        condrange = 'E2:E' + str(lines)
        worksheet.conditional_format(condrange, {'type': 'cell', 'criteria': '>', 'value': CVSpec,'format': format1a})      
        condrange = 'C2:C' + str(lines)
        worksheet.conditional_format(condrange, {'type':'cell', 'criteria': 'not between', 'minimum' : minvol, 'maximum': maxvol,'format':format1a}) 
    
        condrange = 'G'+str(ftst)+':G'+str(ftst+1)
        worksheet.conditional_format(condrange, {'type': 'cell', 'criteria': '>', 'value': relSpec*dataframe['N'].values.sum(),'format': format1a})                               
        condrange = 'H'+str(ftst)+':H'+str(ftst+1)
        worksheet.conditional_format(condrange, {'type': 'cell', 'criteria': '>', 'value': outSpec*dataframe['N'].values.sum(),'format': format1a})
        
        return
    