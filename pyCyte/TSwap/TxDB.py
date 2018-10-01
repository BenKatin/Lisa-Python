# -*- coding: utf-8 -*-
"""
This module wraps the functions needed to manage a merged transducer
database in the TxDB object.  Functions are:
          TxDB - Constructor that returns the TxDB object.
   getDefaults - Shows default database configure settings.  Can be
                 modified through optional constructor arguments.

Inquire with the TDB object and methods for more details.

Joshua Rubin - 2016 - For Labcyte
"""

import os
import sys
import time
import pyodbc
import hashlib
import subprocess

from . import mergeTransducerDB 

_TxDBDefaults = {'DBServer'       : 'Lighthouse',
                 'mergeDBName'    : 'Bonita',
                 'serverDataPath' :  None, # Unless this is specified, this will get set to the server default in the constructor.
                 'cipherPath'     :  r'\\Lighthouse\Cipher\cipher.exe' }

def getDefaults():
    """ Returns the default transducer database settings"""
    print('Note: serverDataPath default determined dynamically from server default when TxDB is created unless specified by user when calling constructor.  Print TxDB.serverDataPath after instantiation to check.')
    return _TxDBDefaults

class TxDB():
    """This object wraps all the functions needed to manage a merged transducer
       database.  Optional specifiable configuration arguments are:
               DBServer - The name of the database connection in your Windows,
                          Administrative Tools -> Data Sources (ODBC) configuration.
          mergeDBServer - The name of the merged transducer database to be manipulated
                          or created.
         serverDataPath - Where the database server likes to keep its database files.
                          Set based on server defaults.  Not determined until TxDB created.
             cipherPath - Where the Labcyte cipher executable resides with respect
                          to the database server.
        To view the defaults, run TxDB.viewDefaultSettings.                 
    """
    def __init__(self, **initArgs ):
        
        # Set defaults
        for key, val in _TxDBDefaults.items():
            setattr(self, key, val)

        # Modify defaults
        for key, val in initArgs.items():
            setattr(self, key, val)
        
        self.databaseTableString   = self.mergeDBName + ".dbo.globalDatabases"
        self.transducerTableString = self.mergeDBName + ".dbo.globalTransducer"
        self.instrumentTableString = self.mergeDBName + ".dbo.globalInstrument"
        
        # Setup database
        cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=lighthouse;Trusted_Connection=yes;')
        cnxn.autocommit = True
        self.cursor = cnxn.cursor()
        
        if not self.serverDataPath:
            self.serverDataPath = self.cursor.execute("exec master.dbo.xp_instance_regread N'HKEY_LOCAL_MACHINE', N'Software\Microsoft\MSSQLServer\MSSQLServer', N'DefaultData'").fetchall()[0][1]
        
    def _initializeTxDBIfMissing(self):
        """If not present, create a new mergeDB with global tables."""
    
        cursor                = self.cursor
        mergeDBName           = self.mergeDBName
        databasesTableString  = self.databaseTableString
        transducerTableString = self.transducerTableString
        instrumentTableString = self.instrumentTableString
   
        cursor.execute("IF DB_ID('"+mergeDBName+"') IS NULL \
                        CREATE DATABASE "+mergeDBName)    
        
        cursor.execute("IF OBJECT_ID('"+ transducerTableString + "','U') IS NULL \
                        CREATE TABLE " + transducerTableString + " (             \
                                            TX_SN NCHAR(32),   \
                                        Amplitude FLOAT,       \
                                        BeamWidth FLOAT,       \
                                     BeamSymmetry FLOAT,       \
                                       FitQuality FLOAT,       \
                                        BowlWidth FLOAT,       \
                                           Volume FLOAT,       \
                                          TxGroup VARCHAR(MAX),\
                               PRIMARY KEY (TX_SN)             \
                            );")    
                            
        cursor.execute("IF OBJECT_ID('"+ instrumentTableString + "','U') IS NULL \
                        CREATE TABLE " + instrumentTableString + " (             \
                                     Instrument_SN NCHAR(32),                    \
                               PRIMARY KEY (Instrument_SN)                       \
                            );")         
        
        cursor.execute("IF OBJECT_ID('"+ databasesTableString + "','U') IS NULL \
                        CREATE TABLE " + databasesTableString + " (             \
                                DatabaseId NCHAR(32),                           \
                                     TX_SN NCHAR(32),                           \
                             Instrument_SN NCHAR(32),                           \
                                     MC_SN NCHAR(32),                           \
                              DatabaseType VARCHAR(MAX),                        \
                             DatabaseStyle VARCHAR(MAX),                        \
                                   Version VARCHAR(MAX),                        \
                              OriginalPath VARCHAR(MAX),                        \
                                UploadDate DATETIME,                            \
                            SourceDatabase VARCHAR(MAX),                        \
                               PRIMARY KEY (DatabaseId),                        \
       CONSTRAINT FK_DatabasesTX         FOREIGN KEY (TX_SN)                    \
       REFERENCES "+ transducerTableString +" (TX_SN)         ON DELETE CASCADE,\
       CONSTRAINT FK_DatabasesInstrument FOREIGN KEY (Instrument_SN)            \
       REFERENCES "+ instrumentTableString +" (Instrument_SN) ON DELETE CASCADE);")

    def _addTxToGlobalInstrumentIfMissing(self, Instrument_SN):
        """Adds a Instrument SN to globalDatabases if it's not already there."""
        print('Adding instrument record if necessary.')

        cursor = self.cursor
        instrumentTableString = self.instrumentTableString        

        cursor.execute("IF (SELECT COUNT(*) FROM " + instrumentTableString + "  \
                             WHERE Instrument_SN = '" + Instrument_SN + "') = 0 \
                             INSERT INTO  " + instrumentTableString + "         \
                             (Instrument_SN) VALUES ('" + Instrument_SN + "')")
    def _addTxToGlobalTransducersIfMissing(self, TX_SN):
        """Adds a transducer SN to globalTransducers if it's not already there."""
        print('Adding transducer record if necessary.')    
        
        cursor = self.cursor
        transducerTableString = self.transducerTableString             
        
        cursor.execute("IF (SELECT COUNT(*) FROM " + transducerTableString + "\
                             WHERE TX_SN = '" + TX_SN + "') = 0               \
                            INSERT INTO  " + transducerTableString + "        \
                           (TX_SN) VALUES ('" + TX_SN + "')")
               
    def _getDatabaseContents(self, dbPath):
        """Takes a .bak file-path and returns a database contents list."""

        cursor = self.cursor    
    
        cursor.execute("RESTORE FILELISTONLY FROM DISK='" + dbPath + "'")
        
        components = []
        
        while 1:
            row = cursor.fetchone()
            if not row:
                break
            
            components.append((row.LogicalName,row.Type))
        
        return components
          
    def _restoreDatabase(self, path, dbName, dbComponents):
        """ Restures a .bak file to lighthouse, decrypt if encrypted."""
            
        serverDataPath = self.serverDataPath    
        cipherPath = self.cipherPath        
        
        moveStrings = ["MOVE '" + comp[0] + "' TO '" + serverDataPath + "\\" + dbName + "_" + comp[0] + (".mdf" if comp[1] == 'D' else ".ldf") + "'" for comp in dbComponents]
        
        print('Restoring DB')
        
        cursor = self.cursor        
        
        cursor.execute("RESTORE DATABASE " + dbName + " FROM DISK='" + path + "' WITH " + ",".join(moveStrings))
    
        time.sleep(3) # Restore database is an async operation.  Should be checking for completeness of restore.
                      # Hacky sloution, but good enough.
    
        # Try to decrypt db - will do nothing if unnecessary
        x=subprocess.run([cipherPath, '-p', 'c1ph3r', '-d', '-s', 'lighthouse', '-n', dbName], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
        if x.returncode == 0:
          print("\t"+x.stdout.decode("utf-8"))
          if 'Unable to proceed' in x.stdout.decode("utf-8"):
              raise Exception('Error with cipher.  (Known not to load drivers properly if pyCyote is run from Lighthouse.)  Not decrypted.  Stopping.')
        else:
          print("\tError code: " + str(x.returncode))
          print("\t"+x.stderr.decode("utf-8"))
    
        sys.stdout.flush()

    def dbExistsWithDBId(self, DBId):
        """ Boolean test for whether a database in the merged set include one with
            DatabaseId == DBId """
        self.cursor.execute("SELECT databaseId FROM "+ self.databaseTableString + "\
                              WHERE databaseId = '" + DBId + "'")
        rows = self.cursor.fetchall()
       
        if len(rows) > 0:
            return True
        
        return False
        
    def dbExistsWithDetails(self, TSN, MSN, ISN, Type, Style, Version):
        """ Boolean test for whether a database in the merged set include one with
            the exact combination of details given as argument """
            
        self.cursor.execute("SELECT databaseId FROM "+ self.databaseTableString + "\
                              WHERE        TX_SN  = '" + TSN     + "' \
                                AND        MC_SN  = '" + MSN     + "' \
                                AND Instrument_SN = '" + ISN     + "' \
                                AND DatabaseType  = '" + Type    + "' \
                                AND DatabaseStyle = '" + Style   + "' \
                                AND       Version = '" + Version + "'")
                                 
        rows = self.cursor.fetchall()
       
        if len(rows) > 0:
            return True
        
        return False

    def addTransducerDB(self, pathToBak, TSN, MSN, ISN, Type, Style, Version):
        """ Pulls transducer's .bak database into Lighthouse as a discrete database 
            and merges it into 'Bonita', the merged databse, for subsequent analysis.
            It computes a md5 fingerprint of the .bak file and stores thast in the mergeDB.
            This allows it to prevent duplicate data form being uploaded.  It also won't
            upload a new set unless the descriptive arguments provided are unique.
            
            Arguments:
             pathToBak - path on the network filesystem where the .bak file resides
                         Must be a path that starts with '\\'  (rather than q:\).
                         Not sensitive to slash direction.
                   TSN - Transducer's serial number e.g. 'E1020_TX1008605_MC0000004_20160303.bak'
                   MSN - Matching circuit serial number e.g. 'MC0506229'
                   ISN - Instrument serial number e.g. 'E1020'
                  Type - Something like 'calibration' or 'instaliation'
                 Style - Something note-like 'opt', or 'Test_Recal_Red
               Version - Something like 2.1 which classifies a calibration process
            
            Returns: md5 DatabaseId """
    
        path = os.path.normpath(pathToBak)
    
        self._initializeTxDBIfMissing()
        
        try:
            md5=(hashlib.md5(open(path, 'rb').read()).hexdigest())
        except:
            raise Exception('Something is wrong with your path.  Is the file '
                 +'really there?  Could you have escape characters like \\t in it? '
                 +'If so, make your path string raw like --> r"\\parentDir\\tacoFolder" ') 
        
        DBNameToBeMerged = TSN + '_' + MSN + '_' + ISN + '_' + md5
        
        print('Database will be called: ' + DBNameToBeMerged)   
        
        ## Check for whether we have a merged database with the same MD5 already - i.e. already uploaded
        if self.dbExistsWithDBId(md5):
           raise Exception("Database "+md5+" is already present in "+self.mergeDBName+'.') 
           
        ## Check for whether human has provided a unique combination of descriptive fields.    
        details = [TSN, MSN, ISN, Type, Style, Version]
        
        if self.dbExistsWithDetails(*details):
           raise Exception("Descriptive field ("+ " ".join(details) +") combination already present in "+self.mergeDBName+'.') 
    
        self._addTxToGlobalTransducersIfMissing(TSN)
    
        self._addTxToGlobalInstrumentIfMissing(ISN)
        
        print("Adding " + md5 + "... ", end='')
        
        dbComponents = self._getDatabaseContents(path)
        
        self._restoreDatabase(path, DBNameToBeMerged, dbComponents)
        
        mergeTransducerDB.merge(DBNameToBeMerged, md5, path, *details)
        
        return md5

    def deleteTransducerDBById(self, DBId):
        """Deletes a database (and all rows from source tables) with DatabaseId = DBId"""

        if self.dbExistsWithDBId(DBId):
             print('Database with Id=' + DBId + ' exists.  Deleting... ',end='', flush=True)             
             self.cursor.execute("DELETE \
                                    FROM "+ self.databaseTableString + " \
                                   WHERE DatabaseId = '" + DBId + "'")
             print('done.')
        else:
            errorString = 'Database with Id = ' + DBId + ' not found.'
            raise Exception(errorString) 

    def deleteTransducerDBByDetails(self, TSN, MSN, ISN, Type, Style, Version):
        """Deletes a database (and all rows from source tables) with discriptive details
           matching those given."""
        
        details = [TSN, MSN, ISN, Type, Style, Version]
        
        if self.dbExistsWithDetails(*details):
            print('Database with details: ' + ' '.join(details) + ' exists.  Deleting... ',end='', flush=True)             
            self.cursor.execute("DELETE FROM "+ self.databaseTableString + "\
                                  WHERE      TX_SN  = '" + TSN     + "' \
                                  AND        MC_SN  = '" + MSN     + "' \
                                  AND Instrument_SN = '" + ISN     + "' \
                                  AND DatabaseType  = '" + Type    + "' \
                                  AND DatabaseStyle = '" + Style   + "' \
                                  AND       Version = '" + Version + "'" )                                  
            print('done.')
        else:
            errorString = 'Database with details: ' + ' '.join(details) + ' not found.'
            raise Exception(errorString) 
