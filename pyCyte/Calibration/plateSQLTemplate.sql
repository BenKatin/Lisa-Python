SET NOCOUNT ON

<VariableDefinitions>

DECLARE @NextPriority INT

IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE 'Secure%')
	BEGIN
	PRINT('Database has secure tables.  Decrypted destination database required.  Exiting without making changes.')
	RETURN
	END

IF EXISTS (SELECT * FROM PlateClassification WHERE PlateTypeName = @ClassifiedName) OR EXISTS (SELECT * FROM PlateType WHERE PlateTypeName = @ClassifiedName)
	BEGIN
	PRINT('There''s already a classified plate named "' + @ClassifiedName + '" on this instrument.  Exiting without making changes.')
	RETURN
	END

IF EXISTS (SELECT * FROM PlateClassification WHERE UnclassifiedName = @UnclassifiedName AND Analysis = @PCAnalysis AND Measurement = @PCMeasurement )
	BEGIN
	PRINT('Plate with UnclassifiedName '''+@UnclassifiedName+''' already exists with Analysis ''' + @PCAnalysis + ''' and Measurement ''' + @PCMeasurement + '''.  Please make classification details for new plate distinct, or delete similar classified plate.  Exiting without making changes.')
	RETURN
	END	
	
SELECT @NextPriority = MAX(Priority)+1 FROM PlateClassification WHERE UnclassifiedName = @UnclassifiedName

IF @NextPriority IS NOT NULL  
	PRINT('Adding additional plate to existing unclassified plate, ' + @UnclassifiedName + ' at next available priority ' + CAST(@NextPriority AS VARCHAR(8))+'.' )
ELSE
	BEGIN
	PRINT('Creating unclassified and classified plates in PlateClassification')
		IF EXISTS (SELECT * FROM PlateType WHERE PlateTypeName = @UnclassifiedName) 
		BEGIN
		PRINT('Can''t create unclassified plate "' + @UnclassifiedName + '" - already exists in PlateType.  Exiting without making changes.')
		RETURN
		END
	<UnclassifiedPlateDetails>
	END

INSERT INTO PlateClassification
            (   InstrumentName,   TransducerName,   PlateTypeName,  UnclassifiedName,    Analysis,    PlateFormFactor, Measurement,   Priority)
     VALUES (@PCInstrumentName,@PCTransducerName, @ClassifiedName, @UnclassifiedName, @PCAnalysis, @PCPlateFormFactor,@PCMeasurement, COALESCE(@NextPriority,1))
	

IF @PCMeasurement IS NOT NULL AND NOT EXISTS (SELECT * FROM PlateType WHERE PlateTypeName = @PCMeasurement)
	BEGIN
	PRINT('Adding classification measurement plate, ' + @PCMeasurement)
	<MeasurementPlateDetails>
	END

IF @PCAnalysis IS NOT NULL AND NOT EXISTS (SELECT * FROM PlateType WHERE PlateTypeName = @PCAnalysis)
	BEGIN
	PRINT('Adding classification analysis plate, ' + @PCAnalysis)
	<AnalysisPlateDetails>
	END
	
<MainPlateDetails>

IF (SELECT COUNT(*) FROM D2AMemory WHERE Waveform = '<D2AMemoryWaveform>') != 0
	PRINT('D2AMemory waveform "<D2AMemoryWaveform>" already exists.  No need to insert.')
ELSE
	BEGIN
	
    DECLARE @FreeMemoryAddress INT
   
    SELECT @FreeMemoryAddress = MAX(MemoryAddress) + 1 FROM D2AMemory WHERE MemoryAddress < 80
    
    PRINT('Inserting new waveform at available memory address ' + CAST(@FreeMemoryAddress AS VARCHAR(4)) + '.')

 	<D2AMemoryDetails>
	END

