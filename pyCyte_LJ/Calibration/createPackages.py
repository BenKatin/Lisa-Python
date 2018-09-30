# -*- coding: utf-8 -*-
"""
Created on Fri Jun 23 14:39:25 2017

@author: avandenbroucke
"""
if __package__ is None or __package__ == '':
    from pyCyte.ToolBox import SimpleTools
    from pyCyte.Calibration import editEPC
    from pyCyte.Calibration import ExtractPlateSql
else:
    from ..ToolBox import SimpleTools
    from ..Calibration import editEPC
    from ..Calibration import ExtractPlateSql
import os, shutil, pandas

class createPackages():
    def __init__(self,rootfolder='\\\\fserver\\people\\Arne\\CalibrationProtocols'):
        self.rootfolder = rootfolder
        os.chdir(rootfolder)
        self.Server='AVANDEN-NUC\Labcyte'
        self.SQLTemplateFolder='\\\\fserver\\people\\Arne\\PYTHON\\pyCyte\\Calibration'
        self.verbose = True
        return

    def createSwissardPackage(self,Model='55X',Type='MFG'):
        os.chdir(self.rootfolder)
        os.chdir(Model)    
        os.chdir(Type)
        for i, folder in enumerate(['./Calibration','./HealthCheck','./Scaling']):
            if not os.path.exists(folder):
                print(' -- ERROR -- folder ', folder , ' does not exist in path ' , os.getcwd())
                return
            os.chdir(folder)
            if folder == './HealthCheck' :
                d =  '.'
                subfolders = [os.path.join(d,o) for o in os.listdir(d) if os.path.isdir(os.path.join(d,o))] 
                if len(subfolders) == 0:
                    subfolders = ['./']
            else:
                subfolders = ['./']
            thisdir = os.getcwd()
            for subfolder in subfolders:
                os.chdir(subfolder)                    
                epcfiles = SimpleTools.getFileList('*.epc')
                miscfiles = []          
                for file in epcfiles:
                    epc = editEPC.parseEPC(file)
                    for miscfile in epc.getAllFiles():
                       if miscfile not in miscfiles:
                            miscfiles.append(miscfile) 
                outputfolder = './Miscellaneous'
                if not os.path.exists(outputfolder):
                    os.mkdir(outputfolder)            
                for filename in miscfiles:
                    src = self.rootfolder + './Miscellaneous/' + filename
                    dest = outputfolder + './' + filename
                    if os.path.exists(src):
                        shutil.copyfile(src,dest)
                    else:
                        print(' -- ERROR ---  file ', src, ' does not exist !' )
                os.chdir(thisdir)        
            os.chdir('../')        
            if ( i == 0 ):
               zipmode = "w"
            else:
               zipmode = "a" 
            zipfile = 'EPC_Protocols__' + Type + '_' + Model + '.zip'
            SimpleTools.zipfolder(folder=folder,zipFileFolder=os.getcwd(),zipFileName=zipfile , verbose=self.verbose, mode=zipmode)
            if ( folder == './HealthCheck' ):
                for f in subfolders:
                    shutil.rmtree(os.path.join(os.getcwd(),folder,f,outputfolder))
            else:    
                shutil.rmtree(os.path.join(os.getcwd(),folder,outputfolder)    )
                
  #      SimpleTools.zipfolder(folder=outputfolder)  
        return 
                
        
    def genPlateSQL(self, Model='55X', Type='MFG'):
        os.chdir(os.path.join(self.rootfolder,Model,Type,'Custom'))
        if Model == '55X':
            db = 'E555_GOLD'
        else:
            db = 'E525_GOLD'
        ExtractPlateSql.extractAllPlateSql(SourceDatabase = db, Server= self.Server, SQLTemplateFolder=self.SQLTemplateFolder, SQLForSwissard=True)
        return

    def createEPCX(self,epcxfilename, epcfilename,platetype, unclassifiedplatetype) :   
        lines = []
        line1 = '<EpcCalibrationGroups name="Auto-Generated" Version="" >'
        lines.append(line1)
        line2 = '<CalibrationGroup generation="2.4" jointsuccess="false" name="CustomPlateTypes" type="CustomPlates" >'
        lines.append(line2)
        line3 = '<File name="' + epcfilename + '" platetype="' + platetype + '" unclassifiedplatetype="' + unclassifiedplatetype +'" executionstatus="False" />'
        lines.append(line3)
        line4 = '</CalibrationGroup>'
        lines.append(line4)
        line5 = '</EpcCalibrationGroups>'
        lines.append(line5)
        lines = [line1,line2,line3,line4,line5]
        print('Creating file ', epcxfilename, ' in folder ' , os.getcwd())
        with open(epcxfilename, "w") as text_file:
            for l in lines:
                text_file.write(l)
                text_file.write('\n')
        return        

    def createCustom(self, Model='55X', Type='MFG', Tag=None   ):
        customfolder = os.path.join(self.rootfolder,Model,Type,'Custom')
        srcfolder = os.path.join(self.rootfolder,'./Miscellaneous')
        if not os.path.exists(customfolder):
           print('Folder ', customfolder, ' does not exists !')
           print('Exiting')
           return
        os.chdir(customfolder)
        epcfiles = SimpleTools.getFileList('*.epc')
        arenaPmDataFrame = pandas.DataFrame()
        if (Tag):
            arenaPmFile = Tag + '_PartNumber_List.csv'
            if os.path.isfile(arenaPmFile):
                arenaPmDataFrame = pandas.read_csv(arenaPmFile)
        for file in epcfiles:
            folder = os.path.dirname(file)
            platetype = os.path.splitext(os.path.basename(file))[0]
#            print('folder :: ', folder, ' file: ', file)
            PN, Z = self.getArenaPartNr(arenaPmDataFrame, platetype) 
            epcxfile = os.path.join(folder, folder + '.epcx')
            if not os.path.exists(epcxfile):
                calsplit = folder.split('_')
                calsplit[0] = calsplit[0][0:-1]
                unclasplate = '_'.join(calsplit)
                self.createEPCX(epcxfilename=epcxfile,epcfilename=os.path.basename(file), platetype=os.path.basename(folder), unclassifiedplatetype=os.path.basename(unclasplate))
            outputfolder = folder + './Miscellaneous'
            if not os.path.exists(outputfolder):
                os.mkdir(outputfolder)
            epc = editEPC.parseEPC(file)
            miscfiles = epc.getAllFiles()    
            for filename in miscfiles:
                src = srcfolder + './' + filename
                dest = outputfolder + './' + filename
                if os.path.exists(src):
                    shutil.copyfile(src,dest)
                else:
                    print(' -- ERROR ---  file ', src, ' does not exist !' )
            zipfoldername = os.path.join(os.getcwd(),folder)    
 #           print( ' zipfoldername : ', zipfoldername, ' os.getcwd() = ' , os.getcwd())
            prefix = PN + '-' + Z + '__' + Model + '__'
            if (Tag):
                prefix += Tag
                prefix += '__'
            enhanced_zipfilename = prefix + platetype  + '.zip'  
            SimpleTools.zipfolder(folder=zipfoldername)        
            zipfilename = platetype + '.zip'
            # now delete the miscellaneous folder
  #          print(' folder content:: ', os.listdir())
            shutil.move( folder +'/' + zipfilename,  folder + '/' + enhanced_zipfilename)
            
            shutil.rmtree(os.path.join(os.getcwd(),outputfolder))
        return 
    
    def getArenaPartNr(self, arenaPmDataFrame, platetypename):
        PN = 'XXX-YYYYY'
        Z = 'Z'
        if arenaPmDataFrame.empty :
            return PN, Z
        matches = arenaPmDataFrame[arenaPmDataFrame['PlateType'] == platetypename ]      
#        print(' Columns :: ', arenaPmDataFrame.columns)
        if len(matches) > 0 :
#            print('matches: ', matches)
            PN = str(matches['PartNumber'].values[0])
            Z = str(matches['Version'].values[0])
        return PN, Z
        
    def genAllSwissard(self):
        self.createSwissardPackage()
        self.createSwissardPackage(Type='Service_TSwap')
        self.createSwissardPackage(Type='MFG_TSwap')
        self.createSwissardPackage(Model='525')
        
    def genAllCustoms(self, genSQL=False):
        if (genSQL):
            self.genPlateSQL()
            self.genPlateSQL(Model='525')
        self.createCustom(Tag='FC')
        self.createCustom(Tag='FC',Model='525')
        self.createCustom(Tag='TB', Type='TxBandAid')


            