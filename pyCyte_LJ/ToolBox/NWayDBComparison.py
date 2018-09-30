# -*- coding: utf-8 -*-
"""
@author: Joshua Rubin
jrubin@labcyte.com
May 3, 2018

This module contains the function compareTables, which performs a comparison of
the requested table across all of the databases requested.

import this way: from pyCyte.ToolBox.NWayDBComparison import compareTables
"""

import pyodbc
import textwrap as tw

logPath = None

def tt(t, d):
    return tw.indent('\n'.join(tw.wrap(t, width=100)), ''.join(['\t' for i in range(d)]), lambda line: True) 

def pp(t, d=0, end='\n'):   
    print(tt(t, d) + end)
    
    if logPath:
        with open(logPath, 'a') as f:
           f.write(tt(t, d) + end + '\n')

def deepSort(argIndex):
    def theSort(x):
        if x[argIndex] is None:
            return ' '
        else:
            return(str(x[argIndex]))
    
    return theSort

def initializeDB(server):
    cnxn = pyodbc.connect('Trusted_Connection=yes', driver = '{SQL Server Native Client 10.0}', server = server)
    cnxn.autocommit = True
    return cnxn.cursor().execute

kNoRow = '<row missing>'

def compareTables(databaseServer, DBs, tableName, rowKeyFields = None, ignoreFields = [], detail=False, outputFilePath = False):
    """
    This function presents differences between an arbitrary number of databases
    residing on server <databaseServer>.
    
    DBs             The list of database names to compare.
    tableName       The table name to compare across databases.
    rowKeyFields    A list of table columns defining a unique row in the table.
                    The order doesn't matter, but results will be sorted
                    alphebetically (with null appearing first; so typically put
                    plateTypeName as the first rowKeyFields if relevent)
                    first field to last.
    ignoreFields    A list of fields to ignore differences in.
    detail [false]  To much info- you don't want this.
    outputFilePath  A path (including filename) to a text file you'd like the
                    output logged in. Be sure to use a 'raw' string (with 'r')
                    r'c:\example\PlateType.txt'.
    """

    #####
    # Set up database server
    db = initializeDB(databaseServer)

    ####
    # Set up logging
    global logPath
    
    if outputFilePath:
        logPath = outputFilePath
        with open(logPath, 'w'):
          pass
    else:
        logPath = None

    rowKeys       = []
    compareFields = []
    
    for DB in DBs:
        ## Generate the superset of all fields and rows.    
        db("USE " + DB)
        rowKeys += [ tuple(field) for field in db("SELECT "+','.join(rowKeyFields)+" FROM "+ tableName).fetchall() ]

        q = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '" +tableName+ "' AND COLUMN_NAME != '" + "' AND COLUMN_NAME != '".join(rowKeyFields + ignoreFields)+"'"
        compareFields += [ field[0] for field in db(q)]

    # De-dup.  Now rowKeys is the list of all keys that appear across this table in all databases.  compareFields contains all the fields across all databases to compare.
    rowKeys       = list(set(rowKeys))
    compareFields = list(set(compareFields))
    
    # Now sort the heck out of the row keys so that they're alphabetical in each field left-to-right with "None" first (so that e.g. plateType = null can appear on top.) 
    for i in reversed(range(len(rowKeyFields))):
        rowKeys = sorted(rowKeys, key=deepSort(i))

    # For each database, get all rows    
    dbData = [] # [instrument:{rowKey:[compareFieldValues]}]
    for DB in DBs:

         q = 'SELECT ' + ",".join(rowKeyFields) + ', ' + ", ".join(compareFields) + " FROM " + DB +".dbo."+tableName

         rowContent = {}

         for row in db(q).fetchall():
            rowContent[tuple(row)[:len(rowKeyFields)]] = tuple(row)[len(rowKeyFields):]

         dbData.append(rowContent)

    pp('Showing differences in ' + tableName + ' for:', end='')
    pp(', '.join(DBs) + ' on server "' + databaseServer + '"\n')
    
    for row in rowKeys:
    
        instrumentsMissingTable = []
        instrumentsWithTable = []
        
        valsByFieldByInstrument = {}
        
        for i, instrument in enumerate(DBs):
            if row in dbData[i]:
                instrumentsWithTable.append(instrument)
                for compareFieldIndex, compareField in enumerate(compareFields):
                    if compareField not in valsByFieldByInstrument:
                        valsByFieldByInstrument[compareField] = []
                    valsByFieldByInstrument[compareField].append(dbData[i][row][compareFieldIndex])
                
            else:
                instrumentsMissingTable.append(instrument)
                for compareFieldIndex, compareField in enumerate(compareFields):
                    if compareField not in valsByFieldByInstrument:
                        valsByFieldByInstrument[compareField] = []
                    valsByFieldByInstrument[compareField].append(kNoRow)
                    
        if (instrumentsMissingTable):
            pp(' '.join(map(lambda x: str(x) if x is not None else '<null>', list(row))), end='', d=1)
            pp('> Present in ' + ', '.join(instrumentsWithTable) + "; missing in: " + ', '.join(instrumentsMissingTable), d=1)
        
        differencesInFields = False
      
        ####
        ## This is just so that we can print the field names if there are differences.
        for compareFieldIndex, compareField in enumerate(compareFields):
            valuesPresent = valsByFieldByInstrument[compareField]
            v = set(valuesPresent) - set([kNoRow])
            if len(v) != 1:
                differencesInFields = True
    
        if differencesInFields:
             pp(' '.join(map(lambda x: str(x) if x is not None else '<null>', list(row))), d=1)
        ####
        
        for compareFieldIndex, compareField in enumerate(compareFields):
            valuesPresent = valsByFieldByInstrument[compareField]
            v = set(valuesPresent) - set([kNoRow])
         
            if len(v) == 1:
                if  detail==True:
                    pp( compareField + ': ("' + str(list(v)[0]) + '" for all instruments with this row.)',d=2)
            else: 
                differencesInFields = True
                pp( compareField + ':', d=2 )
                for i, instrument in enumerate(DBs):
                      if instrument in instrumentsWithTable:
                         pp('%9s'%instrument + ' ' +str(valuesPresent[i]), d=2, end='') 
                pp('')               

#compareTables('Parameter', rowKeyFields=['PlateTypeName', 'GroupName', 'ParameterName'], ignoreFields=['ParameterId'])
#compareTables('PlateType', rowKeyFields=['plateTypeName'], ignoreFields=['plateTypeId', 'CenterX', 'CenterY'])
#dbs = ['Alex_Tubes_1', 'Alex_Tubes_2']
#compareTables('lighthouse', dbs, 'MIPConfiguration',
#              rowKeyFields=['PlateTypeName','ParameterGroup', 'ParameterName', 'Iteration'],
#              ignoreFields=['MIPConfigurationID'],
#              outputFilePath=r'c:\guacamole\test.txt')