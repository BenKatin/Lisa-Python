SET NOCOUNT ON

USE MEDMANdb

DECLARE @UnclassifiedName VARCHAR(MAX) = '96PPR_AQ_SP_High'
DECLARE @ClassifiedName   VARCHAR(MAX) = '96PPRE_AQ_SP_High'

-- Details for updating plate classification.
DECLARE @PCAnalysis        VARCHAR(MAX) = NULL
DECLARE @PCMeasurement     VARCHAR(MAX) = NULL
DECLARE @PCInstrumentName  VARCHAR(MAX) = 'MEDMAN'
DECLARE @PCTransducerName  VARCHAR(MAX) = 'Transducer10MHz'
DECLARE @PCPlateFormFactor VARCHAR(MAX) = '96PP'

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
	

INSERT INTO PingParameters (InstrumentName, PlateTypeName, TransducerName, Amplitude, TOFWindowStart, TOFWindowEnd, EchoThreshMult, FileName)
VALUES 
('MEDMAN', @UnclassifiedName, 'Transducer10MHz', 0.2, 29.28054, 45.66454, 15.0, 'PingBurst')
PRINT(LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into PingParameters for PlateType: "'+@UnclassifiedName+'".')



INSERT INTO PlateType (PlateTypeName, InstrumentName, Manufacturer, LotNumber, PartNumber, BarcodeLocation, Rows, Columns, BootstrapWell, BootstrapZ, SurveyToFRatio, A1OffsetX, A1OffsetY, SkirtHeight, CenterWell, CenterX, CenterY, PlateHeight, WellWidth, WellLength, XWellSpacing, YWellSpacing, WellCapacity, SoundVelocity, BottomInset, PlateUse, PlateFormat, Fluid, BottomThickness, ThicknessTolerance, IsDeleted, ParentPlate)
VALUES 
(@UnclassifiedName, 'MEDMAN', 'Quanti', '1', 'A2', 'None', 8, 12, 'F3', 16000.0, 0.86, 14380.0, 11230.0, 7410.0, 'D6', 102825.0, 43041.0, 14500.0, 8200.0, 8200.0, 9000.0, 9000.0, 1000.0, 2860.0, 2.1, 'SRC', '96PP', 'AQ', 0.0, 0.0, 0, NULL)
PRINT(LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into PlateType for PlateType: "'+@UnclassifiedName+'".')



INSERT INTO TransferVolume (InstrumentName, PlateTypeName, TransducerName, ResolutionNl, MinimumNl, MaxVolumeTotalNl, IncrNl, MaxAllowableVolumeDeltaNl, MinWellVolumeUL, MaxWellVolumeUL, MinFluidThicknessMM, FileName, Configuration)
VALUES 
('MEDMAN', @UnclassifiedName, 'Transducer10MHz', 25.0, 25.0, 320000.0, 25.0, 2000.0, 50.0, 350.0, 0.2, 'ToneX_25nl_3seg_1pt1chirp.cfg', '# This file was modified automatically on Fri Jan 21 13:53:55 2011
#
# 2.5nl Toneburst config file
#
# This file contains parameters that define the 2.5nl toneburst used by the system.
#
# See FluidTransfer::config() for mapping in source code
#
# $Id: //depot/main/Pico/Medman/conf/server/ToneX_0pt8.cfg#1 $
#

:GENERAL

Segment		INT		99
Type		STRING		"X" # if X, then see below

# If toneburst type is not X, then we don''t need to specify
# the start/end frequencies and amplitude as the actual printing
# values come from the LUT.
# If toneburst type is not X, then we need to specify the 
# toneburst length, as follows:
# Length	FLOAT		180  # only applicable when not Tone X

:TONEBURST_X

# You need to define a configuration set for each segment.  For example,
# if # segments is 3, then you *must* define configuration sets SEGMENT1,
# SEGMENT2, and SEGMENT3.  Failure to do so is a catastrophic error.
NumSegments		INT		3

:SEGMENT1
Type		STRING		"G10"
FrequencyChirpWidth		FLOAT		1.1 # MHz

:SEGMENT2
Type		STRING		"Z"

:SEGMENT3
Type		STRING		"G6"
FrequencyChirpWidth		FLOAT		1.1 # MHz')
PRINT(LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into TransferVolume for PlateType: "'+@UnclassifiedName+'".')



INSERT INTO PlateRegistration (RegistrationDate, InstrumentName, TransducerName, PlateTypeName, CenterWell, CenterX, CenterY, XWellSpacing, YWellSpacing)
VALUES 
('2018-04-27 12:09:00', 'MEDMAN', 'Transducer10MHz', @UnclassifiedName, 'D6', 102825.0, 43041.0, 9000.0, 9000.0)
PRINT(LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into PlateRegistration for PlateType: "'+@UnclassifiedName+'".')


	END

INSERT INTO PlateClassification
            (   InstrumentName,   TransducerName,   PlateTypeName,  UnclassifiedName,    Analysis,    PlateFormFactor, Measurement,   Priority)
     VALUES (@PCInstrumentName,@PCTransducerName, @ClassifiedName, @UnclassifiedName, @PCAnalysis, @PCPlateFormFactor,@PCMeasurement, COALESCE(@NextPriority,1))
	

IF @PCMeasurement IS NOT NULL AND NOT EXISTS (SELECT * FROM PlateType WHERE PlateTypeName = @PCMeasurement)
	BEGIN
	PRINT('Adding classification measurement plate, ' + @PCMeasurement)
	
	END

IF @PCAnalysis IS NOT NULL AND NOT EXISTS (SELECT * FROM PlateType WHERE PlateTypeName = @PCAnalysis)
	BEGIN
	PRINT('Adding classification analysis plate, ' + @PCAnalysis)
	
	END
	


INSERT INTO Coefficient (CoefficientName, InstrumentName, TransducerName, PlateTypeName, Description, A, B, C, D, E)
VALUES 
('CoeffAInMRayl', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'y = Ax^2 + Bx+C', 0.0, 0.0, -1.08, NULL, NULL),
('CoeffBInMRayl', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'y = Ax^2 + Bx+C', 0.0, 0.0, -0.83, NULL, NULL)
PRINT(LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into Coefficient for PlateType: "'+@ClassifiedName+'".')



INSERT INTO LUT (LUTName, InstrumentName, TransducerName, PlateTypeName, Volume, Description, X, Y)
VALUES 
('ImpedCorrectionvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.453, 1.0),
('ImpedCorrectionvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 1.895, 1.0),
('ImpedCorrectionvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 2.219, 1.0),
('ImpedCorrectionvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 3.478, 1.0),
('ToneX_Width_us', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '1', 1.47, 275.0),
('ToneX_Width_us', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '1', 1.49, 275.0),
('ToneX_Width_us', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '2', 1.47, 130.0),
('ToneX_Width_us', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '2', 1.49, 130.0),
('ToneX_Width_us', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '3', 1.47, 100.0),
('ToneX_Width_us', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '3', 1.49, 100.0),
('AmpvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, NULL, 0.453, 1.6),
('AmpvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, NULL, 1.419, 1.6),
('AmpvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, NULL, 1.485, 1.6),
('AmpvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, NULL, 1.598, 1.6),
('AmpvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, NULL, 1.718, 1.6),
('AmpvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, NULL, 1.843, 1.6),
('AmpvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, NULL, 1.905, 1.6),
('FrequencyvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, NULL, 0.453, 12.3),
('FrequencyvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, NULL, 1.734, 12.3),
('FrequencyvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, NULL, 1.895, 12.3),
('FrequencyvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, NULL, 2.057, 12.3),
('FrequencyvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, NULL, 2.219, 12.3),
('FrequencyvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, NULL, 2.382, 12.3),
('FrequencyvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, NULL, 3.478, 12.3),
('ToneX_RelAmp', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '1', 1.47, 0.95),
('ToneX_RelAmp', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '1', 1.49, 0.95),
('ToneX_RelAmp', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '3', 1.47, 0.65),
('ToneX_RelAmp', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '3', 1.49, 0.65),
('ToneX_CF_MHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '1', 1.47, 6.85),
('ToneX_CF_MHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '1', 1.49, 6.85),
('ToneX_CF_MHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '3', 1.47, 6.165),
('ToneX_CF_MHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '3', 1.49, 6.165),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8409277561457787, 2.392578125),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8416954229201848, 2.4091796875),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8425179454470673, 2.4287109375),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8433404156805726, 2.439453125),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8442177939599314, 2.4482421875),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8450402641934367, 2.4580078125),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8459724459318946, 2.466796875),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8468497719178762, 2.4677734375),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.847727150197235, 2.474609375),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8486044761832167, 2.4794921875),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8494818021691983, 2.4892578125),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.85035912815518, 2.4951171875),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8512913098936379, 2.5068359375),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8521686358796196, 2.5078125),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8530459618656012, 2.513671875),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8539781436040592, 2.525390625),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8548554695900409, 2.53125),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8557327955760226, 2.54296875),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8566101215620042, 2.5439453125),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8575423033004622, 2.5556640625),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8584744850389201, 2.5634765625),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8593518110249018, 2.5791015625),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8602291370108834, 2.5869140625),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8611613187493414, 2.595703125),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8620386447353231, 2.6103515625),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8629708264737811, 2.625),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8638481524597628, 2.6279296875),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8647803341982206, 2.6513671875),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8656576601842023, 2.65625),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8665898419226603, 2.6796875),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8675220236611183, 2.6884765625),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8684542053995762, 2.7138671875),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8693315313855579, 2.72265625),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8703185165831151, 2.7451171875),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8712506983215731, 2.7626953125),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8721828800600311, 2.7822265625),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8730602060460128, 2.806640625),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.874047243536947, 2.830078125),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8749245695229286, 2.8564453125),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8759115547204859, 2.8876953125),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8767888807064675, 2.9140625),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8777759181974019, 2.943359375),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8409277561457787, 2.328125),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8416954229201848, 2.35546875),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8425179454470673, 2.3935546875),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8433404156805726, 2.4150390625),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8442177939599314, 2.439453125),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8450402641934367, 2.46484375),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8459724459318946, 2.4912109375),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8468497719178762, 2.505859375),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.847727150197235, 2.5361328125),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8486044761832167, 2.55078125),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8494818021691983, 2.580078125),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.85035912815518, 2.6005859375),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8512913098936379, 2.626953125),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8521686358796196, 2.65234375),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8530459618656012, 2.673828125),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8539781436040592, 2.697265625),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8548554695900409, 2.7255859375),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8557327955760226, 2.7470703125),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8566101215620042, 2.7685546875),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8575423033004622, 2.8037109375),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8584744850389201, 2.8212890625),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8593518110249018, 2.849609375),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8602291370108834, 2.8779296875),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8611613187493414, 2.9111328125),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8620386447353231, 2.93359375),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8629708264737811, 2.96875),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8638481524597628, 2.9921875),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8647803341982206, 3.033203125),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8656576601842023, 3.056640625),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8665898419226603, 3.091796875),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8675220236611183, 3.115234375),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8684542053995762, 3.1533203125),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8693315313855579, 3.1796875),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8703185165831151, 3.2080078125),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8712506983215731, 3.2431640625),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8721828800600311, 3.2744140625),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8730602060460128, 3.3046875),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.874047243536947, 3.3271484375),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8749245695229286, 3.3583984375),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8759115547204859, 3.392578125),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8767888807064675, 3.416015625),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8777759181974019, 3.4482421875)
PRINT(LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into LUT for PlateType: "'+@ClassifiedName+'".')



INSERT INTO LUT2D (LUT2DName, InstrumentName, TransducerName, PlateTypeName, Volume, Description, X, Y, Z)
VALUES 
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.48, 0.0, 0.0),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.48, 0.928, 50.0),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.48, 4.967, 200.0),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.48, 7.648, 300.0),
('MaxRepRateHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'f(%DMSO;fluidHeight)', 1.48, 0.2, 200.0),
('MaxRepRateHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'f(%DMSO;fluidHeight)', 1.48, 6.5, 200.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.48, 1.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.48, 2.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.48, 3.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.48, 4.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.48, 5.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.48, 6.5, 0.0),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 0.2, 2.22),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 1.35, 2.22),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 2.1, 2.22),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 2.85, 2.22),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 3.6, 2.22),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 4.35, 2.22),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 5.1, 2.22),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 6.0, 2.22),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 0.2, 350.0),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 1.35, 350.0),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 2.1, 350.0),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 2.85, 350.0),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 3.6, 350.0),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 4.35, 350.0),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 5.1, 350.0),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 5.9, 350.0),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.48, 0.2, 1.2468),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.48, 0.75, 1.2468),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.48, 1.098, 1.2468),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.48, 1.6, 1.2468),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.48, 2.236, 1.2468),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.48, 2.8, 1.2468),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.48, 3.5, 1.2468),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.48, 4.12, 1.2468),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.48, 4.5, 1.2468),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.48, 4.9, 1.2468),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.48, 5.3, 1.2468),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.48, 5.8, 1.2468),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.48, 6.1, 1.2468)
PRINT(LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into LUT2D for PlateType: "'+@ClassifiedName+'".')



INSERT INTO Parameter (ParameterName, InstrumentName, TransducerName, PlateTypeName, GroupName, ParameterType, ParameterValue, Description)
VALUES 
('DoFiltering', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'TB outlier', 'BOOL', 'false', 'Not implemented yet'),
('CompositionOutputType', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Calibration', 'STRING', 'MRayl', 'Output types are: AQ, DMSO, Glycerol, MRayl, or NaCl'),
('ImpedanceBasedCal', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Calibration', 'BOOL', 'true', 'true = MRayl based calibration; false = DMSO based calibration'),
('UseVoltage', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Calibration', 'BOOL', 'true', 'true = voltage based LUT2D, false = energy based LUT2D'),
('UseImpedanceModel', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Calibration', 'BOOL', 'false', 'true = use model'),
('CalibrationType', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Calibration', 'STRING', 'Omics', 'General calibration type: Omics, Omics2, DMSO, DMSO2, LDV_AQ, LDV_DMSO, RES_AQ'),
('CalibrationVersion', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Calibration', 'STRING', '2.6.0', 'Calibration version'),
('SolventConcLo', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'DMSO', 'FLOAT', '1.479', '%DMSO clipping - Calculated values outside this range will be clipped.'),
('SolventConcHi', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'DMSO', 'FLOAT', '1.481', '%DMSO clipping - Calculated values outside this range will be clipped.'),
('Algorithm2.0', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'EchoAlgorithm', 'BOOL', 'true', ''),
('MaxBotThkToF_Ns', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'EchoAlgorithm', 'INT', '900', 'Default maximum ToF span between BB and TB, in nsec'),
('MinBotThkToF_Ns', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'EchoAlgorithm', 'INT', '450', 'Default minimum ToF span between BB and TB, in nsec'),
('MaxSR_TB1ToF_Ns', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'EchoAlgorithm', 'INT', '0', 'Maximum ToF span from TB feature to SR feature, in nsec'),
('MinSR_TB1ToF_Ns', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'EchoAlgorithm', 'INT', '0', 'Minimum ToF span from TB feature to SR feature, in nsec'),
('NumberFeatures', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'EchoAlgorithm', 'INT', '3', ''),
('RefWaveform', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'EchoAlgorithm', 'STRING', 'LongWaveform', ''),
('SRThreshold', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'EchoAlgorithm', 'FLOAT', '0.5', ''),
('HilbertMinPeakMag', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'EchoAlgorithm', 'FLOAT', '0', 'Any Hilbert peak < HilbertMinPeakMag is removed'),
('HilbertMinBBPeakMag', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'EchoAlgorithm', 'FLOAT', '20', 'Remove all peaks chronologically from beginning until peak > HilbertMinBBPeakMag'),
('DoFiltering', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Homogeneous BB outlier', 'BOOL', 'true', 'Turn on/off BB outlier filtering.'),
('DoMedianFilter', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Homogeneous BB outlier', 'BOOL', 'false', 'Run BB outlier filter output thru a 3x3 median filter (recommended if not doing TB outlier filtering)'),
('Ksigma', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Homogeneous BB outlier', 'FLOAT', '4.0', 'BB outlier if |BB vpp - avg BB vpp| > k*sigma'),
('AvgAnalysisTimePerWell', 'MEDMAN', NULL, @ClassifiedName, 'Survey', 'FLOAT', '123', 'Average nominal time duration (in milliseconds) to do survey analysis for each well.'),
('AvgCollectionTimePerWell', 'MEDMAN', NULL, @ClassifiedName, 'Survey', 'FLOAT', '123', 'Average nominal time duration (in milliseconds) to do survey collection for each well.'),
('DimplePing', 'MEDMAN', NULL, @ClassifiedName, 'Survey', 'BOOL', 'true', 'Default is no dimple ping'),
('DimplePingAmpV', 'MEDMAN', NULL, @ClassifiedName, 'Survey', 'FLOAT', '0.65', 'Dimple Ping Amp'),
('NumEchosPerWell', 'MEDMAN', NULL, @ClassifiedName, 'Survey', 'INT', '1', 'How many echos per well when surveying.'),
('DropXferTime', 'MEDMAN', NULL, @ClassifiedName, 'Timing', 'INT', '10', 'In milliseconds'),
('PlateXferTime', 'MEDMAN', NULL, @ClassifiedName, 'Timing', 'INT', '2200', 'In milliseconds'),
('PostXferTime', 'MEDMAN', NULL, @ClassifiedName, 'Timing', 'INT', '0', 'In milliseconds'),
('WellXferTime', 'MEDMAN', NULL, @ClassifiedName, 'Timing', 'INT', '195', 'In milliseconds'),
('DoFiltering', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Inhomogeneous BB outlier', 'BOOL', 'false', 'Turn on/off BB outlier filtering.'),
('Ksigma', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Inhomogeneous BB outlier', 'FLOAT', '4', 'BB outlier if |BB vpp - avg BB vpp| > k*sigma'),
('PingAfterDropTransfer', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Print', 'BOOL', 'false', 'Default is no ping'),
('PingBeforeDropTransfer', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Print', 'BOOL', 'true', 'Default is no ping'),
('PostPingDelay', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Print', 'FLOAT', '0', 'Default delay 0 (in milliseconds)'),
('PrePingDelay', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Print', 'FLOAT', '0', 'Default delay 0 (in milliseconds)'),
('TransZAdjustThreshold', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Print', 'FLOAT', '0.15', 'Transducer Z threshold for adjustment'),
('FluidHeightDiffToleranceMM', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Print', 'FLOAT', '0.3', 'mm'),
('FluidHeightRePingDelayMs', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Print', 'FLOAT', '10', 'ms'),
('WallTB2BBRatio', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'WellCenter', 'FLOAT', '0.1', 'TB/BB ratio for Wall During registration only'),
('WellRegToFRatio', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'WellCenter', 'FLOAT', '0.92', 'Tof Ratio for registration transducer height')
PRINT(LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into Parameter for PlateType: "'+@ClassifiedName+'".')



INSERT INTO MIPConfiguration (ParameterName, PlateTypeName, Iteration, ParameterGroup, ParameterType, ParameterValue, Description, X, Y, Z, A, B)
VALUES 
('Type', @ClassifiedName, NULL, 'ZSweep', 'STRING', 'RTNONE', NULL, NULL, NULL, NULL, NULL, NULL),
('RangeUm', @ClassifiedName, NULL, 'ZSweep', 'FLOAT', '500.00', NULL, NULL, NULL, NULL, NULL, NULL),
('StepSizeUm', @ClassifiedName, NULL, 'ZSweep', 'FLOAT', '50.00', NULL, NULL, NULL, NULL, NULL, NULL),
('DelayMsec', @ClassifiedName, NULL, 'ZSweep', 'FLOAT', '50.000', NULL, NULL, NULL, NULL, NULL, NULL),
('InitTargNullMHz', @ClassifiedName, NULL, 'ZSweep', 'FLOAT', '3.000', NULL, NULL, NULL, NULL, NULL, NULL),
('EjectOffRecalcThreshUm', @ClassifiedName, NULL, 'ZSweep', 'FLOAT', '350.000', NULL, NULL, NULL, NULL, NULL, NULL),
('CoarsePSStartDb', @ClassifiedName, NULL, 'ZSweep', 'FLOAT', '-4.000', NULL, NULL, NULL, NULL, NULL, NULL),
('CoarsePSMaxDb', @ClassifiedName, NULL, 'ZSweep', 'FLOAT', '2.000', NULL, NULL, NULL, NULL, NULL, NULL),
('CoarsePSIncrDb', @ClassifiedName, NULL, 'ZSweep', 'FLOAT', '0.100', NULL, NULL, NULL, NULL, NULL, NULL),
('ValidatePeakSep', @ClassifiedName, NULL, 'ZSweep', 'BOOL', 'False', NULL, NULL, NULL, NULL, NULL, NULL),
('ValidateRingDecay', @ClassifiedName, NULL, 'ZSweep', 'BOOL', 'False', NULL, NULL, NULL, NULL, NULL, NULL),
('ValidateRingFreq', @ClassifiedName, NULL, 'ZSweep', 'BOOL', 'False', NULL, NULL, NULL, NULL, NULL, NULL),
('UseFixedZSweepPreamble', @ClassifiedName, NULL, 'ZSweep', 'BOOL', 'False', NULL, NULL, NULL, NULL, NULL, NULL),
('EnableInitialQuickTZ', @ClassifiedName, NULL, 'ZSweep', 'BOOL', 'True', NULL, NULL, NULL, NULL, NULL, NULL),
('AcceptanceMask', @ClassifiedName, NULL, 'ZSweep', 'INT', '14', NULL, NULL, NULL, NULL, NULL, NULL),
('UseMIPToneX', @ClassifiedName, NULL, 'General', 'BOOL', 'False', NULL, NULL, NULL, NULL, NULL, NULL),
('EnableDebugInfo', @ClassifiedName, NULL, 'General', 'BOOL', 'True', NULL, NULL, NULL, NULL, NULL, NULL),
('EnableExtraMIInfo', @ClassifiedName, NULL, 'General', 'BOOL', 'True', NULL, NULL, NULL, NULL, NULL, NULL),
('EnableRunTimePowerAdjustment', @ClassifiedName, NULL, 'General', 'BOOL', 'True', NULL, NULL, NULL, NULL, NULL, NULL),
('AlgorithmType', @ClassifiedName, NULL, 'General', 'STRING', 'Standard', NULL, NULL, NULL, NULL, NULL, NULL),
('EjectUsingLUTToneburst', @ClassifiedName, NULL, 'General', 'BOOL', 'True', NULL, NULL, NULL, NULL, NULL, NULL),
('PreambleType', @ClassifiedName, NULL, 'General', 'STRING', 'FFT', NULL, NULL, NULL, NULL, NULL, NULL),
('DoPreamblePrePing', @ClassifiedName, NULL, 'General', 'BOOL', 'False', NULL, NULL, NULL, NULL, NULL, NULL),
('MISequenceType', @ClassifiedName, NULL, 'General', 'INT', '1', NULL, NULL, NULL, NULL, NULL, NULL),
('FFTPreambleResMHz', @ClassifiedName, NULL, 'General', 'FLOAT', '0.240', NULL, NULL, NULL, NULL, NULL, NULL),
('FFTPreambleAlg', @ClassifiedName, NULL, 'General', 'STRING', 'Alg_2', NULL, NULL, NULL, NULL, NULL, NULL),
('AllMISignals', @ClassifiedName, NULL, 'Capture', 'BOOL', 'False', NULL, NULL, NULL, NULL, NULL, NULL),
('OnlyLastSignals', @ClassifiedName, NULL, 'Capture', 'BOOL', 'False', NULL, NULL, NULL, NULL, NULL, NULL),
('RawSurveySignals', @ClassifiedName, NULL, 'Capture', 'BOOL', 'False', NULL, NULL, NULL, NULL, NULL, NULL),
('AvgSurveySignals', @ClassifiedName, NULL, 'Capture', 'BOOL', 'False', NULL, NULL, NULL, NULL, NULL, NULL),
('IndividualPingSignals', @ClassifiedName, NULL, 'Capture', 'BOOL', 'False', NULL, NULL, NULL, NULL, NULL, NULL),
('DropTransferOff', @ClassifiedName, 1, 'Setting', 'BOOL', 'False', NULL, NULL, NULL, NULL, NULL, NULL),
('DialationFactor', @ClassifiedName, 1, 'Setting', 'FLOAT', '1.000', NULL, NULL, NULL, NULL, NULL, NULL),
('MaxAmplitudeV', @ClassifiedName, 1, 'Setting', 'FLOAT', '4.500', NULL, NULL, NULL, NULL, NULL, NULL),
('UseZSweepCalcPower', @ClassifiedName, 1, 'Setting', 'BOOL', 'False', NULL, NULL, NULL, NULL, NULL, NULL),
('EjectDelayMsec', @ClassifiedName, 1, 'Setting', 'FLOAT', '0.000', NULL, NULL, NULL, NULL, NULL, NULL),
('MIDelayMsec', @ClassifiedName, 1, 'Setting', 'FLOAT', '40.000', NULL, NULL, NULL, NULL, NULL, NULL),
('ConstInterrPingAmp', @ClassifiedName, 1, 'Setting', 'BOOL', 'True', NULL, NULL, NULL, NULL, NULL, NULL),
('InterrogationPingAmpV', @ClassifiedName, 1, 'Setting', 'FLOAT', '0.900', NULL, NULL, NULL, NULL, NULL, NULL),
('StartDb', @ClassifiedName, 1, 'EjectSweep', 'FLOAT', '-3.000', NULL, NULL, NULL, NULL, NULL, NULL),
('StepSizeDb', @ClassifiedName, 1, 'EjectSweep', 'FLOAT', '0.200', NULL, NULL, NULL, NULL, NULL, NULL),
('MaxDb', @ClassifiedName, 1, 'EjectSweep', 'FLOAT', '0.000', NULL, NULL, NULL, NULL, NULL, NULL),
('FFTStartFreqMHz', @ClassifiedName, 1, 'Tuning', 'FLOAT', '4.0', NULL, NULL, NULL, NULL, NULL, NULL),
('FFTEndFreqMHz', @ClassifiedName, 1, 'Tuning', 'FLOAT', '8.0', NULL, NULL, NULL, NULL, NULL, NULL),
('MinWidthCycles', @ClassifiedName, 1, 'Tuning', 'FLOAT', '5.50', NULL, NULL, NULL, NULL, NULL, NULL),
('MaxNullSpaceMHz', @ClassifiedName, 1, 'Tuning', 'FLOAT', '2.50', NULL, NULL, NULL, NULL, NULL, NULL),
('RingingFreqThreshMHz', @ClassifiedName, 1, 'Tuning', 'FLOAT', '8.0', NULL, NULL, NULL, NULL, NULL, NULL),
('RingingAmpThreshV', @ClassifiedName, 1, 'Tuning', 'FLOAT', '75.0', NULL, NULL, NULL, NULL, NULL, NULL),
('TargetStartFreqMHz', @ClassifiedName, 1, 'Tuning', 'FLOAT', '5.0', NULL, NULL, NULL, NULL, NULL, NULL),
('TargetEndFreqMHz', @ClassifiedName, 1, 'Tuning', 'FLOAT', '6.5', NULL, NULL, NULL, NULL, NULL, NULL),
('MinNullSpacingMHz', @ClassifiedName, 1, 'Tuning', 'FLOAT', '1.10', NULL, NULL, NULL, NULL, NULL, NULL),
('MinPeakSepCycles', @ClassifiedName, 1, 'Tuning', 'FLOAT', '6.5', NULL, NULL, NULL, NULL, NULL, NULL),
('MinRingFreqMHz', @ClassifiedName, 1, 'Tuning', 'FLOAT', '10.0', NULL, NULL, NULL, NULL, NULL, NULL),
('MinPeakFactor', @ClassifiedName, 1, 'Tuning', 'FLOAT', '0.90', NULL, NULL, NULL, NULL, NULL, NULL),
('MaxPeakFactor', @ClassifiedName, 1, 'Tuning', 'FLOAT', '2.25', NULL, NULL, NULL, NULL, NULL, NULL),
('EnableImpedanceBasedTPF', @ClassifiedName, 1, 'Tuning', 'BOOL', 'False', NULL, NULL, NULL, NULL, NULL, NULL),
('ImpedanceToTPFFactor', @ClassifiedName, 1, 'Tuning', 'FLOAT', '5.00', NULL, NULL, NULL, NULL, NULL, NULL),
('MinTargetPeakHeight', @ClassifiedName, 1, 'Tuning', 'INT', '100', NULL, NULL, NULL, NULL, NULL, NULL),
('OverPowerAlgoType', @ClassifiedName, 1, 'Tuning', 'INT', '2', NULL, NULL, NULL, NULL, NULL, NULL),
('MinVrms', @ClassifiedName, 1, 'Tuning', 'FLOAT', '0.00', NULL, NULL, NULL, NULL, NULL, NULL),
('MatrixStartCycles', @ClassifiedName, 1, 'Tuning', 'FLOAT', '2.0', NULL, NULL, NULL, NULL, NULL, NULL),
('MatrixWidthCycles', @ClassifiedName, 1, 'Tuning', 'FLOAT', '10.0', NULL, NULL, NULL, NULL, NULL, NULL),
('MoundStartSamples', @ClassifiedName, 1, 'Tuning', 'INT', '0', NULL, NULL, NULL, NULL, NULL, NULL),
('MoundStopSamples', @ClassifiedName, 1, 'Tuning', 'INT', '0', NULL, NULL, NULL, NULL, NULL, NULL),
('InterrogationDelayUs', @ClassifiedName, 1, 'Override', 'FLOAT', '120.000', NULL, NULL, NULL, NULL, NULL, NULL),
('EjectionOffsetUm', @ClassifiedName, 1, 'Offset', 'FLOAT', '0.000', NULL, NULL, NULL, NULL, NULL, NULL),
('Thresh2XferBiasDb', @ClassifiedName, 1, 'Offset', 'FLOAT', '0.000', NULL, NULL, NULL, NULL, NULL, NULL)
PRINT(LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into MIPConfiguration for PlateType: "'+@ClassifiedName+'".')



INSERT INTO PingParameters (InstrumentName, PlateTypeName, TransducerName, Amplitude, TOFWindowStart, TOFWindowEnd, EchoThreshMult, FileName)
VALUES 
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2.1, 29.28054, 45.66454, 15.0, 'Dimple_525_Meta')
PRINT(LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into PingParameters for PlateType: "'+@ClassifiedName+'".')



INSERT INTO PlateSignature (InstrumentName, PlateTypeName, TransducerName, Row, Col, Description, A, B, C, Constant)
VALUES 
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 0, 'A1', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 1, 'A2', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 2, 'A3', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 3, 'A4', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 4, 'A5', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 5, 'A6', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 6, 'A7', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 7, 'A8', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 8, 'A9', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 9, 'A10', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 10, 'A11', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 11, 'A12', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 0, 'B1', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 1, 'B2', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 2, 'B3', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 3, 'B4', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 4, 'B5', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 5, 'B6', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 6, 'B7', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 7, 'B8', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 8, 'B9', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 9, 'B10', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 10, 'B11', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 11, 'B12', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 0, 'C1', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 1, 'C2', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 2, 'C3', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 3, 'C4', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 4, 'C5', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 5, 'C6', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 6, 'C7', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 7, 'C8', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 8, 'C9', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 9, 'C10', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 10, 'C11', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 11, 'C12', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 0, 'D1', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 1, 'D2', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 2, 'D3', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 3, 'D4', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 4, 'D5', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 5, 'D6', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 6, 'D7', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 7, 'D8', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 8, 'D9', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 9, 'D10', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 10, 'D11', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 11, 'D12', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 0, 'E1', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 1, 'E2', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 2, 'E3', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 3, 'E4', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 4, 'E5', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 5, 'E6', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 6, 'E7', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 7, 'E8', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 8, 'E9', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 9, 'E10', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 10, 'E11', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 11, 'E12', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 0, 'F1', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 1, 'F2', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 2, 'F3', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 3, 'F4', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 4, 'F5', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 5, 'F6', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 6, 'F7', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 7, 'F8', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 8, 'F9', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 9, 'F10', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 10, 'F11', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 11, 'F12', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 0, 'G1', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 1, 'G2', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 2, 'G3', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 3, 'G4', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 4, 'G5', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 5, 'G6', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 6, 'G7', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 7, 'G8', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 8, 'G9', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 9, 'G10', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 10, 'G11', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 11, 'G12', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 0, 'H1', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 1, 'H2', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 2, 'H3', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 3, 'H4', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 4, 'H5', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 5, 'H6', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 6, 'H7', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 7, 'H8', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 8, 'H9', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 9, 'H10', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 10, 'H11', 0.0, 0.0, 0.0, 1.48),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 11, 'H12', 0.0, 0.0, 0.0, 1.48)
PRINT(LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into PlateSignature for PlateType: "'+@ClassifiedName+'".')



INSERT INTO PlateType (PlateTypeName, InstrumentName, Manufacturer, LotNumber, PartNumber, BarcodeLocation, Rows, Columns, BootstrapWell, BootstrapZ, SurveyToFRatio, A1OffsetX, A1OffsetY, SkirtHeight, CenterWell, CenterX, CenterY, PlateHeight, WellWidth, WellLength, XWellSpacing, YWellSpacing, WellCapacity, SoundVelocity, BottomInset, PlateUse, PlateFormat, Fluid, BottomThickness, ThicknessTolerance, IsDeleted, ParentPlate)
VALUES 
(@ClassifiedName, 'MEDMAN', 'Quanti', '1', 'A2', 'None', 8, 12, 'F3', 16000.0, 0.86, 14380.0, 11230.0, 7410.0, 'D6', 102711.1, 42935.0, 14500.0, 8200.0, 8200.0, 9000.0, 9000.0, 1000.0, 2860.0, 2.1, 'HID', '96PP', 'AQ', 0.0, 0.0, 0, NULL)
PRINT(LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into PlateType for PlateType: "'+@ClassifiedName+'".')



INSERT INTO ReferenceWaveforms (InstrumentName, PlateTypeName, TransducerName, Waveform, Directory, FileName, Configuration)
VALUES 
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 'LongWaveform', 'waveforms\7p5MHz_Kernel', '7p5MHz_GeneralKernel_081712.csv', '193
nPoints,193
xIncr,2.00E-09
xZero,0.00E+00
xUnits,s
yMult,0.00E+00
yZero,0.00E+00
yOffset,0.00E+00
yUnits,v

s,v
0,0.015625
1,0.0625
2,0.109375
3,0.15625
4,0.203125
5,0.25
6,0.291666667
7,0.338541667
8,0.375
9,0.421875
10,0.463541667
11,0.505208333
12,0.546875
13,0.588541667
14,0.625
15,0.666666667
16,0.697916667
17,0.723958333
18,0.760416667
19,0.78125
20,0.807291667
21,0.828125
22,0.84375
23,0.859375
24,0.869791667
25,0.875
26,0.880208333
27,0.875
28,0.864583333
29,0.848958333
30,0.833333333
31,0.817708333
32,0.791666667
33,0.75
34,0.713541667
35,0.671875
36,0.619791667
37,0.5625
38,0.489583333
39,0.427083333
40,0.348958333
41,0.265625
42,0.177083333
43,0.083333333
44,-0.010416667
45,-0.114583333
46,-0.213541667
47,-0.317708333
48,-0.427083333
49,-0.536458333
50,-0.645833333
51,-0.75
52,-0.848958333
53,-0.953125
54,-1.052083333
55,-1.140625
56,-1.229166667
57,-1.307291667
58,-1.380208333
59,-1.4375
60,-1.5
61,-1.536458333
62,-1.567708333
63,-1.583333333
64,-1.583333333
65,-1.578125
66,-1.5625
67,-1.520833333
68,-1.473958333
69,-1.40625
70,-1.333333333
71,-1.239583333
72,-1.140625
73,-1.026041667
74,-0.90625
75,-0.776041667
76,-0.625
77,-0.473958333
78,-0.317708333
79,-0.161458333
80,0.010416667
81,0.171875
82,0.338541667
83,0.5
84,0.666666667
85,0.828125
86,0.973958333
87,1.119791667
88,1.244791667
89,1.364583333
90,1.473958333
91,1.572916667
92,1.651041667
93,1.729166667
94,1.776041667
95,1.802083333
96,1.822916667
97,1.802083333
98,1.776041667
99,1.729166667
100,1.651041667
101,1.572916667
102,1.473958333
103,1.364583333
104,1.244791667
105,1.119791667
106,0.973958333
107,0.828125
108,0.666666667
109,0.5
110,0.338541667
111,0.171875
112,0.010416667
113,-0.161458333
114,-0.317708333
115,-0.473958333
116,-0.625
117,-0.776041667
118,-0.90625
119,-1.026041667
120,-1.140625
121,-1.239583333
122,-1.333333333
123,-1.40625
124,-1.473958333
125,-1.520833333
126,-1.5625
127,-1.578125
128,-1.583333333
129,-1.583333333
130,-1.567708333
131,-1.536458333
132,-1.5
133,-1.4375
134,-1.380208333
135,-1.307291667
136,-1.229166667
137,-1.140625
138,-1.052083333
139,-0.953125
140,-0.848958333
141,-0.75
142,-0.645833333
143,-0.536458333
144,-0.427083333
145,-0.317708333
146,-0.213541667
147,-0.114583333
148,-0.010416667
149,0.083333333
150,0.177083333
151,0.265625
152,0.348958333
153,0.427083333
154,0.489583333
155,0.5625
156,0.619791667
157,0.671875
158,0.713541667
159,0.75
160,0.791666667
161,0.817708333
162,0.833333333
163,0.848958333
164,0.864583333
165,0.875
166,0.880208333
167,0.875
168,0.869791667
169,0.859375
170,0.84375
171,0.828125
172,0.807291667
173,0.78125
174,0.760416667
175,0.723958333
176,0.697916667
177,0.666666667
178,0.625
179,0.588541667
180,0.546875
181,0.505208333
182,0.463541667
183,0.421875
184,0.375
185,0.338541667
186,0.291666667
187,0.25
188,0.203125
189,0.15625
190,0.109375
191,0.0625
192,0.015625')
PRINT(LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into ReferenceWaveforms for PlateType: "'+@ClassifiedName+'".')



INSERT INTO TransferVolume (InstrumentName, PlateTypeName, TransducerName, ResolutionNl, MinimumNl, MaxVolumeTotalNl, IncrNl, MaxAllowableVolumeDeltaNl, MinWellVolumeUL, MaxWellVolumeUL, MinFluidThicknessMM, FileName, Configuration)
VALUES 
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 25.0, 25.0, 320000.0, 25.0, 2000.0, 50.0, 350.0, 0.2, 'ToneX_25nl_3seg_1pt1chirp.cfg', '# This file was modified automatically on Fri Jan 21 13:53:55 2011
#
# 2.5nl Toneburst config file
#
# This file contains parameters that define the 2.5nl toneburst used by the system.
#
# See FluidTransfer::config() for mapping in source code
#
# $Id: //depot/main/Pico/Medman/conf/server/ToneX_0pt8.cfg#1 $
#

:GENERAL

Segment		INT		99
Type		STRING		"X" # if X, then see below

# If toneburst type is not X, then we don''t need to specify
# the start/end frequencies and amplitude as the actual printing
# values come from the LUT.
# If toneburst type is not X, then we need to specify the 
# toneburst length, as follows:
# Length	FLOAT		180  # only applicable when not Tone X

:TONEBURST_X

# You need to define a configuration set for each segment.  For example,
# if # segments is 3, then you *must* define configuration sets SEGMENT1,
# SEGMENT2, and SEGMENT3.  Failure to do so is a catastrophic error.
NumSegments		INT		3

:SEGMENT1
Type		STRING		"G10"
FrequencyChirpWidth		FLOAT		1.1 # MHz

:SEGMENT2
Type		STRING		"Z"

:SEGMENT3
Type		STRING		"G6"
FrequencyChirpWidth		FLOAT		1.1 # MHz')
PRINT(LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into TransferVolume for PlateType: "'+@ClassifiedName+'".')



INSERT INTO WellAdjustment (InstrumentName, PlateTypeName, Algorithm, WellList, WellAdjustPeriod, BackOffUm, SpatialFrequencyUm, PlateSkewAdjust, WellListOffsetXUm, WellListOffsetYUm)
VALUES 
('MEDMAN', @ClassifiedName, 'V1.2', 'D6', 0, 500, 25, 0, 0.0, -1000.0)
PRINT(LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into WellAdjustment for PlateType: "'+@ClassifiedName+'".')



INSERT INTO PlateRegistration (RegistrationDate, InstrumentName, TransducerName, PlateTypeName, CenterWell, CenterX, CenterY, XWellSpacing, YWellSpacing)
VALUES 
('2018-04-27 12:09:00', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'D6', 102825.0, 43041.0, 9000.0, 9000.0),
('2018-07-24 10:49:37', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'D6', 103011.0, 42935.0, 9000.0, 9000.0),
('2018-07-24 15:22:14', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'D6', 102667.155, 42970.1563, 9000.0, 9000.0)
PRINT(LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into PlateRegistration for PlateType: "'+@ClassifiedName+'".')



IF (SELECT COUNT(*) FROM D2AMemory WHERE Waveform = 'Dimple_525_Meta') != 0
	PRINT('D2AMemory waveform "Dimple_525_Meta" already exists.  No need to insert.')
ELSE
	BEGIN
	
    DECLARE @FreeMemoryAddress INT
   
    SELECT @FreeMemoryAddress = MAX(MemoryAddress) + 1 FROM D2AMemory WHERE MemoryAddress < 80
    
    PRINT('Inserting new waveform at available memory address ' + CAST(@FreeMemoryAddress AS VARCHAR(4)) + '.')

 	

INSERT INTO D2AMemory (Waveform, MemoryAddress, Type, Length, Path, Description, Configuration)
VALUES 
('Dimple_525_Meta', @FreeMemoryAddress, 'X', 300000, 'Dimple_525_Meta.cfg', 'dimple meta', '# Sample Dimple Ping waveform
# Modeled from one of the newer Dimple Ping waveforms:

:GENERAL

Type                          STRING            "X"

:TONEBURST_X

NumSegments                   INT               3

:SEGMENT1
Type                          STRING            "G1"
CenterFreqMHz                 FLOAT       7.5
FrequencyChirpWidth           FLOAT       1.0   # MHz
LengthUs                      FLOAT       55.0
RelativeAmplitudeV            FLOAT       1.0

:SEGMENT2
Type                          STRING            "Z"
LengthUs                      FLOAT       200.0

:SEGMENT3
Type                          STRING            "I"

Samples           FLTVEC      0 -0.0051511	0.0023677	0.017729	0.0074864	-0.042689	-0.11175	-0.16642	-0.17827	-0.13232	-0.037364	0.072495	0.15653	0.18334	0.14902	0.077688	0.014064	0.00071716	0.052564	0.15001	0.23758	0.25011	0.1408	-0.0899	-0.38451	-0.64575	-0.76635	-0.6746	-0.36522	0.089708	0.56079	0.90429	1.0115	0.84808	0.46635	-0.01366	-0.44703	-0.71336	-0.75692	-0.59838	-0.32086	-0.032363	0.17528	0.25637	0.22324	0.12767	0.036698	-0.002022	0.024491	0.094048	0.16075	0.18317	0.14213	0.050389	-0.060253	-0.14747	-0.18011	-0.15717	-0.097585	-0.029691	0.01437	0.015404	-0.0070559	-0.015551	-0.0044209	0.0026431	-0.00026692	-0.0010613	0.00072076	2.01E-19	-0.00044284	0.00042732	0.0000462	-0.00013795	0.00015105	0.0000376	-0.0000908	0.0000278	0.00000877')
PRINT(LTRIM(STR(@@ROWCOUNT)) + '  row(s) inserted into D2AMemory for waveform: "Dimple_525_Meta".')


	END

