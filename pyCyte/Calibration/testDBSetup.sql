SET NOCOUNT ON
GO

:setvar DBName "TestDB_InsertPlates"
:setvar DBPath "C:\E1211_RED_decrypted.bak"
:setvar PlateTypeName "'384PPL_AQ_CP'"
:setvar PlateTypeName2 "'384PPG_AQ_CP'"

:setvar PlateTypeName3 "'384PP_AQ_CP'"

PRINT('Restoring $(DBPath) to database $(DBName)')

PRINT('')

USE Master
   -- Ensure neither database exists before restoring.
   IF DB_ID('$(DBName)') IS NOT NULL EXEC msdb.dbo.sp_delete_database_backuphistory @database_name = N'$(DBName)'

   IF DB_ID('$(DBName)') IS NOT NULL ALTER DATABASE $(DBName) SET SINGLE_USER WITH ROLLBACK IMMEDIATE

   IF DB_ID('$(DBName)') IS NOT NULL DROP DATABASE $(DBName)
   GO

/***************************************************************************   
**  This is how you find SQL Server 2008's default data directory so that you
**  can restore a .bak to a new name on a new database server... which 
**  is appalling.  From http://stackoverflow.com/questions/1883071
*/
declare @DefaultData nvarchar(512)

PRINT('=== Please ignore "Error 2" below.  JR. ===')

-- This throws an error if no reg-key is available.  'RegQueryValueEx() returned error 2'  Unable to suppress.  Maybe we don't actually need this line.
exec master.dbo.xp_instance_regread N'HKEY_LOCAL_MACHINE', N'Software\Microsoft\MSSQLServer\MSSQLServer', N'DefaultData', @DefaultData output

declare @MasterData nvarchar(512)
exec master.dbo.xp_instance_regread N'HKEY_LOCAL_MACHINE', N'Software\Microsoft\MSSQLServer\MSSQLServer\Parameters', N'SqlArg0', @MasterData output
select @MasterData=substring(@MasterData, 3, 255)
select @MasterData=substring(@MasterData, 1, len(@MasterData) - charindex('\', reverse(@MasterData)))

declare @DataDir nvarchar(512) = isnull(@DefaultData,  @MasterData)

PRINT('')

/****************************************************************************/


/***************************************************************************   
**  Similarly appalling is that to restore a database with aribitrarily named
**  logical components inside (like ususally 'MEDMANdb', but occationally 'MEDMAN'),
**  we need to store the output of 'RESTORE FILELISTONLY' to a table so that 
**  we can then query it for specific LogicalName fields.
**  http://stackoverflow.com/questions/2511502 was helpful.
*/
DECLARE @tempDBInfo TABLE
(
    LogicalName          NVARCHAR(128),
    PhysicalName         NVARCHAR(260),
    [Type]               CHAR(1),
    FileGroupName        NVARCHAR(128),
    Size                 NUMERIC(20,0),
    MaxSize              NUMERIC(20,0),
    FileID               BIGINT,
    CreateLSN            NUMERIC(25,0),
    DropLSN              NUMERIC(25,0),
    UniqueID             UNIQUEIDENTIFIER,
    ReadOnlyLSN          NUMERIC(25,0),
    ReadWriteLSN         NUMERIC(25,0),
    BackupSizeInBytes    BIGINT,
    SourceBlockSize      INT,
    FileGroupID          INT,
    LogGroupGUID         UNIQUEIDENTIFIER,
    DifferentialBaseLSN  NUMERIC(25,0),
    DifferentialBaseGUID UNIQUEIDENTIFIER,
    IsReadOnl            BIT,
    IsPresent            BIT,
    TDEThumbprint        VARBINARY(32)
)

/****************************************************************************/   

DECLARE @DBLogicalDataName  VARCHAR(16)
DECLARE @DBLogicalLogName   VARCHAR(16)

/** Restore local/src database to SQL Server **/
PRINT('$(DBPath)')
INSERT INTO @tempDBInfo EXEC('RESTORE FILELISTONLY FROM DISK = ''$(DBPath)''')

SELECT @DBLogicalDataName=d.LogicalName, @DBLogicalLogName=l.LogicalName FROM
(SELECT * FROM @tempDBInfo WHERE Type = 'D') d,
(SELECT * FROM @tempDBInfo WHERE Type = 'L') l

DECLARE @SrcDataPath  nvarchar(512) = @DataDir + '\$(DBName)'
DECLARE @SrcLogPath   nvarchar(512) = @DataDir + '\$(DBName)_log'

RESTORE DATABASE $(DBName) FROM DISK='$(DBPath)'
   WITH REPLACE,
        MOVE @DBLogicalDataName TO @SrcDataPath,
        MOVE @DBLogicalLogName  TO @SrcLogPath        

-- Used when restoring the database to check for database complete (i.e. 0 rather than 1 or 2)
DECLARE @state INTEGER

-- Pause until async restore process complete
SELECT @state=state FROM sys.databases WHERE name = '$(DBName)'
WHILE (@state != 0)
BEGIN
	WAITFOR DELAY '00:00:00.500'
	SELECT @state=state FROM sys.databases WHERE name = '$(DBName)'
END

PRINT('Restore complete.  $(DBName) is available.')
PRINT(' ')

DELETE FROM @tempDBInfo

GO

USE $(DBName)

IF EXISTS (
  SELECT * 
  FROM sys.objects 
  WHERE object_id = OBJECT_ID('removePlateEntries') AND type in ('P'))
BEGIN
  DROP PROCEDURE copyTable
END

GO

CREATE PROCEDURE removePlateEntries
    @TableName nvarchar(50)
AS
	DECLARE @cmd NVARCHAR(MAX)
	
	SET @cmd = 'IF (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '''+@TableName+''') > 0
   	            DELETE FROM ' + @TableName + ' WHERE PlateTypeName = '''+$(PlateTypeName)+''''
		
	EXEC(@cmd)
	PRINT('Removing '''+$(PlateTypeName)+''' from ' + @TableName + ': ' + LTRIM(STR(@@ROWCOUNT)) + ' row(s) deleted.')
GO

DELETE p
  FROM Protocol p,
       PlateType pt
 WHERE p.SourcePlateTypeId = pt.PlateTypeId
   AND pt.PlateTypeName = $(PlateTypeName)

PRINT('Removing ' + LTRIM(STR(@@ROWCOUNT)) + ' protocols with SourcePlate: '''+$(PlateTypeName)+'''')

EXEC removePlateEntries @TableName = 'PlateType';
EXEC removePlateEntries @TableName = 'Coefficient';
EXEC removePlateEntries @TableName = 'LUT';
EXEC removePlateEntries @TableName = 'LUT2D';
EXEC removePlateEntries @TableName = 'Parameter';
EXEC removePlateEntries @TableName = 'MIPConfiguration';
EXEC removePlateEntries @TableName = 'PingParameters';
EXEC removePlateEntries @TableName = 'PlateRegistration';
EXEC removePlateEntries @TableName = 'PlateSignature';
EXEC removePlateEntries @TableName = 'ReferenceWaveforms';
EXEC removePlateEntries @TableName = 'TransferVolume';
EXEC removePlateEntries @TableName = 'WellAdjustment';
EXEC removePlateEntries @TableName = 'SystemEvents';
EXEC removePlateEntries @TableName = 'PowerSweep';
EXEC removePlateEntries @TableName = 'PlateClassification';

DROP PROCEDURE removePlateEntries




GO


CREATE PROCEDURE removePlateEntries
    @TableName nvarchar(50)
AS
	DECLARE @cmd NVARCHAR(MAX)
	
	SET @cmd = 'IF (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '''+@TableName+''') > 0
   	            DELETE FROM ' + @TableName + ' WHERE PlateTypeName = '''+$(PlateTypeName2)+''''
		
	EXEC(@cmd)
	PRINT('Removing '''+$(PlateTypeName2)+''' from ' + @TableName + ': ' + LTRIM(STR(@@ROWCOUNT)) + ' row(s) deleted.')
GO

DELETE p
  FROM Protocol p,
       PlateType pt
 WHERE p.SourcePlateTypeId = pt.PlateTypeId
   AND pt.PlateTypeName = $(PlateTypeName2)

PRINT('Removing ' + LTRIM(STR(@@ROWCOUNT)) + ' protocols with SourcePlate: '''+$(PlateTypeName2)+'''')

EXEC removePlateEntries @TableName = 'PlateType';
EXEC removePlateEntries @TableName = 'Coefficient';
EXEC removePlateEntries @TableName = 'LUT';
EXEC removePlateEntries @TableName = 'LUT2D';
EXEC removePlateEntries @TableName = 'Parameter';
EXEC removePlateEntries @TableName = 'MIPConfiguration';
EXEC removePlateEntries @TableName = 'PingParameters';
EXEC removePlateEntries @TableName = 'PlateRegistration';
EXEC removePlateEntries @TableName = 'PlateSignature';
EXEC removePlateEntries @TableName = 'ReferenceWaveforms';
EXEC removePlateEntries @TableName = 'TransferVolume';
EXEC removePlateEntries @TableName = 'WellAdjustment';
EXEC removePlateEntries @TableName = 'SystemEvents';
EXEC removePlateEntries @TableName = 'PowerSweep';
EXEC removePlateEntries @TableName = 'PlateClassification';

DROP PROCEDURE removePlateEntries





GO


CREATE PROCEDURE removePlateEntries
    @TableName nvarchar(50)
AS
	DECLARE @cmd NVARCHAR(MAX)
	
	SET @cmd = 'IF (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '''+@TableName+''') > 0
   	            DELETE FROM ' + @TableName + ' WHERE PlateTypeName = '''+$(plateTypeName3)+''''
		
	EXEC(@cmd)
	PRINT('Removing '''+$(plateTypeName3)+''' from ' + @TableName + ': ' + LTRIM(STR(@@ROWCOUNT)) + ' row(s) deleted.')
GO

DELETE p
  FROM Protocol p,
       PlateType pt
 WHERE p.SourcePlateTypeId = pt.PlateTypeId
   AND pt.PlateTypeName = $(plateTypeName3)

PRINT('Removing ' + LTRIM(STR(@@ROWCOUNT)) + ' protocols with SourcePlate: '''+$(plateTypeName3)+'''')

EXEC removePlateEntries @TableName = 'PlateType';
EXEC removePlateEntries @TableName = 'Coefficient';
EXEC removePlateEntries @TableName = 'LUT';
EXEC removePlateEntries @TableName = 'LUT2D';
EXEC removePlateEntries @TableName = 'Parameter';
EXEC removePlateEntries @TableName = 'MIPConfiguration';
EXEC removePlateEntries @TableName = 'PingParameters';
EXEC removePlateEntries @TableName = 'PlateRegistration';
EXEC removePlateEntries @TableName = 'PlateSignature';
EXEC removePlateEntries @TableName = 'ReferenceWaveforms';
EXEC removePlateEntries @TableName = 'TransferVolume';
EXEC removePlateEntries @TableName = 'WellAdjustment';
EXEC removePlateEntries @TableName = 'SystemEvents';
EXEC removePlateEntries @TableName = 'PowerSweep';
EXEC removePlateEntries @TableName = 'PlateClassification';

DROP PROCEDURE removePlateEntries

