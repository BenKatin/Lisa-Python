# -*- coding: utf-8 -*-
"""
Created on Sat May 20 22:05:27 2017

@author: avandenbroucke
"""

import xml.etree.cElementTree as ET

class parseEPC():
    def __init__(self, filename=None):
        self.filename = filename
        if (filename):
            if filename.endswith('.epc'):
                self.epcfile  = ET.ElementTree(file=filename)
            else:
                print('Please specify *.epc file')
                return
        return        

    def getCalVersion(self,Name="Update Calibration Version"):        
        for elt in self.epcfile.iter():
            if elt.tag == 'Workstep':
                if elt.attrib['Name'] == Name:
                    for l in elt.iter():
                        if l.tag == 'Parameter' and l.attrib['name'] == 'SQL Parameters':
                            m = l
                          #  print(l.tag, l.attrib)
        try:                  
            mm = m.attrib['default']
            mu = mm.split(',')                
        except:
            return ''
        return mu[-1]
     
    def getFiles(self,ID="MAPFILE", Tag='Parameter'):   
        matches = []
        for elt in self.epcfile.iter():
            if elt.tag == Tag:
          #      print(elt.attrib)
                if 'id' in elt.attrib:
                    if elt.attrib['id'] == ID:
                        for l in elt.iter():
                            if l.tag == Tag : #and l.attrib['name'] == 'SQL Parameters':
                                matches.append(l)
                            #    print(l.attrib['default'],l.tag, l.attrib)
       
        allmatches = []                     
        for m in matches:                     
            try:                       
                mm = m.attrib['default']
                allmatches.append(mm)                
            except:
                continue
        return allmatches
   
    def getSupportFiles(self,AttributeIDs=['MAPFILE'],Tag='Parameter'):
        files = []
        TagID = Tag
        for id in AttributeIDs:
            f = self.getFiles(ID=id,Tag=TagID)
            if len(f) > 0 :
                for file in f:
                    files.append(file)
        return files

    def getAllCSVFiles(self):
        return self.getSupportFiles(AttributeIDs = [ 'MAPFILE' ,'TransferPickList','FITP0FILE','FITP1FILE','SpeedAccelValuesFile','StageTestPickListFile'])

    def getAllXMLFiles(self):
        return self.getSupportFiles(AttributeIDs = ['MISetup'] )
        
    def getAllSQLFiles(self):
        return self.getSupportFiles(AttributeIDs = ['SQL_FILE'] )
            
    def getAllMISCFiles(self):
        return self.getSupportFiles(AttributeIDs = ['MiscFile'], Tag='MiscFileName' )
            
    def getAllFiles(self):
        csv = self.getAllCSVFiles()
        xml = self.getAllXMLFiles()
        sql = self.getAllSQLFiles()
        msc = self.getAllMISCFiles()
        allfiles = []
        for i in csv,xml,sql,msc :
            if len(i) > 0 :
                for file in i:
                    allfiles.append(file)
        return allfiles    
        
    def setCalVersion(self,Version="",Name="Update Calibration Version"):        
        if Version == "" :
            print('Please specify version number !')
            return
        sqltag = 'SQL Parameters'
        for elt in self.epcfile.iter():
            if elt.tag == 'Workstep':
                if elt.attrib['Name'] == Name:
                    for l in elt.iter():
                        if l.tag == 'Parameter' and l.attrib['name'] == sqltag:
                            m = l
        mm = m.attrib['default']
        mu = mm.split(',')
        mu[-1] = ' ' +  str(Version)
        mmm = ','.join(mu)
        m.attrib['default'] = mmm                
        return    

    def write(self, filename=""):
        if filename == "" and self.filename == "":
            print("Please specify file to write")
            print("Exiting.")
            print("")
            return
        if filename == "":
            filename = self.filename
        self.epcfile.write(filename)     
        return
     
    def updateCalVersion(self,Version="")  :
         PrevRev = self.getCalVersion()
         if PrevRev == '':
             print('Skipping file ', self.filename)
             return
         PrevProtocol = '"' + PrevRev.strip() + '"'
         CurRev = ' ' + str(Version)
         CurProtocol = '"' + str(Version) + '"'
         filename =  self.filename
         with open(filename, 'r+') as f:
             content = f.read()
             f.seek(0)
             f.truncate()

             # below is an example from my extractPlateSQL.py – the ‘<xyz>’ are target strings to be replaced.
             f.write(content.replace(PrevRev, CurRev)
                            .replace(PrevProtocol,CurProtocol)
             )
       
             f.close()
         return    
   