# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 14:07:16 2017

@author: jrubin
"""
from pprint import pprint as pp
import pyodbc
import shutil
import os

cursor = None

def quote(string): # Quote strings and escape quotes.
    if string is not None:
        return "'" + string.replace("'","''") + "'"
    else:
        return None

def quoteArray(stringArray, typeArray):
    for index, item in enumerate(typeArray):
        if stringArray[index] is None: # Python None's will have to be turned to "NULL"
            stringArray[index] = "NULL"
        elif 'char' in item: # Strings will need to have single quote characters around them for tsql.
            stringArray[index] = quote(stringArray[index])
        elif 'text' in item: # Strings will need to have single quote characters around them for tsql.
            stringArray[index] = quote(stringArray[index])
        elif 'date' in item: # Also needs to be quoted.
            stringArray[index] = quote(stringArray[index].strftime("%Y-%m-%d %H:%M:%S"))    
        #stringArray[index] = quote(stringArray[index])
        else: # Otherwise, should be a number or data... shold be converted to string, but unquoted.
             stringArray[index] = str(stringArray[index])
             
def extractTableData(table, conditional = "", fieldOverrides={}, sqlMessage=False):

    outString = ''

    # Get info on all non-identity columns.  Doesn't depend on column names (D2AMemory for example is inconsistent in the naming of the ID column)    
    columns  =  cursor.execute(" SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME =  '"+table+"' AND columnproperty(object_id('"+table+"'), COLUMN_NAME,'IsIdentity') = 0").fetchall()
   
    colNames = [ i[0] for i in columns ]

    colTypes = [ i[1] for i in columns ]
    
    row = cursor.execute("SELECT " + ', '.join(colNames) + " FROM " + table + " " + conditional).fetchone()

    if row is not None:
        moreToDo = True          
        while moreToDo:
            rowCountThisInsert = 0
            q = '\n\nINSERT INTO ' + table + ' (' + ', '.join(colNames) + ')\nVALUES '

            outputRows = []
            while row is not None and rowCountThisInsert < 900: # SQL Server 2008 only lets us insert 1000 rows at a time.  Doing 900 row batches until done.
               rowCountThisInsert += 1
               quoteArray(row, colTypes)
               for key, val in fieldOverrides.items():
                   try:
                       idx=colNames.index(key)
                       row[idx] = val
                   except: 
                       print('Warning: requested wildcard field "' + key + '" to be set to "' + val + '".  No such field exists in table "' + table + '".')

               outputRows.append(', '.join(row))       
               row = cursor.fetchone()
            
            q += '\n(' + '),\n('.join(outputRows) + ')'
                            
            outString += q
            
            outString += '\n'
            
            if sqlMessage:
                outString += "PRINT(" + sqlMessage + ")\n\n"

            if row is None:
                moreToDo = False

    return outString
    
def getPlateContentInsertString(PlateTypeName,  fieldOverrides = {}):
    
    print('Extracting plate: ' + PlateTypeName + '\n')
    
    fullOutString = ''

    tablesToExtract = [ 
                        'Coefficient',
                        'LUT',
                        'LUT2D',
                        'Parameter',
                        'MIPConfiguration',
                        'PingParameters',
                        'PlateSignature',
                        'PlateType',
                        'ReferenceWaveforms',
                        'TransferVolume',
                        'WellAdjustment',
                        'PlateRegistration',
                        'PowerSweep'
                        ]
    
    for table in tablesToExtract:
        
        # for some tables we'll want explicit plateTypeNames - like 384Meas - for some plateTypes,
        # the user will be able to change in SQL, so these will need to turn into @ variable -
        # thus different escaping for SQL print statement.
        if 'PlateTypeName' in fieldOverrides:
            message = "LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into " + table + " for PlateType: \"'+"+fieldOverrides['PlateTypeName']+"+'\".'"
        else:
            message = "LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into " + table + " for PlateType: \""+PlateTypeName+"\".'"
           
    
        fullOutString += extractTableData(table,
                                          conditional       = "WHERE PlateTypeName = '" + PlateTypeName + "'",
                                          fieldOverrides    = fieldOverrides,
                                          sqlMessage        = message )
    
    return fullOutString

def getClassificationDetails(ClassifiedPlateName):
    q = "SELECT InstrumentName, TransducerName, PlateTypeName, UnclassifiedName, Analysis, PlateFormFactor, Measurement FROM PlateClassification WHERE PlateTypeName = '" + ClassifiedPlateName + "'" 
    row = cursor.execute(q).fetchone()
    
    if row:
        return { "InstrumentName"   : row[0],
                 "TransducerName"   : row[1],
                 "PlateTypeName"    : row[2],
                 "UnclassifiedName" : row[3],
                 "Analysis"         : row[4],
                 "PlateFormFactor"  : row[5],
                 "Measurement"      : row[6]  }
    else:
         raise Exception("No entries found with PlateTypeName " + ClassifiedPlateName + " in PlateClassification.")


def extractPlateSQL(PlateTypeName, **kwargs):
 
    global cursor
    
    # Define defaults
    settings = {
                              'Server' : 'localhost',
                      'SourceDatabase' : 'MEDMANdb',
                 'DestinationDatabase' : 'MEDMANdb',                
                      'outputFileName' : PlateTypeName + '.sql',
                   'SQLTemplateFolder' : os.path.abspath(os.path.dirname(__file__)),
                      'SQLForSwissard' : False
               }
    
    # Replate default settings.
    for key, value in kwargs.items():
        if key not in settings:
            raise Exception("I don't know argument: " + key + ".  Sorry quitting.")
        settings[key] = value
    print('Settings:')
    pp(settings)
    
    cnxn = pyodbc.connect('Trusted_Connection=yes', driver = '{SQL Server Native Client 10.0}', server = settings['Server'], database=settings['SourceDatabase'])
    cnxn.autocommit = True
    cursor = cnxn.cursor()
    
    classificationDetails = getClassificationDetails(PlateTypeName)
    
    print('')
    print('Classification details:')
    pp(classificationDetails)
    print('')
    
    print("UnclassifiedName: " + classificationDetails['UnclassifiedName'])
         
    print('Writing file ' + settings['outputFileName'] + '...', end='')
    
    SQLTemplatePath = os.path.join(settings['SQLTemplateFolder'], 'plateSQLTemplate.sql')
    
    shutil.copyfile(SQLTemplatePath, settings['outputFileName'])    
    
    with open(settings['outputFileName'], 'r+') as f:
        content = f.read()
        f.seek(0)
        f.truncate()
        
        if settings['SQLForSwissard']:
            varDefString = "DECLARE @UnclassifiedName VARCHAR(MAX) = \'$(UnclassifiedName)\'\n"
        else:    
            varDefString  = 'USE '    + settings['DestinationDatabase'] + '\n\n'
            varDefString += "DECLARE @UnclassifiedName VARCHAR(MAX) = '" + classificationDetails['UnclassifiedName'] + "'\n"
        
        varDefString += "DECLARE @ClassifiedName   VARCHAR(MAX) = '" + PlateTypeName + "'\n\n"

        varDefString += "-- Details for updating plate classification.\n"

        if classificationDetails['Analysis'] is not None:
            varDefString += "DECLARE @PCAnalysis        VARCHAR(MAX) = '" + classificationDetails['Analysis']        + "'\n"
        else:
            varDefString += "DECLARE @PCAnalysis        VARCHAR(MAX) = NULL\n"

        if classificationDetails['Measurement'] is not None:            
            varDefString += "DECLARE @PCMeasurement     VARCHAR(MAX) = '" + classificationDetails['Measurement']     + "'\n"
        else:
           varDefString += "DECLARE @PCMeasurement     VARCHAR(MAX) = NULL\n"

        varDefString += "DECLARE @PCInstrumentName  VARCHAR(MAX) = '" + classificationDetails['InstrumentName']  + "'\n"
        varDefString += "DECLARE @PCTransducerName  VARCHAR(MAX) = '" + classificationDetails['TransducerName']  + "'\n"
        varDefString += "DECLARE @PCPlateFormFactor VARCHAR(MAX) = '" + classificationDetails['PlateFormFactor'] + "'"

        mainPlateInsertString = getPlateContentInsertString( PlateTypeName, fieldOverrides = {'PlateTypeName':'@ClassifiedName'})
        
        D2AMemoryWaveform = cursor.execute("SELECT FileName FROM PingParameters WHERE PlateTypeName = '" + PlateTypeName + "'").fetchall()[0][0]
        
        D2AMemoryDetails  = extractTableData('D2AMemory',
                                              fieldOverrides    = {'MemoryAddress':'@FreeMemoryAddress'}, # @FreeMemoryAddress is defined in the template and computed on the local system at runtime. 
                                              conditional       = "WHERE Waveform = '" + D2AMemoryWaveform + "'",
                                              sqlMessage        = "LTRIM(STR(@@ROWCOUNT)) + '  row(s) inserted into D2AMemory for waveform: \""+D2AMemoryWaveform+"\".'" )
         
        unclassifiedPlateInsertString = getPlateContentInsertString( classificationDetails['UnclassifiedName'], fieldOverrides = {'PlateTypeName':'@UnclassifiedName'} )

        analysisPlateInsertString = ''
        if classificationDetails['Analysis'] is not None:
            analysisPlateInsertString   = '\n\n-- Necessary analysis plate, ' + classificationDetails['Analysis'] + ' missing.  Adding...\n'
            analysisPlateInsertString  += getPlateContentInsertString(classificationDetails['Analysis'])

        measurementPlateInsertString = ''
        if classificationDetails['Measurement'] is not None:
            measurementPlateInsertString  = '\n\n-- Necessary measurement plate, ' + classificationDetails['Measurement'] + ' missing.  Adding...\n'
            measurementPlateInsertString += getPlateContentInsertString(classificationDetails['Measurement'])

        f.write(content.replace('<VariableDefinitions>'      , varDefString)
                       .replace('<AnalysisPlateDetails>'     , analysisPlateInsertString )
                       .replace('<MeasurementPlateDetails>'  , measurementPlateInsertString )
                       .replace('<UnclassifiedPlateDetails>' , unclassifiedPlateInsertString )
                       .replace('<MainPlateDetails>'         , mainPlateInsertString )
                       .replace('<D2AMemoryWaveform>'        , D2AMemoryWaveform )
                       .replace('<D2AMemoryDetails>'         , D2AMemoryDetails ))
        
        f.close()
    
        print(' done.')

def getListOfHIDPlateTypes(**kwargs):
     # Define defaults
    settings = {
                              'Server' : 'localhost',
                      'SourceDatabase' : 'MEDMANdb',
                        'DestinationDatabase' : '',                
                      'outputFileName' : 'l',
                      'SQLTemplateFolder' : os.path.dirname(__file__),
                       'SQLForSwissard' : False
               }
    
    # Replate default settings.
    for key, value in kwargs.items():
        if key not in settings:
            raise Exception("I don't know argument: " + key + ".  Sorry quitting.")
        settings[key] = value
    
    pp(settings)
    
    cnxn = pyodbc.connect('Trusted_Connection=yes', driver = '{SQL Server Native Client 10.0}', server = settings['Server'], database=settings['SourceDatabase'])
    
    cursor = cnxn.cursor()
    q = "SELECT PlateTypeName FROM PlateType WHERE PlateUse = 'HID'"        
    return [ f[0] for f in cursor.execute(q) ]

    
def extractAllPlateSql(**kwargs):
	dir = 'ExtractedPlateSQLs'
	for plate in getListOfHIDPlateTypes(**kwargs):
	
		if not os.path.exists(dir):
			os.makedirs(dir)
		
		args = kwargs
		args['outputFileName'] = os.path.join(dir, plate)
		
		extractPlateSQL(plate, **kwargs)
#		os.chdir('../')
    
def genAllSql():    
    dirs = [ '\\\\fserver\\people\\Arne\\2017\\525_protocols\\CUSTOM' , 
      '\\\\fserver\\people\\Arne\\2016\\Lemonade\\MFG_Lemonade\\CUSTOM' ]
    databases = ['E525_GOLD','E555_GOLD']  
    for i,folder in enumerate(dirs):
        os.chdir(folder)
        extractAllPlateSql(SourceDatabase = databases[i], Server='AVANDEN-NUC\Labcyte', SQLTemplateFolder=folder)
      
# extractPlateSQL('384PPL_AQ_CP')

# AVDB -- Sorry Josh for messing with your code ;-) 6/5/2017e

#extractPlateSQL('384LDVS_Plus_AQ_GP',  SourceDatabase = 'E1704_SourceForPlusGPPlate_2_x_12')
#extractPlateSQL('384PPL_Plus_AQ_GP',   SourceDatabase = 'E1704_SourceForPlusGPPlate_2_x_12')
#extractPlateSQL('384PPL_Plus_AQ_GPSA', SourceDatabase = 'E1704_SourceForPlusGPPlate_2_x_12')
#extractPlateSQL('384PPL_Plus_AQ_GPSB', SourceDatabase = 'E1704_SourceForPlusGPPlate_2_x_12')
#extractPlateSQL('384PPG_Plus_AQ_GP',   SourceDatabase = 'E1704_SourceForPlusGPPlate_2_x_12')
#extractPlateSQL('384PPG_Plus_AQ_GPSA', SourceDatabase = 'E1704_SourceForPlusGPPlate_2_x_12')
#extractPlateSQL('384PPG_Plus_AQ_GPSB', SourceDatabase = 'E1704_SourceForPlusGPPlate_2_x_12')