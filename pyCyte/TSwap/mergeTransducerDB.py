# -*- coding: utf-8 -*-
import sys
import sqlalchemy
import pprint as pp

# Written by Josh Rubin for Labcyte

# The database needs to already exist.  SQL Server refuses to
# allow aqlchemy to CREATE DATABASE in a multi-statement session
# which is apperently what it does by default (or can be easily
# made to do).
# So Specify the name of the destination database here.

mergeDBName   = "Bonita"

# strings to represent special tables
databasesTableName       = "globalDatabases"
databasesTableString    = mergeDBName + ".dbo." + databasesTableName

####
# Shortcut for simple queries that return nothing. Can be used for weird cases
# were SQL Server requires transactional stuff.
def commitDBQuery(query) :
    trans = conn.begin()
    conn.execute(query)
    trans.commit()

####
# lighthouseODBC needs to be defined in Start->Administrative Tools->Data Sources for Windows.
# No additional login credentials were necessary beyond being logged in to the labcyte domain.
####

conn = sqlalchemy.create_engine("mssql+pyodbc://lighthouseODBC").connect()

####
# Retrurn metadata describing the contents of database dbName
# Returns a dict(tableName, dict(columnName, dict{rowDetail(type|size)}))
def unpackDatabaseInfo(dbName):
    DBInfo = {}  

    result = conn.execute("SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH FROM " + dbName + ".INFORMATION_SCHEMA.COLUMNS")

    # Unpack all the tables and columns in the new DB
    for row in result:
        if row["TABLE_NAME"] not in DBInfo:
            DBInfo[row["TABLE_NAME"]] = {}
        if row["COLUMN_NAME"] not in DBInfo[row["TABLE_NAME"]]:
            DBInfo[row["TABLE_NAME"]][row["COLUMN_NAME"]] = {}
        DBInfo[row["TABLE_NAME"]][row["COLUMN_NAME"]] = {"DATA_TYPE":row["DATA_TYPE"], "CHARACTER_MAXIMUM_LENGTH":row["CHARACTER_MAXIMUM_LENGTH"]} 
        
    return DBInfo

def merge(DBNameToBeMerged, DatabaseId, path, TXN, MSN, ISN, Type, Style, Version):

    newDBInfo     = unpackDatabaseInfo(DBNameToBeMerged)
    mergedDBInfo  = unpackDatabaseInfo(mergeDBName)
   
    q = "INSERT INTO " + databasesTableString + " (DatabaseId, TX_SN, MC_SN, Instrument_SN, OriginalPath,  UploadDate, SourceDatabase, DatabaseType, DatabaseStyle, Version) VALUES \
    ('"+ DatabaseId +"','"+ TXN + "','" + MSN + "','"+ISN+"','" + path + "' , GETDATE(), '"+ DBNameToBeMerged +"','"+Type+"','"+Style+"','"+Version+"')"
    
    commitDBQuery(q)

    print("Adding data from "+ DBNameToBeMerged + " to " + mergeDBName + "...")

    ####
    # Look for any tables and fields present in newDB, but missing in merged.
    # If any are found, add them... with appropriate types and indeces before.
    # inserting new data
    ####
    
    tablesToAddToMerge = list(set(list(newDBInfo.keys()))-set(list(mergedDBInfo.keys())))
    
    for table in tablesToAddToMerge:
        print("Creating table: " + table)  
    
        commitDBQuery("CREATE TABLE " + mergeDBName + ".dbo." + table + " (DatabaseId  NCHAR(32),    \
                                                                      TX_SN  NCHAR(32),    \
                                                              Instrument_SN  NCHAR(32),    \
                                                                      MC_SN  NCHAR(32),    \
                                                               DatabaseType  VARCHAR(MAX), \
                                                              DatabaseStyle  VARCHAR(MAX), \
                                                                    Version  VARCHAR(MAX)) ")
    
        # ...and index them           
        commitDBQuery("CREATE CLUSTERED INDEX Index_"+table+"_Databases ON " + mergeDBName + ".dbo." + table + " (DatabaseId)")
    
       
        # Now add foreign key constraints...
        commitDBQuery("ALTER TABLE "+ mergeDBName + ".dbo." + table + " ADD CONSTRAINT FK_"+table+"_Databases FOREIGN KEY (DatabaseId) \
               REFERENCES " + databasesTableString + " (DatabaseId) \
               ON DELETE CASCADE \
               ON UPDATE CASCADE")
    

    # We've added tables, update list
    mergedDBInfo  = unpackDatabaseInfo(mergeDBName)
    
    # Now we need to add any missing filds to tables in the merged set.
    for table, field in newDBInfo.items():
       print("\nTable: " + table)
       fieldsToAddToMerge = list(set(newDBInfo[table].keys())-set(mergedDBInfo[table].keys()))
       for missingField in fieldsToAddToMerge:
             idFieldString = ""
             if missingField == (table + "Id") :
             #    idFieldString = " IDENTITY(1,1) "
                 idFieldString = ""
             sizeString = ""
             if newDBInfo[table][missingField]["CHARACTER_MAXIMUM_LENGTH"] and newDBInfo[table][missingField]["DATA_TYPE"] != "text":
                 sizeString = "(" + str(newDBInfo[table][missingField]["CHARACTER_MAXIMUM_LENGTH"]) +")"
         
             print("\tAdding field " + missingField + " " + newDBInfo[table][missingField]["DATA_TYPE"] + sizeString)
             commitDBQuery(    "ALTER TABLE " + mergeDBName + ".dbo." + table + " ADD " + missingField + " " + newDBInfo[table][missingField]["DATA_TYPE"] + sizeString + " " + idFieldString)
         
       # Now insert new tables into merged...
       fields = ", ".join(list(newDBInfo[table].keys()))
    
       print( "\tInserting: "+ DBNameToBeMerged + ".dbo." + table)
       commitDBQuery( " INSERT INTO " + mergeDBName + ".dbo." + table + " (DatabaseId, TX_SN, Instrument_SN, MC_SN, DatabaseType, DatabaseStyle, Version,\
            " + fields + ") SELECT '" + DatabaseId + "', '"+ TXN + "', '"+ ISN + "', '"+ MSN + "', '"+ Type + "', '"+ Style + "', '"+ Version + "', " + fields + " FROM " + DBNameToBeMerged + ".dbo." + table)
