SET NOCOUNT ON

USE MEDMANdb

DECLARE @UnclassifiedName VARCHAR(MAX) = '384LDV_Plus_AQ_GP_UCP'
DECLARE @ClassifiedName   VARCHAR(MAX) = '384LDVS_Plus_AQ_GP_UCP'

-- Details for updating plate classification.
DECLARE @PCAnalysis        VARCHAR(MAX) = NULL
DECLARE @PCMeasurement     VARCHAR(MAX) = NULL
DECLARE @PCInstrumentName  VARCHAR(MAX) = 'MEDMAN'
DECLARE @PCTransducerName  VARCHAR(MAX) = 'Transducer10MHz'
DECLARE @PCPlateFormFactor VARCHAR(MAX) = '384LDVS'

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
('MEDMAN', @UnclassifiedName, 'Transducer10MHz', 0.2, 29.28312, 45.66712, 15.0, 'PingBurst')
PRINT(LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into PingParameters for PlateType: "'+@UnclassifiedName+'".')



INSERT INTO PlateType (PlateTypeName, InstrumentName, Manufacturer, LotNumber, PartNumber, BarcodeLocation, Rows, Columns, BootstrapWell, BootstrapZ, SurveyToFRatio, A1OffsetX, A1OffsetY, SkirtHeight, CenterWell, CenterX, CenterY, PlateHeight, WellWidth, WellLength, XWellSpacing, YWellSpacing, WellCapacity, SoundVelocity, BottomInset, PlateUse, PlateFormat, Fluid, BottomThickness, ThicknessTolerance, IsDeleted, ParentPlate)
VALUES 
(@UnclassifiedName, 'MEDMAN', 'Labcyte', '1', 'LP-0200', 'None', 16, 24, 'N7', 17000.0, 0.86, 12130.0, 8990.0, 2410.0, 'H12', 105670.0, 39750.0, 10400.0, 1540.0, 1540.0, 4500.0, 4506.0, 20.0, 2500.0, 4.5, 'SRC', '384LDV', 'Glycerol', 0.0, 0.0, 0, NULL)
PRINT(LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into PlateType for PlateType: "'+@UnclassifiedName+'".')



INSERT INTO TransferVolume (InstrumentName, PlateTypeName, TransducerName, ResolutionNl, MinimumNl, MaxVolumeTotalNl, IncrNl, MaxAllowableVolumeDeltaNl, MinWellVolumeUL, MaxWellVolumeUL, MinFluidThicknessMM, FileName, Configuration)
VALUES 
('MEDMAN', @UnclassifiedName, 'Transducer10MHz', 25.0, 25.0, 100000.0, 25.0, 500.0, 3.75, 15.0, 0.65, 'ToneX_25nl_3seg_1pt1chirp.cfg', '# This file was modified automatically on Fri Jan 21 13:53:55 2011
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
('2017-05-22 18:31:10', 'MEDMAN', 'Transducer10MHz', @UnclassifiedName, 'H12', 105670.0, 39750.0, 4500.0, 4506.0)
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
('CoeffAInMRayl', 'MEDMAN', '', @ClassifiedName, 'y = Ax^2 + Bx + C', 0.0, 0.0, -0.8, NULL, NULL),
('CoeffBInMRayl', 'MEDMAN', '', @ClassifiedName, 'y = Ax^2 + Bx + C', 0.0, 0.0, -0.83, NULL, NULL),
('VelocityVsMRayl', 'MEDMAN', '', @ClassifiedName, 'y = Ax^2 + Bx + C', 165.62, -70.45, 1226.0, NULL, NULL),
('MRayl2Glycerol', 'MEDMAN', '', @ClassifiedName, 'y = Ax^2 + Bx + C', 18.951, 24.889, -78.018, NULL, NULL)
PRINT(LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into Coefficient for PlateType: "'+@ClassifiedName+'".')



INSERT INTO LUT (LUTName, InstrumentName, TransducerName, PlateTypeName, Volume, Description, X, Y)
VALUES 
('ToneX_CF_MHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '1', 1.48, 6.85),
('ToneX_CF_MHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '1', 1.59, 6.95),
('ToneX_CF_MHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '1', 1.71, 7.1),
('ToneX_CF_MHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '1', 1.82, 7.2),
('ToneX_CF_MHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '1', 1.93, 7.3),
('ToneX_CF_MHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '1', 2.02, 7.5),
('ToneX_CF_MHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '1', 2.06, 7.5),
('ToneX_CF_MHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '3', 1.48, 6.165),
('ToneX_CF_MHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '3', 1.59, 6.394),
('ToneX_CF_MHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '3', 1.71, 6.74),
('ToneX_CF_MHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '3', 1.82, 6.84),
('ToneX_CF_MHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '3', 1.93, 6.935),
('ToneX_CF_MHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '3', 2.02, 7.125),
('ToneX_CF_MHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '3', 2.06, 7.125),
('FrequencyvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, NULL, 1.48, 12.2),
('FrequencyvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, NULL, 1.59, 12.2),
('FrequencyvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, NULL, 1.71, 12.2),
('FrequencyvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, NULL, 1.82, 12.2),
('FrequencyvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, NULL, 1.93, 12.2),
('FrequencyvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, NULL, 2.02, 12.2),
('FrequencyvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, NULL, 2.06, 12.2),
('ToneX_RelAmp', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '1', 1.48, 0.95),
('ToneX_RelAmp', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '1', 1.59, 0.95),
('ToneX_RelAmp', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '1', 1.71, 0.95),
('ToneX_RelAmp', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '1', 1.82, 0.95),
('ToneX_RelAmp', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '1', 1.93, 0.95),
('ToneX_RelAmp', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '1', 2.02, 0.95),
('ToneX_RelAmp', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '1', 2.06, 0.95),
('ToneX_RelAmp', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '3', 1.48, 0.6),
('ToneX_RelAmp', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '3', 1.59, 0.6),
('ToneX_RelAmp', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '3', 1.71, 0.6),
('ToneX_RelAmp', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '3', 1.82, 0.6),
('ToneX_RelAmp', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '3', 1.93, 0.6),
('ToneX_RelAmp', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '3', 2.02, 0.6),
('ToneX_RelAmp', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '3', 2.06, 0.6),
('AmpvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, NULL, 1.48, 1.6),
('AmpvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, NULL, 1.59, 1.6),
('AmpvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, NULL, 1.71, 1.6),
('AmpvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, NULL, 1.82, 1.6),
('AmpvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, NULL, 1.93, 1.6),
('AmpvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, NULL, 2.02, 1.6),
('AmpvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, NULL, 2.06, 1.6),
('ToneX_Width_us', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '1', 1.48, 275.0),
('ToneX_Width_us', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '1', 1.59, 275.0),
('ToneX_Width_us', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '1', 1.71, 275.0),
('ToneX_Width_us', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '1', 1.82, 275.0),
('ToneX_Width_us', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '1', 1.93, 275.0),
('ToneX_Width_us', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '1', 2.02, 275.0),
('ToneX_Width_us', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '1', 2.06, 275.0),
('ToneX_Width_us', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '2', 1.48, 130.0),
('ToneX_Width_us', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '2', 1.59, 130.0),
('ToneX_Width_us', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '2', 1.71, 130.0),
('ToneX_Width_us', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '2', 1.82, 130.0),
('ToneX_Width_us', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '2', 1.93, 130.0),
('ToneX_Width_us', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '2', 2.02, 130.0),
('ToneX_Width_us', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '2', 2.06, 130.0),
('ToneX_Width_us', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '3', 1.48, 100.0),
('ToneX_Width_us', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '3', 1.59, 100.0),
('ToneX_Width_us', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '3', 1.71, 100.0),
('ToneX_Width_us', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '3', 1.82, 100.0),
('ToneX_Width_us', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '3', 1.93, 100.0),
('ToneX_Width_us', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '3', 2.02, 100.0),
('ToneX_Width_us', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, '3', 2.06, 100.0),
('ImpedCorrectionvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 1.48, 1.0),
('ImpedCorrectionvsSolvent', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 2.2, 1.0),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.7777960623, 1.620117188),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.7811943618, 1.65234375),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.7849215037, 1.681640625),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.7885938123, 1.71875),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.7923210065, 1.740234375),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.7960481483, 1.775390625),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.7997205093, 1.80859375),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8034476511, 1.83984375),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8071200121, 1.872070313),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.810792373, 1.899414063),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8144646817, 1.934570313),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8180822094, 1.958007813),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8217545704, 1.984375),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8253720981, 2.014648438),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8289347926, 2.040039063),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8324975394, 2.068359375),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8361150672, 2.100585938),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8396777617, 2.119140625),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8432405085, 2.149414063),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.846803203, 2.171875),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8503659498, 2.198242188),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8539834776, 2.21875),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8576010053, 2.256835938),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8611636998, 2.291992188),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8648360608, 2.325195313),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8684535885, 2.385742188),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8721259494, 2.452148438),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8759078722, 2.528320313),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8796350664, 2.625),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8834170414, 2.744140625),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8872537974, 2.87109375),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8910357725, 3.014648438),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8948725285, 3.1875),
('BBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8987092845, 3.40625),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.7777960623, 0.8310546875),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.7811943618, 0.8310546875),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.7849215037, 0.8388671875),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.7885938123, 0.8486328125),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.7923210065, 0.876953125),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.7960481483, 0.896484375),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.7997205093, 0.9384765625),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8034476511, 0.994140625),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8071200121, 1.055664063),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.810792373, 1.12109375),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8144646817, 1.190429688),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8180822094, 1.271484375),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8217545704, 1.361328125),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8253720981, 1.477539063),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8289347926, 1.58984375),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8324975394, 1.71875),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8361150672, 1.850585938),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8396777617, 1.990234375),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8432405085, 2.125976563),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.846803203, 2.265625),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8503659498, 2.40625),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8539834776, 2.55078125),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8576010053, 2.694335938),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8611636998, 2.829101563),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8648360608, 2.966796875),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8684535885, 3.103515625),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8721259494, 3.235351563),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8759078722, 3.361328125),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8796350664, 3.490234375),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8834170414, 3.610351563),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8872537974, 3.719726563),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8910357725, 3.828125),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8948725285, 3.905273438),
('TBToFcorrection', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, NULL, 0.8987092845, 3.951171875)
PRINT(LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into LUT for PlateType: "'+@ClassifiedName+'".')



INSERT INTO LUT2D (LUT2DName, InstrumentName, TransducerName, PlateTypeName, Volume, Description, X, Y, Z)
VALUES 
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.48, 0.6, 1.5173),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.48, 0.65, 1.5173),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.48, 0.8, 1.5173),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.48, 1.0, 1.56843),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.48, 1.25, 1.5353),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.48, 1.45, 1.4819),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.48, 1.6, 1.43514),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.48, 1.76, 1.38613),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.48, 2.2, 1.3124),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.48, 2.4, 1.33766),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.48, 2.6, 1.41882),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.48, 2.85, 1.43522),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.48, 3.5, 1.43522),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.59, 0.6, 1.5953),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.59, 0.65, 1.5953),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.59, 0.8, 1.5953),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.59, 1.0, 1.64819),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.59, 1.25, 1.59557),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.59, 1.45, 1.53611),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.59, 1.6, 1.48868),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.59, 1.76, 1.44124),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.59, 2.2, 1.37336),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.59, 2.4, 1.39652),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.59, 2.6, 1.46898),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.59, 2.85, 1.54717),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.59, 3.5, 1.54717),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.71, 0.6, 1.69293),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.71, 0.65, 1.69293),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.71, 0.8, 1.69293),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.71, 1.0, 1.76005),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.71, 1.25, 1.68421),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.71, 1.45, 1.61562),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.71, 1.6, 1.56544),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.71, 1.76, 1.51786),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.71, 2.2, 1.45574),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.71, 2.4, 1.48),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.71, 2.6, 1.54966),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.71, 2.85, 1.64076),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.71, 3.5, 1.64076),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.82, 0.6, 1.78624),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.82, 0.65, 1.78624),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.82, 0.8, 1.78624),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.82, 1.0, 1.85618),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.82, 1.25, 1.77403),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.82, 1.45, 1.69709),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.82, 1.6, 1.64033),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.82, 1.76, 1.5867),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.82, 2.2, 1.52309),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.82, 2.4, 1.55923),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.82, 2.6, 1.65199),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.82, 2.85, 1.71511),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.82, 3.5, 1.71511),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.93, 0.6, 1.96517),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.93, 0.65, 1.96517),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.93, 0.8, 1.96517),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.93, 1.0, 2.01519),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.93, 1.25, 1.95044),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.93, 1.45, 1.85884),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.93, 1.6, 1.78359),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.93, 1.76, 1.7105),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.93, 2.2, 1.65239),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.93, 2.4, 1.7494),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.93, 2.6, 1.95908),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.93, 2.85, 1.90954),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 1.93, 3.5, 1.90954),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 2.02, 0.6, 2.12354),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 2.02, 0.65, 2.12354),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 2.02, 0.8, 2.12354),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 2.02, 1.0, 2.17572),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 2.02, 1.25, 2.10377),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 2.02, 1.45, 2.01474),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 2.02, 1.6, 1.94276),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 2.02, 1.76, 1.87163),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 2.02, 2.2, 1.78881),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 2.02, 2.4, 1.84861),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 2.02, 2.6, 1.99738),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 2.02, 2.85, 2.08633),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 2.02, 3.5, 2.08633),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 2.06, 0.6, 2.18456),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 2.06, 0.65, 2.18456),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 2.06, 0.8, 2.18456),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 2.06, 1.0, 2.25454),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 2.06, 1.25, 2.1654),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 2.06, 1.45, 2.06567),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 2.06, 1.6, 1.98812),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 2.06, 1.76, 1.91392),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 2.06, 2.2, 1.84202),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 2.06, 2.4, 1.91837),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 2.06, 2.6, 2.09236),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 2.06, 2.85, 2.17882),
('SolventFluidThickThreshEnergy', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'DMSO vs mm', 2.06, 3.5, 2.17882),
('MaxRepRateHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'f(%DMSO;fluidHeight)', 1.48, 0.2, 100.0),
('MaxRepRateHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'f(%DMSO;fluidHeight)', 1.48, 5.0, 100.0),
('MaxRepRateHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'f(%DMSO;fluidHeight)', 1.59, 0.2, 100.0),
('MaxRepRateHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'f(%DMSO;fluidHeight)', 1.59, 5.0, 100.0),
('MaxRepRateHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'f(%DMSO;fluidHeight)', 1.71, 0.2, 100.0),
('MaxRepRateHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'f(%DMSO;fluidHeight)', 1.71, 5.0, 100.0),
('MaxRepRateHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'f(%DMSO;fluidHeight)', 1.82, 0.2, 100.0),
('MaxRepRateHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'f(%DMSO;fluidHeight)', 1.82, 5.0, 100.0),
('MaxRepRateHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'f(%DMSO;fluidHeight)', 1.93, 0.2, 100.0),
('MaxRepRateHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'f(%DMSO;fluidHeight)', 1.93, 5.0, 100.0),
('MaxRepRateHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'f(%DMSO;fluidHeight)', 2.02, 0.2, 100.0),
('MaxRepRateHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'f(%DMSO;fluidHeight)', 2.02, 5.0, 100.0),
('MaxRepRateHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'f(%DMSO;fluidHeight)', 2.06, 0.2, 100.0),
('MaxRepRateHz', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'f(%DMSO;fluidHeight)', 2.06, 5.0, 100.0),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 0.3, 1.5),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 0.4, 1.5),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 0.6, 1.55),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 0.8, 1.62),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 1.0, 1.79),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 1.25, 1.81),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 1.45, 1.78),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 1.6, 1.6),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 2.0, 1.21),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 2.4, 1.397),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 2.6, 1.55),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 2.8, 1.57),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 5.0, 1.57),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.59, 0.3, 1.54),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.59, 0.4, 1.54),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.59, 0.67, 1.57),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.59, 0.91, 1.64),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.59, 1.18, 1.67),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.59, 1.25, 1.64),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.59, 1.57, 1.55),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.59, 1.76, 1.4),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.59, 2.2, 1.34),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.59, 2.35, 1.56),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.59, 2.8, 1.6),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.59, 3.2, 1.6),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.59, 5.0, 1.6),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.71, 0.3, 1.633),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.71, 0.4, 1.633),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.71, 0.56, 1.633),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.71, 0.73, 1.767),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.71, 0.95, 1.785),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.71, 1.13, 1.703),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.71, 1.35, 1.626),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.71, 1.57, 1.444),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.71, 1.77, 1.46),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.71, 2.18, 1.55),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.71, 2.66, 1.65),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.71, 3.2, 1.687),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.71, 5.0, 1.687),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.82, 0.3, 1.455),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.82, 0.4, 1.455),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.82, 0.61, 1.455),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.82, 0.8, 1.528),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.82, 1.04, 1.572),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.82, 1.26, 1.426),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.82, 1.48, 1.339),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.82, 1.65, 1.263),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.82, 1.83, 1.42),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.82, 2.28, 1.583),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.82, 2.76, 1.574),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.82, 3.2, 1.574),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.82, 5.0, 1.574),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.93, 0.3, 1.457),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.93, 0.4, 1.457),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.93, 0.71, 1.457),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.93, 0.93, 1.533),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.93, 1.15, 1.598),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.93, 1.36, 1.452),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.93, 1.55, 1.299),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.93, 1.75, 1.323),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.93, 1.98, 1.367),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.93, 2.36, 1.478),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.93, 2.8, 1.495),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.93, 3.2, 1.495),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.93, 5.0, 1.495),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.02, 0.3, 1.493),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.02, 0.4, 1.493),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.02, 0.63, 1.493),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.02, 0.94, 1.637),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.02, 1.05, 1.57),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.02, 1.28, 1.505),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.02, 1.55, 1.4),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.02, 1.72, 1.36),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.02, 1.95, 1.268),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.02, 2.39, 1.615),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.02, 2.75, 1.708),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.02, 3.2, 1.708),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.02, 5.0, 1.708),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.06, 0.3, 1.493),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.06, 0.4, 1.493),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.06, 0.63, 1.493),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.06, 0.94, 1.637),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.06, 1.05, 1.57),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.06, 1.28, 1.505),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.06, 1.55, 1.4),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.06, 1.72, 1.36),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.06, 1.95, 1.268),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.06, 2.39, 1.615),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.06, 2.75, 1.708),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.06, 3.2, 1.708),
('Thresh2XferdB', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.06, 5.0, 1.708),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 0.6, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 0.65, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 0.8, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 1.0, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 1.25, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 1.45, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 1.6, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 1.76, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 2.2, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 2.4, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 2.6, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 2.85, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.48, 3.5, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.59, 0.6, 450.0),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.59, 0.65, 450.0),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.59, 0.8, 450.0),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.59, 1.0, 450.0),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.59, 1.25, 450.0),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.59, 1.45, 450.0),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.59, 1.6, 450.0),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.59, 1.76, 450.0),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.59, 2.2, 450.0),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.59, 2.4, 450.0),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.59, 2.6, 450.0),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.59, 2.85, 450.0),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.59, 3.5, 450.0),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.71, 0.6, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.71, 0.65, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.71, 0.8, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.71, 1.0, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.71, 1.25, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.71, 1.45, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.71, 1.6, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.71, 1.76, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.71, 2.2, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.71, 2.4, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.71, 2.6, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.71, 2.85, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.71, 3.5, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.82, 0.6, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.82, 0.65, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.82, 0.8, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.82, 1.0, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.82, 1.25, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.82, 1.45, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.82, 1.6, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.82, 1.76, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.82, 2.2, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.82, 2.4, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.82, 2.6, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.82, 2.85, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.82, 3.5, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.93, 0.6, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.93, 0.65, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.93, 0.8, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.93, 1.0, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.93, 1.25, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.93, 1.45, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.93, 1.6, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.93, 1.76, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.93, 2.2, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.93, 2.4, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.93, 2.6, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.93, 2.85, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 1.93, 3.5, 449.99899),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.02, 0.6, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.02, 0.65, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.02, 0.8, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.02, 1.0, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.02, 1.25, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.02, 1.45, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.02, 1.6, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.02, 1.76, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.02, 2.2, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.02, 2.4, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.02, 2.6, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.02, 2.85, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.02, 3.5, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.06, 0.6, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.06, 0.65, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.06, 0.8, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.06, 1.0, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.06, 1.25, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.06, 1.45, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.06, 1.6, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.06, 1.76, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.06, 2.2, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.06, 2.4, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.06, 2.6, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.06, 2.85, 449.99997),
('EjectionOffset', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'ejectionOffset=f(%DMSO;fluidHeight)', 2.06, 3.5, 449.99997),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.48, 0.0, 0.0),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.48, 0.2, 2.0),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.48, 0.6, 3.9),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.48, 1.0, 5.7),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.48, 1.4, 7.6),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.48, 1.8, 9.4),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.48, 2.2, 11.3),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.48, 2.6, 13.1),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.48, 3.0, 15.0),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.48, 3.4, 16.8),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.48, 3.8, 18.7),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.48, 6.0, 28.9),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.59, 0.0, 0.0),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.59, 0.2, 1.5),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.59, 0.6, 3.5),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.59, 1.0, 5.4),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.59, 1.4, 7.4),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.59, 1.8, 9.3),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.59, 2.2, 11.3),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.59, 2.6, 13.3),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.59, 3.0, 15.2),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.59, 3.4, 17.2),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.59, 3.8, 19.2),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.59, 6.0, 29.9),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.71, 0.0, 0.0),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.71, 0.2, 1.3),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.71, 0.6, 3.3),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.71, 1.0, 5.3),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.71, 1.4, 7.3),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.71, 1.8, 9.3),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.71, 2.2, 11.3),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.71, 2.6, 13.3),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.71, 3.0, 15.2),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.71, 3.4, 17.2),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.71, 3.8, 19.2),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.71, 6.0, 30.1),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.82, 0.0, 0.0),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.82, 0.2, 1.8),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.82, 0.6, 3.7),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.82, 1.0, 5.6),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.82, 1.4, 7.5),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.82, 1.8, 9.3),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.82, 2.2, 11.2),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.82, 2.6, 13.1),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.82, 3.0, 15.0),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.82, 3.4, 16.8),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.82, 3.8, 18.7),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.82, 6.0, 29.0),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.93, 0.0, 0.0),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.93, 0.2, 1.8),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.93, 0.6, 3.7),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.93, 1.0, 5.6),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.93, 1.4, 7.5),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.93, 1.8, 9.4),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.93, 2.2, 11.3),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.93, 2.6, 13.2),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.93, 3.0, 15.1),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.93, 3.4, 17.0),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.93, 3.8, 18.9),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 1.93, 6.0, 29.4),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 2.02, 0.0, 0.0),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 2.02, 0.2, 1.8),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 2.02, 0.6, 3.7),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 2.02, 1.0, 5.5),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 2.02, 1.4, 7.4),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 2.02, 1.8, 9.3),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 2.02, 2.2, 11.2),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 2.02, 2.6, 13.1),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 2.02, 3.0, 15.0),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 2.02, 3.4, 16.9),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 2.02, 3.8, 18.8),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 2.02, 6.0, 29.3),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 2.06, 0.0, 0.0),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 2.06, 0.2, 1.8),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 2.06, 0.6, 3.7),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 2.06, 1.0, 5.5),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 2.06, 1.4, 7.4),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 2.06, 1.8, 9.3),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 2.06, 2.2, 11.2),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 2.06, 2.6, 13.1),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 2.06, 3.0, 15.0),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 2.06, 3.4, 16.9),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 2.06, 3.8, 18.8),
('WellFluidVolume', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, NULL, 'f(solvent,mm) = Volume(uL)', 2.06, 6.0, 29.3),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.48, 1.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.48, 2.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.48, 3.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.48, 4.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.48, 5.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.48, 6.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.59, 1.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.59, 2.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.59, 3.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.59, 4.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.59, 5.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.59, 6.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.71, 1.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.71, 2.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.71, 3.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.71, 4.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.71, 5.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.71, 6.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.82, 1.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.82, 2.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.82, 3.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.82, 4.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.82, 5.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.82, 6.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.93, 1.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.93, 2.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.93, 3.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.93, 4.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.93, 5.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.93, 6.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.97, 1.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.97, 2.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.97, 3.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.97, 4.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.97, 5.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 1.97, 6.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 2.02, 1.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 2.02, 2.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 2.02, 3.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 2.02, 4.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 2.02, 5.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 2.02, 6.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 2.06, 1.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 2.06, 2.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 2.06, 3.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 2.06, 4.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 2.06, 5.0, 0.0),
('PwrAdj4FluidHeight', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 25.0, 'dB vs mm', 2.06, 6.0, 0.0)
PRINT(LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into LUT2D for PlateType: "'+@ClassifiedName+'".')



INSERT INTO Parameter (ParameterName, InstrumentName, TransducerName, PlateTypeName, GroupName, ParameterType, ParameterValue, Description)
VALUES 
('Algorithm2.0', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'EchoAlgorithm', 'BOOL', 'true', ''),
('MaxBotThkToF_Ns', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'EchoAlgorithm', 'INT', '1150', 'Default maximum ToF span between BB and TB, in nsec'),
('MaxSR_TB1ToF_Ns', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'EchoAlgorithm', 'INT', '0', 'Maximum ToF span from TB feature to SR feature, in nsec'),
('MinBotThkToF_Ns', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'EchoAlgorithm', 'INT', '500', 'Default minimum ToF span between BB and TB, in nsec'),
('MinSR_TB1ToF_Ns', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'EchoAlgorithm', 'INT', '0', 'Minimum ToF span from TB feature to SR feature, in nsec'),
('NumberFeatures', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'EchoAlgorithm', 'INT', '3', ''),
('RefWaveform', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'EchoAlgorithm', 'STRING', 'LongWaveform', ''),
('SRThreshold', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'EchoAlgorithm', 'FLOAT', '0.3', ''),
('HilbertMinPeakMag', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'EchoAlgorithm', 'FLOAT', '15', 'Any Hilbert peak < HilbertMinPeakMag is removed'),
('HilbertMinBBPeakMag', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'EchoAlgorithm', 'FLOAT', '20', 'Remove all peaks chronologically from beginning until peak > HilbertMinBBPeakMag'),
('AvgAnalysisTimePerWell', 'MEDMAN', NULL, @ClassifiedName, 'Survey', 'FLOAT', '46', 'Average nominal time duration (in milliseconds) to do survey analysis for each well.'),
('AvgCollectionTimePerWell', 'MEDMAN', NULL, @ClassifiedName, 'Survey', 'FLOAT', '46', 'Average nominal time duration (in milliseconds) to do survey collection for each well.'),
('NumEchosPerWell', 'MEDMAN', NULL, @ClassifiedName, 'Survey', 'INT', '1', 'How many echos per well when surveying.'),
('DimplePing', 'MEDMAN', NULL, @ClassifiedName, 'Survey', 'BOOL', 'false', 'Default is no dimple ping'),
('DoFiltering', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Homogeneous BB outlier', 'BOOL', 'true', 'Turn on/off BB outlier filtering.'),
('DoMedianFilter', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Homogeneous BB outlier', 'BOOL', 'true', 'Run BB outlier filter output thru a 3x3 median filter (recommended if not doing TB outlier filtering)'),
('Ksigma', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Homogeneous BB outlier', 'FLOAT', '4.0', 'BB outlier if |BB vpp - avg BB vpp| > k*sigma'),
('SolventConcHi', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'DMSO', 'FLOAT', '2.06', '%DMSO clipping - Calculated values outside this range will be clipped.'),
('SolventConcLo', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'DMSO', 'FLOAT', '1.481', '%DMSO clipping - Calculated values outside this range will be clipped.'),
('DoFiltering', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Inhomogeneous BB outlier', 'BOOL', 'true', 'Turn on/off BB outlier filtering.'),
('Ksigma', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Inhomogeneous BB outlier', 'FLOAT', '4.0', 'BB outlier if |BB vpp - avg BB vpp| > k*sigma'),
('DropXferTime', 'MEDMAN', NULL, @ClassifiedName, 'Timing', 'INT', '10', 'In milliseconds'),
('PlateXferTime', 'MEDMAN', NULL, @ClassifiedName, 'Timing', 'INT', '1000', 'In milliseconds'),
('PostXferTime', 'MEDMAN', NULL, @ClassifiedName, 'Timing', 'INT', '0', 'In milliseconds'),
('WellXferTime', 'MEDMAN', NULL, @ClassifiedName, 'Timing', 'INT', '143', 'In milliseconds'),
('WallTB2BBRatio', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'WellCenter', 'FLOAT', '0.1', 'TB/BB ratio for Wall During registration only'),
('WellRegToFRatio', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'WellCenter', 'FLOAT', '0.92', 'Tof Ratio for registration transducer height'),
('CompositionOutputType', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Calibration', 'STRING', 'Glycerol', 'Output types are: AQ, DMSO, Glycerol, MRayl, or NaCl'),
('ImpedanceBasedCal', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Calibration', 'BOOL', 'true', 'true = MRayl based calibration; false = DMSO based calibration'),
('UseVoltage', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Calibration', 'BOOL', 'true', 'true = voltage based LUT2D, false = energy based LUT2D'),
('UseImpedanceModel', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Calibration', 'BOOL', 'false', 'true = use model'),
('DoFiltering', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'TB outlier', 'BOOL', 'false', 'Not implemented yet'),
('PrePingDelay', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Print', 'FLOAT', '0', 'Default delay 0 (in milliseconds)'),
('TransZAdjustThreshold', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Print', 'FLOAT', '0.15', 'Transducer Z threshold for adjustment'),
('FluidHeightDiffToleranceMM', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Print', 'FLOAT', '0.3', 'mm'),
('FluidHeightRePingDelayMs', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Print', 'FLOAT', '10', 'msec'),
('PingAfterDropTransfer', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Print', 'BOOL', 'false', 'Default is no ping'),
('PingBeforeDropTransfer', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Print', 'BOOL', 'true', 'Default is no ping'),
('PostPingDelay', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Print', 'FLOAT', '0', 'Default delay 0 (in milliseconds)'),
('CalibrationType', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Calibration', 'STRING', 'LDV_AQ', 'General calibration type: Omics, Omics2, DMSO, DMSO2, LDV_AQ, LDV_DMSO, RES_AQ'),
('CalibrationVersion', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'Calibration', 'STRING', '2.5.14', 'Calibration version')
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
('PreambleType', @ClassifiedName, NULL, 'General', 'STRING', 'PrePing', NULL, NULL, NULL, NULL, NULL, NULL),
('DoPreamblePrePing', @ClassifiedName, NULL, 'General', 'BOOL', 'True', NULL, NULL, NULL, NULL, NULL, NULL),
('MISequenceType', @ClassifiedName, NULL, 'General', 'INT', '1', NULL, NULL, NULL, NULL, NULL, NULL),
('FFTPreambleResMHz', @ClassifiedName, NULL, 'General', 'FLOAT', '0.240', NULL, NULL, NULL, NULL, NULL, NULL),
('FFTPreambleAlg', @ClassifiedName, NULL, 'General', 'STRING', 'Alg_2', NULL, NULL, NULL, NULL, NULL, NULL),
('PrePingPreambleRHilbertMaxCycles', @ClassifiedName, NULL, 'General', 'FLOAT', '2.30', NULL, NULL, NULL, NULL, NULL, NULL),
('AllMISignals', @ClassifiedName, NULL, 'Capture', 'BOOL', 'False', NULL, NULL, NULL, NULL, NULL, NULL),
('OnlyLastSignals', @ClassifiedName, NULL, 'Capture', 'BOOL', 'False', NULL, NULL, NULL, NULL, NULL, NULL),
('RawSurveySignals', @ClassifiedName, NULL, 'Capture', 'BOOL', 'False', NULL, NULL, NULL, NULL, NULL, NULL),
('AvgSurveySignals', @ClassifiedName, NULL, 'Capture', 'BOOL', 'False', NULL, NULL, NULL, NULL, NULL, NULL),
('IndividualPingSignals', @ClassifiedName, NULL, 'Capture', 'BOOL', 'False', NULL, NULL, NULL, NULL, NULL, NULL),
('DropTransferOff', @ClassifiedName, 1, 'Setting', 'BOOL', 'True', NULL, NULL, NULL, NULL, NULL, NULL),
('DialationFactor', @ClassifiedName, 1, 'Setting', 'FLOAT', '1.000', NULL, NULL, NULL, NULL, NULL, NULL),
('MaxAmplitudeV', @ClassifiedName, 1, 'Setting', 'FLOAT', '4.500', NULL, NULL, NULL, NULL, NULL, NULL),
('UseZSweepCalcPower', @ClassifiedName, 1, 'Setting', 'BOOL', 'False', NULL, NULL, NULL, NULL, NULL, NULL),
('EjectDelayMsec', @ClassifiedName, 1, 'Setting', 'FLOAT', '0.000', NULL, NULL, NULL, NULL, NULL, NULL),
('MIDelayMsec', @ClassifiedName, 1, 'Setting', 'FLOAT', '40.000', NULL, NULL, NULL, NULL, NULL, NULL),
('ConstInterrPingAmp', @ClassifiedName, 1, 'Setting', 'BOOL', 'True', NULL, NULL, NULL, NULL, NULL, NULL),
('InterrogationPingAmpV', @ClassifiedName, 1, 'Setting', 'FLOAT', '0.800', NULL, NULL, NULL, NULL, NULL, NULL),
('StartDb', @ClassifiedName, 1, 'EjectSweep', 'FLOAT', '-2.600', NULL, NULL, NULL, NULL, NULL, NULL),
('StepSizeDb', @ClassifiedName, 1, 'EjectSweep', 'FLOAT', '0.200', NULL, NULL, NULL, NULL, NULL, NULL),
('MaxDb', @ClassifiedName, 1, 'EjectSweep', 'FLOAT', '0.000', NULL, NULL, NULL, NULL, NULL, NULL),
('FFTStartFreqMHz', @ClassifiedName, 1, 'Tuning', 'FLOAT', '4.0', NULL, NULL, NULL, NULL, NULL, NULL),
('FFTEndFreqMHz', @ClassifiedName, 1, 'Tuning', 'FLOAT', '8.5', NULL, NULL, NULL, NULL, NULL, NULL),
('MinWidthCycles', @ClassifiedName, 1, 'Tuning', 'FLOAT', '4.25', NULL, NULL, NULL, NULL, NULL, NULL),
('MaxNullSpaceMHz', @ClassifiedName, 1, 'Tuning', 'FLOAT', '3.00', NULL, NULL, NULL, NULL, NULL, NULL),
('RingingFreqThreshMHz', @ClassifiedName, 1, 'Tuning', 'FLOAT', '9.0', NULL, NULL, NULL, NULL, NULL, NULL),
('RingingAmpThreshV', @ClassifiedName, 1, 'Tuning', 'FLOAT', '100.0', NULL, NULL, NULL, NULL, NULL, NULL),
('TargetStartFreqMHz', @ClassifiedName, 1, 'Tuning', 'FLOAT', '5.4', NULL, NULL, NULL, NULL, NULL, NULL),
('TargetEndFreqMHz', @ClassifiedName, 1, 'Tuning', 'FLOAT', '7.0', NULL, NULL, NULL, NULL, NULL, NULL),
('MinNullSpacingMHz', @ClassifiedName, 1, 'Tuning', 'FLOAT', '1.50', NULL, NULL, NULL, NULL, NULL, NULL),
('MinPeakSepCycles', @ClassifiedName, 1, 'Tuning', 'FLOAT', '5.0', NULL, NULL, NULL, NULL, NULL, NULL),
('MinRingFreqMHz', @ClassifiedName, 1, 'Tuning', 'FLOAT', '8.0', NULL, NULL, NULL, NULL, NULL, NULL),
('MinPeakFactor', @ClassifiedName, 1, 'Tuning', 'FLOAT', '0.90', NULL, NULL, NULL, NULL, NULL, NULL),
('MaxPeakFactor', @ClassifiedName, 1, 'Tuning', 'FLOAT', '3.25', NULL, NULL, NULL, NULL, NULL, NULL),
('EnableImpedanceBasedTPF', @ClassifiedName, 1, 'Tuning', 'BOOL', 'True', NULL, NULL, NULL, NULL, NULL, NULL),
('ImpedanceToTPFFactor', @ClassifiedName, 1, 'Tuning', 'FLOAT', '3.00', NULL, NULL, NULL, NULL, NULL, NULL),
('MinTargetPeakHeight', @ClassifiedName, 1, 'Tuning', 'INT', '90', NULL, NULL, NULL, NULL, NULL, NULL),
('OverPowerAlgoType', @ClassifiedName, 1, 'Tuning', 'INT', '2', NULL, NULL, NULL, NULL, NULL, NULL),
('MinVrms', @ClassifiedName, 1, 'Tuning', 'FLOAT', '0.00', NULL, NULL, NULL, NULL, NULL, NULL),
('MatrixStartCycles', @ClassifiedName, 1, 'Tuning', 'FLOAT', '2.0', NULL, NULL, NULL, NULL, NULL, NULL),
('MatrixWidthCycles', @ClassifiedName, 1, 'Tuning', 'FLOAT', '10.0', NULL, NULL, NULL, NULL, NULL, NULL),
('MoundStartSamples', @ClassifiedName, 1, 'Tuning', 'INT', '0', NULL, NULL, NULL, NULL, NULL, NULL),
('MoundStopSamples', @ClassifiedName, 1, 'Tuning', 'INT', '0', NULL, NULL, NULL, NULL, NULL, NULL),
('MinValidDips', @ClassifiedName, 1, 'Tuning', 'INT', '3', NULL, NULL, NULL, NULL, NULL, NULL),
('MinNullFreqSkew', @ClassifiedName, 1, 'Tuning', 'FLOAT', '0.00', NULL, NULL, NULL, NULL, NULL, NULL),
('MaxNullFreqSkew', @ClassifiedName, 1, 'Tuning', 'FLOAT', '0.00', NULL, NULL, NULL, NULL, NULL, NULL),
('MinNullAmplBalance', @ClassifiedName, 1, 'Tuning', 'FLOAT', '0.00', NULL, NULL, NULL, NULL, NULL, NULL),
('MaxNullAmplBalance', @ClassifiedName, 1, 'Tuning', 'FLOAT', '0.00', NULL, NULL, NULL, NULL, NULL, NULL),
('FFTSizeMHz', @ClassifiedName, 1, 'Override', 'INT', '480', NULL, NULL, NULL, NULL, NULL, NULL),
('InterrogationDelayUs', @ClassifiedName, 1, 'Override', 'FLOAT', '180.000', NULL, NULL, NULL, NULL, NULL, NULL),
('EjectionOffsetUm', @ClassifiedName, 1, 'Offset', 'FLOAT', '0.000', NULL, NULL, NULL, NULL, NULL, NULL),
('Thresh2XferBiasDb', @ClassifiedName, 1, 'Offset', 'FLOAT', '0.000', NULL, NULL, NULL, NULL, NULL, NULL)
PRINT(LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into MIPConfiguration for PlateType: "'+@ClassifiedName+'".')



INSERT INTO PingParameters (InstrumentName, PlateTypeName, TransducerName, Amplitude, TOFWindowStart, TOFWindowEnd, EchoThreshMult, FileName)
VALUES 
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1.4, 29.28312, 45.66712, 15.0, 'PingBurst')
PRINT(LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into PingParameters for PlateType: "'+@ClassifiedName+'".')



INSERT INTO PlateSignature (InstrumentName, PlateTypeName, TransducerName, Row, Col, Description, A, B, C, Constant)
VALUES 
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 0, 'A1', 0.0, 0.0, -0.6698640608411526, 2.294912140481698),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 1, 'A2', 0.0, 0.0, -0.6621044305212354, 2.2938477908616837),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 2, 'A3', 0.0, 0.0, -0.668120707404847, 2.2964047841197934),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 3, 'A4', 0.0, 0.0, -0.6693563726603444, 2.2973347464347524),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 4, 'A5', 0.0, 0.0, -0.6707939964992262, 2.298067041715327),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 5, 'A6', 0.0, 0.0, -0.6684815896930313, 2.296942200318366),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 6, 'A7', 0.0, 0.0, -0.670967961060545, 2.2963918578082136),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 7, 'A8', 0.0, 0.0, -0.6699431404248484, 2.2961393282003497),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 8, 'A9', 0.0, 0.0, -0.6705106105488682, 2.2962360915002167),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 9, 'A10', 0.0, 0.0, -0.668428570744105, 2.294768714908836),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 10, 'A11', 0.0, 0.0, -0.671969089733654, 2.2965888946968893),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 11, 'A12', 0.0, 0.0, -0.6699658784493137, 2.293092626296901),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 12, 'A13', 0.0, 0.0, -0.673321275260652, 2.295546668635665),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 13, 'A14', 0.0, 0.0, -0.6684797777917317, 2.2931290641899706),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 14, 'A15', 0.0, 0.0, -0.6713841724921347, 2.296820998417416),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 15, 'A16', 0.0, 0.0, -0.6725689125281327, 2.297345870918386),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 16, 'A17', 0.0, 0.0, -0.66880890091625, 2.2970888749887357),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 17, 'A18', 0.0, 0.0, -0.6692354937641337, 2.294739832022288),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 18, 'A19', 0.0, 0.0, -0.6667324628759164, 2.296289751506224),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 19, 'A20', 0.0, 0.0, -0.6695474515738629, 2.2969356853095517),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 20, 'A21', 0.0, 0.0, -0.6700782701869638, 2.29820234357497),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 21, 'A22', 0.0, 0.0, -0.6680493854539494, 2.296803442969691),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 22, 'A23', 0.0, 0.0, -0.6674841719655826, 2.2971590514215943),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 0, 23, 'A24', 0.0, 0.0, -0.6686948878930129, 2.293642133899721),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 0, 'B1', 0.0, 0.0, -0.6626476484167814, 2.2942044269424477),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 1, 'B2', 0.0, 0.0, -0.6679294935010467, 2.299723971001104),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 2, 'B3', 0.0, 0.0, -0.6689526319584115, 2.2994020857203266),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 3, 'B4', 0.0, 0.0, -0.6712397371212797, 2.298920349618808),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 4, 'B5', 0.0, 0.0, -0.674396686257011, 2.3026857743742775),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 5, 'B6', 0.0, 0.0, -0.6716888753269348, 2.3006590652193784),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 6, 'B7', 0.0, 0.0, -0.6707608098829676, 2.29891296668777),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 7, 'B8', 0.0, 0.0, -0.6697491451889955, 2.2961962249333605),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 8, 'B9', 0.0, 0.0, -0.672992049596586, 2.2964330216991393),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 9, 'B10', 0.0, 0.0, -0.673880934187919, 2.2966134333784676),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 10, 'B11', 0.0, 0.0, -0.6733580125829881, 2.296125033902016),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 11, 'B12', 0.0, 0.0, -0.6729100839192959, 2.2978991925907044),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 12, 'B13', 0.0, 0.0, -0.6712003646461633, 2.297383309044919),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 13, 'B14', 0.0, 0.0, -0.673950702515495, 2.296848989385246),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 14, 'B15', 0.0, 0.0, -0.6740264428955061, 2.296345874064842),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 15, 'B16', 0.0, 0.0, -0.6733827415709261, 2.2965528314939028),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 16, 'B17', 0.0, 0.0, -0.671832947697419, 2.2967777086291536),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 17, 'B18', 0.0, 0.0, -0.6714818308410774, 2.2987040806839625),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 18, 'B19', 0.0, 0.0, -0.6714620499133325, 2.29859234552458),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 19, 'B20', 0.0, 0.0, -0.672303810263658, 2.2980054895166675),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 20, 'B21', 0.0, 0.0, -0.6740828389309482, 2.297796869600018),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 21, 'B22', 0.0, 0.0, -0.669841833122959, 2.2969581694840784),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 22, 'B23', 0.0, 0.0, -0.6717347748428623, 2.2998425911815716),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 1, 23, 'B24', 0.0, 0.0, -0.6711262315323068, 2.297015517445928),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 0, 'C1', 0.0, 0.0, -0.6670713323257434, 2.29440249794874),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 1, 'C2', 0.0, 0.0, -0.6732220301367758, 2.2984823689070737),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 2, 'C3', 0.0, 0.0, -0.6725619664845609, 2.2965275861503507),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 3, 'C4', 0.0, 0.0, -0.6714309102453198, 2.295101749584189),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 4, 'C5', 0.0, 0.0, -0.6758942490932168, 2.2982434799845493),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 5, 'C6', 0.0, 0.0, -0.6704918657842781, 2.297214140347866),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 6, 'C7', 0.0, 0.0, -0.6689566725086045, 2.2959648297777937),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 7, 'C8', 0.0, 0.0, -0.6782324962949144, 2.2992241288220576),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 8, 'C9', 0.0, 0.0, -0.6749413496261887, 2.2937727836870807),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 9, 'C10', 0.0, 0.0, -0.6758262362457357, 2.294614519587216),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 10, 'C11', 0.0, 0.0, -0.6750712591829868, 2.293849898399947),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 11, 'C12', 0.0, 0.0, -0.6740971032656394, 2.296426933932568),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 12, 'C13', 0.0, 0.0, -0.670599286047043, 2.2960382786270133),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 13, 'C14', 0.0, 0.0, -0.6719611052477502, 2.2928196591685563),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 14, 'C15', 0.0, 0.0, -0.6751236199824527, 2.2946386053138017),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 15, 'C16', 0.0, 0.0, -0.6743314758498843, 2.2947091658658842),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 16, 'C17', 0.0, 0.0, -0.6752583139462004, 2.2962869784002193),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 17, 'C18', 0.0, 0.0, -0.671375469709064, 2.296277251691274),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 18, 'C19', 0.0, 0.0, -0.672099052435981, 2.2992876848105674),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 19, 'C20', 0.0, 0.0, -0.6727975778027578, 2.298114682100121),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 20, 'C21', 0.0, 0.0, -0.6731581666907548, 2.2969601768718784),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 21, 'C22', 0.0, 0.0, -0.676364607665517, 2.29954715281017),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 22, 'C23', 0.0, 0.0, -0.6726047242541917, 2.298032685857884),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 2, 23, 'C24', 0.0, 0.0, -0.6731669491247935, 2.296902309092955),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 0, 'D1', 0.0, 0.0, -0.670675189578059, 2.2958970213383627),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 1, 'D2', 0.0, 0.0, -0.6710292702098304, 2.2967302699133447),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 2, 'D3', 0.0, 0.0, -0.6718212734065202, 2.2963008041535455),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 3, 'D4', 0.0, 0.0, -0.6710001295465218, 2.295681124231685),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 4, 'D5', 0.0, 0.0, -0.6685462508782445, 2.296357173275849),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 5, 'D6', 0.0, 0.0, -0.6698193134536963, 2.2986163877764),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 6, 'D7', 0.0, 0.0, -0.6726049112139008, 2.2969342527811487),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 7, 'D8', 0.0, 0.0, -0.6741466136005183, 2.2949015036006752),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 8, 'D9', 0.0, 0.0, -0.6757064925580133, 2.2947769680662264),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 9, 'D10', 0.0, 0.0, -0.675238726821414, 2.292655757933264),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 10, 'D11', 0.0, 0.0, -0.6771924601573273, 2.293379538769741),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 11, 'D12', 0.0, 0.0, -0.6769190162494572, 2.298156440818864),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 12, 'D13', 0.0, 0.0, -0.6722609171027591, 2.296414460124175),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 13, 'D14', 0.0, 0.0, -0.675728841661014, 2.29349875563265),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 14, 'D15', 0.0, 0.0, -0.6770955164664827, 2.292511243907662),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 15, 'D16', 0.0, 0.0, -0.6747431020903016, 2.2927558693924346),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 16, 'D17', 0.0, 0.0, -0.6752455707942522, 2.2940132330344305),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 17, 'D18', 0.0, 0.0, -0.675624454227072, 2.2963592883046817),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 18, 'D19', 0.0, 0.0, -0.670815725786675, 2.2966945549300632),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 19, 'D20', 0.0, 0.0, -0.6738469952202579, 2.297936155117875),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 20, 'D21', 0.0, 0.0, -0.672808673660757, 2.2951262419941325),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 21, 'D22', 0.0, 0.0, -0.6750935937351007, 2.296082749537625),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 22, 'D23', 0.0, 0.0, -0.6729585203484274, 2.2962524422927992),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 3, 23, 'D24', 0.0, 0.0, -0.6736716767438704, 2.295368549401363),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 0, 'E1', 0.0, 0.0, -0.6716467479883564, 2.2929343777079305),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 1, 'E2', 0.0, 0.0, -0.677176414666499, 2.295581725062934),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 2, 'E3', 0.0, 0.0, -0.6739885384208666, 2.293370008837316),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 3, 'E4', 0.0, 0.0, -0.6742615355909278, 2.295236374655778),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 4, 'E5', 0.0, 0.0, -0.6692955009312948, 2.294548051073145),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 5, 'E6', 0.0, 0.0, -0.6692669328763452, 2.2944692528604342),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 6, 'E7', 0.0, 0.0, -0.6737203645529057, 2.2948895848337583),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 7, 'E8', 0.0, 0.0, -0.6760894028966321, 2.294359726898678),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 8, 'E9', 0.0, 0.0, -0.6739118623495478, 2.2913018992519927),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 9, 'E10', 0.0, 0.0, -0.6779007615139603, 2.2913497005723693),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 10, 'E11', 0.0, 0.0, -0.6766143288187486, 2.291461883190495),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 11, 'E12', 0.0, 0.0, -0.6768223771654477, 2.2966955106055824),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 12, 'E13', 0.0, 0.0, -0.6718793081671987, 2.2950037222710082),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 13, 'E14', 0.0, 0.0, -0.675406036848501, 2.292892828407209),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 14, 'E15', 0.0, 0.0, -0.6773745957358517, 2.292542955852653),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 15, 'E16', 0.0, 0.0, -0.6717859484730238, 2.2902188308444598),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 16, 'E17', 0.0, 0.0, -0.6740316954778707, 2.29358723290189),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 17, 'E18', 0.0, 0.0, -0.6726156588352709, 2.2937856301227657),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 18, 'E19', 0.0, 0.0, -0.6738501941692078, 2.297241699589001),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 19, 'E20', 0.0, 0.0, -0.671347284891579, 2.2963566868454266),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 20, 'E21', 0.0, 0.0, -0.6703410737346001, 2.2952037822632807),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 21, 'E22', 0.0, 0.0, -0.6752464542846952, 2.2967780625018936),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 22, 'E23', 0.0, 0.0, -0.6796116099517432, 2.2980283918680455),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 4, 23, 'E24', 0.0, 0.0, -0.6745800333239506, 2.2939311285258728),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 0, 'F1', 0.0, 0.0, -0.6738222929251209, 2.2939745922267676),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 1, 'F2', 0.0, 0.0, -0.6732094218790216, 2.294296147909496),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 2, 'F3', 0.0, 0.0, -0.6716183489896461, 2.294485922665516),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 3, 'F4', 0.0, 0.0, -0.6718019939022564, 2.2959117233987674),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 4, 'F5', 0.0, 0.0, -0.6680666287608286, 2.295552044528877),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 5, 'F6', 0.0, 0.0, -0.6704502361671318, 2.2944358102301523),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 6, 'F7', 0.0, 0.0, -0.6735878242242189, 2.2944570001314335),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 7, 'F8', 0.0, 0.0, -0.6755011966506055, 2.2945510350526352),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 8, 'F9', 0.0, 0.0, -0.676155849873984, 2.2926710592685384),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 9, 'F10', 0.0, 0.0, -0.6762443895665787, 2.291255669322312),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 10, 'F11', 0.0, 0.0, -0.6771753025822517, 2.2921526116744593),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 11, 'F12', 0.0, 0.0, -0.6742422245251171, 2.2951325626428267),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 12, 'F13', 0.0, 0.0, -0.6725932042421844, 2.2953714729368033),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 13, 'F14', 0.0, 0.0, -0.6766167988281315, 2.2937084298045725),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 14, 'F15', 0.0, 0.0, -0.6761686062362359, 2.290826217230715),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 15, 'F16', 0.0, 0.0, -0.6766636526240062, 2.2916464266521737),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 16, 'F17', 0.0, 0.0, -0.6737838577973769, 2.2920540634912343),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 17, 'F18', 0.0, 0.0, -0.6739223687313685, 2.2934874687224776),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 18, 'F19', 0.0, 0.0, -0.6737376819068489, 2.296179598617406),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 19, 'F20', 0.0, 0.0, -0.6754993560544995, 2.2975009847865926),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 20, 'F21', 0.0, 0.0, -0.674665911295101, 2.2964809713257783),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 21, 'F22', 0.0, 0.0, -0.6758079330507444, 2.2974899265355675),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 22, 'F23', 0.0, 0.0, -0.6778562463532729, 2.2965600364095944),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 5, 23, 'F24', 0.0, 0.0, -0.6759590156644932, 2.292528075856359),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 0, 'G1', 0.0, 0.0, -0.674334805414199, 2.292686492474196),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 1, 'G2', 0.0, 0.0, -0.6742453237429449, 2.2940219822179526),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 2, 'G3', 0.0, 0.0, -0.6732205585980615, 2.2944065509414684),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 3, 'G4', 0.0, 0.0, -0.6746953005753331, 2.296509524494591),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 4, 'G5', 0.0, 0.0, -0.6702917258888748, 2.293777698109939),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 5, 'G6', 0.0, 0.0, -0.6726070675067374, 2.294448342583681),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 6, 'G7', 0.0, 0.0, -0.6723829959219239, 2.2926015175001875),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 7, 'G8', 0.0, 0.0, -0.6732194653224141, 2.2916413472020376),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 8, 'G9', 0.0, 0.0, -0.6753440063915902, 2.292006908270525),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 9, 'G10', 0.0, 0.0, -0.6776407449014983, 2.2913742598060867),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 10, 'G11', 0.0, 0.0, -0.6781429396193376, 2.2933008517054065),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 11, 'G12', 0.0, 0.0, -0.6739728942930391, 2.2962292146656456),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 12, 'G13', 0.0, 0.0, -0.6724035447139436, 2.294533803977112),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 13, 'G14', 0.0, 0.0, -0.6737690174114771, 2.2922355483441175),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 14, 'G15', 0.0, 0.0, -0.6771977112733277, 2.292554387020242),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 15, 'G16', 0.0, 0.0, -0.6779074889707059, 2.2937152979436726),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 16, 'G17', 0.0, 0.0, -0.6765590114087553, 2.2935668442961488),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 17, 'G18', 0.0, 0.0, -0.6747694639589048, 2.2943823793291585),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 18, 'G19', 0.0, 0.0, -0.6726064866842498, 2.2945569162564925),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 19, 'G20', 0.0, 0.0, -0.6725877492950142, 2.2954432860843226),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 20, 'G21', 0.0, 0.0, -0.6759582160063761, 2.298856898184607),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 21, 'G22', 0.0, 0.0, -0.6728571447118844, 2.2966323342882795),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 22, 'G23', 0.0, 0.0, -0.6748235995461065, 2.2956944129585986),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 6, 23, 'G24', 0.0, 0.0, -0.6752398131095807, 2.292974888376088),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 0, 'H1', 0.0, 0.0, -0.6705643430252055, 2.29177780545614),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 1, 'H2', 0.0, 0.0, -0.6700279268856341, 2.2965913607929975),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 2, 'H3', 0.0, 0.0, -0.6704528156553012, 2.297479850869563),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 3, 'H4', 0.0, 0.0, -0.6707590267323901, 2.2974243792882993),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 4, 'H5', 0.0, 0.0, -0.6706313747788764, 2.2957953322011337),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 5, 'H6', 0.0, 0.0, -0.671052850886869, 2.29547321671162),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 6, 'H7', 0.0, 0.0, -0.6727510812403648, 2.2950277478611336),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 7, 'H8', 0.0, 0.0, -0.6765276044483187, 2.295768529493283),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 8, 'H9', 0.0, 0.0, -0.6762760463947858, 2.2943301670822835),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 9, 'H10', 0.0, 0.0, -0.6766435292940362, 2.293599321811042),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 10, 'H11', 0.0, 0.0, -0.6762340506982373, 2.2949922147088944),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 11, 'H12', 0.0, 0.0, -0.6746833586244714, 2.2959264599755986),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 12, 'H13', 0.0, 0.0, -0.6751175221846818, 2.295956564719331),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 13, 'H14', 0.0, 0.0, -0.6746267822689143, 2.2944079873152052),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 14, 'H15', 0.0, 0.0, -0.6777146756158234, 2.2942008383770283),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 15, 'H16', 0.0, 0.0, -0.6765277701287744, 2.294090465349977),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 16, 'H17', 0.0, 0.0, -0.6786529099336845, 2.2959739621885693),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 17, 'H18', 0.0, 0.0, -0.6752931184899521, 2.295139056662294),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 18, 'H19', 0.0, 0.0, -0.6752047439134669, 2.296759681423936),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 19, 'H20', 0.0, 0.0, -0.6763536894925827, 2.297566795224316),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 20, 'H21', 0.0, 0.0, -0.6739748858441552, 2.2981804709893905),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 21, 'H22', 0.0, 0.0, -0.6736376490037191, 2.2979603393215933),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 22, 'H23', 0.0, 0.0, -0.6731293900229207, 2.29663583274851),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 7, 23, 'H24', 0.0, 0.0, -0.6733860199087485, 2.2934564350992774),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 8, 0, 'I1', 0.0, 0.0, -0.6720893340943725, 2.291633153406391),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 8, 1, 'I2', 0.0, 0.0, -0.671356005320792, 2.294391824864437),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 8, 2, 'I3', 0.0, 0.0, -0.6727860381168603, 2.2955278379599204),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 8, 3, 'I4', 0.0, 0.0, -0.6713536385894934, 2.2946386072061635),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 8, 4, 'I5', 0.0, 0.0, -0.673786293388087, 2.2957635766645947),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 8, 5, 'I6', 0.0, 0.0, -0.6717005425942842, 2.2919949519638956),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 8, 6, 'I7', 0.0, 0.0, -0.6742772984388727, 2.29399030958724),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 8, 7, 'I8', 0.0, 0.0, -0.6745307611490305, 2.291942521119998),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 8, 8, 'I9', 0.0, 0.0, -0.6766515455515428, 2.293322834360579),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 8, 9, 'I10', 0.0, 0.0, -0.6765599327760534, 2.292125895821195),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 8, 10, 'I11', 0.0, 0.0, -0.6772285484711599, 2.294129296981613),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 8, 11, 'I12', 0.0, 0.0, -0.6735195887766744, 2.295298191013463),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 8, 12, 'I13', 0.0, 0.0, -0.6751093210935525, 2.2947016309233894),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 8, 13, 'I14', 0.0, 0.0, -0.6746014202211443, 2.2937262299884926),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 8, 14, 'I15', 0.0, 0.0, -0.6754721666625834, 2.292068164737899),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 8, 15, 'I16', 0.0, 0.0, -0.6751673128156948, 2.2922241108623367),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 8, 16, 'I17', 0.0, 0.0, -0.6774172380186215, 2.294403601113257),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 8, 17, 'I18', 0.0, 0.0, -0.6751637108911929, 2.294348699468507),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 8, 18, 'I19', 0.0, 0.0, -0.6733215293459055, 2.2944578673708182),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 8, 19, 'I20', 0.0, 0.0, -0.6731028812887365, 2.296215919589136),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 8, 20, 'I21', 0.0, 0.0, -0.6722167926598389, 2.2965623044929577),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 8, 21, 'I22', 0.0, 0.0, -0.6730965181104119, 2.2970569900539233),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 8, 22, 'I23', 0.0, 0.0, -0.6734795665394143, 2.295103962992392),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 8, 23, 'I24', 0.0, 0.0, -0.6737410150478067, 2.2900535345310873),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 9, 0, 'J1', 0.0, 0.0, -0.6698063764324264, 2.2891596648725128),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 9, 1, 'J2', 0.0, 0.0, -0.6717401872346581, 2.293337684979352),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 9, 2, 'J3', 0.0, 0.0, -0.6724932335052497, 2.29522925891269),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 9, 3, 'J4', 0.0, 0.0, -0.6681761790121036, 2.293374568932761),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 9, 4, 'J5', 0.0, 0.0, -0.6694551586605618, 2.294709057274589),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 9, 5, 'J6', 0.0, 0.0, -0.670205211535953, 2.294000218208616),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 9, 6, 'J7', 0.0, 0.0, -0.6711285223894143, 2.292152207761226),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 9, 7, 'J8', 0.0, 0.0, -0.6735010534517195, 2.2920891136302655),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 9, 8, 'J9', 0.0, 0.0, -0.6734255574109465, 2.290937667642688),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 9, 9, 'J10', 0.0, 0.0, -0.6773318542249319, 2.291948610183239),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 9, 10, 'J11', 0.0, 0.0, -0.6758430124595769, 2.292514408196777),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 9, 11, 'J12', 0.0, 0.0, -0.6723657122389678, 2.294703532518291),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 9, 12, 'J13', 0.0, 0.0, -0.6737462931952358, 2.2957399780232124),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 9, 13, 'J14', 0.0, 0.0, -0.6733747244369124, 2.290870212957611),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 9, 14, 'J15', 0.0, 0.0, -0.6754008333253387, 2.2894732095161605),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 9, 15, 'J16', 0.0, 0.0, -0.677930029242835, 2.2923415271061014),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 9, 16, 'J17', 0.0, 0.0, -0.6763551278914126, 2.2926518152613276),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 9, 17, 'J18', 0.0, 0.0, -0.6764819265967734, 2.2944763829202484),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 9, 18, 'J19', 0.0, 0.0, -0.6758633588145795, 2.2960448912355456),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 9, 19, 'J20', 0.0, 0.0, -0.671966748939617, 2.2942857659191396),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 9, 20, 'J21', 0.0, 0.0, -0.6715872940984291, 2.2936219269445295),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 9, 21, 'J22', 0.0, 0.0, -0.6743229022809228, 2.295085157424631),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 9, 22, 'J23', 0.0, 0.0, -0.6725812990196269, 2.291016505437492),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 9, 23, 'J24', 0.0, 0.0, -0.6723025353361131, 2.2876407135164447),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 10, 0, 'K1', 0.0, 0.0, -0.6700044564444558, 2.288353575524736),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 10, 1, 'K2', 0.0, 0.0, -0.6744120547434473, 2.2917332228443565),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 10, 2, 'K3', 0.0, 0.0, -0.6723198847705439, 2.290846087798266),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 10, 3, 'K4', 0.0, 0.0, -0.671244646354479, 2.2926868193053864),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 10, 4, 'K5', 0.0, 0.0, -0.6708513930569078, 2.2937138383513758),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 10, 5, 'K6', 0.0, 0.0, -0.6730581117340557, 2.294314892862766),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 10, 6, 'K7', 0.0, 0.0, -0.6704392678064733, 2.2901815670191565),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 10, 7, 'K8', 0.0, 0.0, -0.6732280320632469, 2.290364506827335),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 10, 8, 'K9', 0.0, 0.0, -0.6750028198439852, 2.290849809026479),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 10, 9, 'K10', 0.0, 0.0, -0.6754113278447548, 2.2889444071403457),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 10, 10, 'K11', 0.0, 0.0, -0.6742845231910873, 2.290278984663469),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 10, 11, 'K12', 0.0, 0.0, -0.6717518697465389, 2.2929253991311325),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 10, 12, 'K13', 0.0, 0.0, -0.6695583903944836, 2.292340073817123),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 10, 13, 'K14', 0.0, 0.0, -0.6751339233582887, 2.291950808821551),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 10, 14, 'K15', 0.0, 0.0, -0.6770593532616767, 2.290774571669871),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 10, 15, 'K16', 0.0, 0.0, -0.6774368757526026, 2.291812616054673),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 10, 16, 'K17', 0.0, 0.0, -0.6748502883084502, 2.292600851418123),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 10, 17, 'K18', 0.0, 0.0, -0.6736309100981467, 2.2930575877321924),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 10, 18, 'K19', 0.0, 0.0, -0.671761225708284, 2.2933166116188404),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 10, 19, 'K20', 0.0, 0.0, -0.6721592624545304, 2.294295206116295),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 10, 20, 'K21', 0.0, 0.0, -0.6705129070329124, 2.29362373087236),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 10, 21, 'K22', 0.0, 0.0, -0.6744633766514746, 2.2944810560506776),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 10, 22, 'K23', 0.0, 0.0, -0.6763172076726116, 2.293028963506026),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 10, 23, 'K24', 0.0, 0.0, -0.6708838440646991, 2.2848382852054527),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 11, 0, 'L1', 0.0, 0.0, -0.6669131931546529, 2.289179473546007),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 11, 1, 'L2', 0.0, 0.0, -0.6725212998703655, 2.2929948364640595),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 11, 2, 'L3', 0.0, 0.0, -0.6711883104814088, 2.292759540528555),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 11, 3, 'L4', 0.0, 0.0, -0.6710977970462073, 2.294390687432553),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 11, 4, 'L5', 0.0, 0.0, -0.6684018172232288, 2.2949359500895934),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 11, 5, 'L6', 0.0, 0.0, -0.6702567389682005, 2.294827921679621),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 11, 6, 'L7', 0.0, 0.0, -0.6693305610703569, 2.292582859709457),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 11, 7, 'L8', 0.0, 0.0, -0.6724620640070808, 2.292588800046866),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 11, 8, 'L9', 0.0, 0.0, -0.6752435968070407, 2.2922151836879068),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 11, 9, 'L10', 0.0, 0.0, -0.6760132419109386, 2.2908638347074417),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 11, 10, 'L11', 0.0, 0.0, -0.6752474335200852, 2.291631985579883),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 11, 11, 'L12', 0.0, 0.0, -0.6711301014996883, 2.2931797482436598),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 11, 12, 'L13', 0.0, 0.0, -0.6733586035011702, 2.2942734805014577),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 11, 13, 'L14', 0.0, 0.0, -0.6741732094000616, 2.2909865367381106),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 11, 14, 'L15', 0.0, 0.0, -0.6782407176145671, 2.291478204806531),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 11, 15, 'L16', 0.0, 0.0, -0.6730432519675648, 2.289631766859721),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 11, 16, 'L17', 0.0, 0.0, -0.6728418907632954, 2.2917801303133687),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 11, 17, 'L18', 0.0, 0.0, -0.6740682060177494, 2.2942285799885527),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 11, 18, 'L19', 0.0, 0.0, -0.6683811353622571, 2.2906719647393086),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 11, 19, 'L20', 0.0, 0.0, -0.6698703490284356, 2.2941292223195133),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 11, 20, 'L21', 0.0, 0.0, -0.6708099799835179, 2.292207377768341),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 11, 21, 'L22', 0.0, 0.0, -0.6754972100975624, 2.2931939646460537),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 11, 22, 'L23', 0.0, 0.0, -0.6755903707922953, 2.292641653342885),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 11, 23, 'L24', 0.0, 0.0, -0.6695137998080435, 2.2885930715010416),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 12, 0, 'M1', 0.0, 0.0, -0.6654422694629949, 2.2863868832935066),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 12, 1, 'M2', 0.0, 0.0, -0.6700186047159197, 2.2920230142532745),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 12, 2, 'M3', 0.0, 0.0, -0.6715253073833031, 2.2915550500158797),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 12, 3, 'M4', 0.0, 0.0, -0.6724518002414387, 2.2923624758595085),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 12, 4, 'M5', 0.0, 0.0, -0.6706569879364352, 2.293351791154542),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 12, 5, 'M6', 0.0, 0.0, -0.6688046532855563, 2.294157692015173),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 12, 6, 'M7', 0.0, 0.0, -0.6694320505363063, 2.292310044074615),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 12, 7, 'M8', 0.0, 0.0, -0.671138092735751, 2.2908420779684233),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 12, 8, 'M9', 0.0, 0.0, -0.6734801853129535, 2.29213506802691),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 12, 9, 'M10', 0.0, 0.0, -0.6745011314596571, 2.2903231487425733),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 12, 10, 'M11', 0.0, 0.0, -0.673489531411621, 2.290279096545087),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 12, 11, 'M12', 0.0, 0.0, -0.6690615532410178, 2.292243970258258),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 12, 12, 'M13', 0.0, 0.0, -0.6715069469785698, 2.2936636007876605),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 12, 13, 'M14', 0.0, 0.0, -0.6714169383724872, 2.2901436245228686),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 12, 14, 'M15', 0.0, 0.0, -0.6747728560304728, 2.2908619763475424),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 12, 15, 'M16', 0.0, 0.0, -0.6725449185701441, 2.2913216748187692),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 12, 16, 'M17', 0.0, 0.0, -0.670569946709451, 2.290969261695904),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 12, 17, 'M18', 0.0, 0.0, -0.6720631642149585, 2.2934657308021698),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 12, 18, 'M19', 0.0, 0.0, -0.6674833742354656, 2.293566337715863),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 12, 19, 'M20', 0.0, 0.0, -0.6685472556204399, 2.2927687086469706),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 12, 20, 'M21', 0.0, 0.0, -0.6710084099909208, 2.291906757421946),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 12, 21, 'M22', 0.0, 0.0, -0.6695425418073463, 2.291686062132284),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 12, 22, 'M23', 0.0, 0.0, -0.6713808710997224, 2.293486524865718),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 12, 23, 'M24', 0.0, 0.0, -0.6669922814808432, 2.2884746341149067),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 13, 0, 'N1', 0.0, 0.0, -0.6622665685683374, 2.2893060789111783),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 13, 1, 'N2', 0.0, 0.0, -0.6655162743010029, 2.2926013184429084),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 13, 2, 'N3', 0.0, 0.0, -0.667385948769396, 2.292818220036446),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 13, 3, 'N4', 0.0, 0.0, -0.668773625072774, 2.293293441349323),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 13, 4, 'N5', 0.0, 0.0, -0.6685781539384369, 2.2937701259358385),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 13, 5, 'N6', 0.0, 0.0, -0.6675817042034223, 2.294522101561486),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 13, 6, 'N7', 0.0, 0.0, -0.6659312417393541, 2.292933138483326),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 13, 7, 'N8', 0.0, 0.0, -0.6691761830319125, 2.2920471301598826),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 13, 8, 'N9', 0.0, 0.0, -0.6724753225026214, 2.292239499961657),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 13, 9, 'N10', 0.0, 0.0, -0.6731221388330503, 2.2918533170235422),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 13, 10, 'N11', 0.0, 0.0, -0.672781412235864, 2.291711496989048),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 13, 11, 'N12', 0.0, 0.0, -0.6719763398454872, 2.2943016235979896),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 13, 12, 'N13', 0.0, 0.0, -0.6693986772326801, 2.2936845283278355),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 13, 13, 'N14', 0.0, 0.0, -0.6710800111493191, 2.2904762944315733),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 13, 14, 'N15', 0.0, 0.0, -0.670862356764858, 2.2894280455102427),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 13, 15, 'N16', 0.0, 0.0, -0.6712736850292821, 2.290156478477288),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 13, 16, 'N17', 0.0, 0.0, -0.6705172379193667, 2.2910897532323697),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 13, 17, 'N18', 0.0, 0.0, -0.6680877810652798, 2.2932646758166904),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 13, 18, 'N19', 0.0, 0.0, -0.6667031644909697, 2.291663699524055),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 13, 19, 'N20', 0.0, 0.0, -0.670269277940093, 2.2920487375493375),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 13, 20, 'N21', 0.0, 0.0, -0.6701559294867776, 2.291623475977309),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 13, 21, 'N22', 0.0, 0.0, -0.6689337213050991, 2.2910955155119264),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 13, 22, 'N23', 0.0, 0.0, -0.6702589736083073, 2.292974908252165),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 13, 23, 'N24', 0.0, 0.0, -0.6629141056984852, 2.2882688156360547),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 14, 0, 'O1', 0.0, 0.0, -0.6618640894167548, 2.2906678524022213),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 14, 1, 'O2', 0.0, 0.0, -0.6637405753112533, 2.292925850635816),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 14, 2, 'O3', 0.0, 0.0, -0.6673512789263996, 2.2935838588288147),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 14, 3, 'O4', 0.0, 0.0, -0.6688239932854666, 2.29252208179721),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 14, 4, 'O5', 0.0, 0.0, -0.6692161319761768, 2.294129417823661),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 14, 5, 'O6', 0.0, 0.0, -0.6682501044542629, 2.294161065386326),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 14, 6, 'O7', 0.0, 0.0, -0.6672795862351104, 2.2934984898204482),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 14, 7, 'O8', 0.0, 0.0, -0.6706269165388118, 2.29362655959858),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 14, 8, 'O9', 0.0, 0.0, -0.6669198952165579, 2.2903236221445016),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 14, 9, 'O10', 0.0, 0.0, -0.6709030317809763, 2.292041126779126),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 14, 10, 'O11', 0.0, 0.0, -0.6703653074437252, 2.2920850899299063),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 14, 11, 'O12', 0.0, 0.0, -0.6686115310525428, 2.2939523961880344),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 14, 12, 'O13', 0.0, 0.0, -0.6685175851899895, 2.2935662140812876),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 14, 13, 'O14', 0.0, 0.0, -0.6666830153057348, 2.2899281445738686),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 14, 14, 'O15', 0.0, 0.0, -0.66872018359388, 2.2918934436999976),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 14, 15, 'O16', 0.0, 0.0, -0.6680086607656232, 2.290758118110905),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 14, 16, 'O17', 0.0, 0.0, -0.668990048909374, 2.29295282676507),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 14, 17, 'O18', 0.0, 0.0, -0.666855346254088, 2.2933959279595895),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 14, 18, 'O19', 0.0, 0.0, -0.6658120988481628, 2.2923239251476173),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 14, 19, 'O20', 0.0, 0.0, -0.6673292368619437, 2.292489119380376),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 14, 20, 'O21', 0.0, 0.0, -0.6680299226096128, 2.2910221274700615),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 14, 21, 'O22', 0.0, 0.0, -0.6657853651393771, 2.291965855781885),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 14, 22, 'O23', 0.0, 0.0, -0.6649508714133989, 2.293690912887588),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 14, 23, 'O24', 0.0, 0.0, -0.6648148272760998, 2.2908957535949783),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 15, 0, 'P1', 0.0, 0.0, -0.6624895564844232, 2.288353755092823),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 15, 1, 'P2', 0.0, 0.0, -0.6528138216113162, 2.288094584397817),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 15, 2, 'P3', 0.0, 0.0, -0.6645235889056118, 2.2944712772575513),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 15, 3, 'P4', 0.0, 0.0, -0.6633519885178968, 2.29222250618681),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 15, 4, 'P5', 0.0, 0.0, -0.6663556114460117, 2.294664758454353),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 15, 5, 'P6', 0.0, 0.0, -0.6620611522775182, 2.2915751064421266),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 15, 6, 'P7', 0.0, 0.0, -0.6674880950296598, 2.2922521552631885),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 15, 7, 'P8', 0.0, 0.0, -0.6649302375769935, 2.290901411492807),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 15, 8, 'P9', 0.0, 0.0, -0.6663485194258082, 2.290912797265473),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 15, 9, 'P10', 0.0, 0.0, -0.6696071654088953, 2.2921747245362214),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 15, 10, 'P11', 0.0, 0.0, -0.6662236180004425, 2.290031215160076),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 15, 11, 'P12', 0.0, 0.0, -0.6679507011856861, 2.288793560669057),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 15, 12, 'P13', 0.0, 0.0, -0.6694305730574973, 2.2902821770606834),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 15, 13, 'P14', 0.0, 0.0, -0.6648331030130133, 2.2885690684526168),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 15, 14, 'P15', 0.0, 0.0, -0.6648138788533554, 2.2890029864542925),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 15, 15, 'P16', 0.0, 0.0, -0.6654262080449294, 2.2893550912583627),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 15, 16, 'P17', 0.0, 0.0, -0.662038016866085, 2.2882319139318463),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 15, 17, 'P18', 0.0, 0.0, -0.6649802896916154, 2.2874042281603724),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 15, 18, 'P19', 0.0, 0.0, -0.6638321829546193, 2.2906421861036717),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 15, 19, 'P20', 0.0, 0.0, -0.666965399730481, 2.2916848783336774),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 15, 20, 'P21', 0.0, 0.0, -0.6645641549165712, 2.289465136851852),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 15, 21, 'P22', 0.0, 0.0, -0.658049546058876, 2.287305097294262),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 15, 22, 'P23', 0.0, 0.0, -0.6605989520424329, 2.28835405241797),
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 15, 23, 'P24', 0.0, 0.0, -0.6653835514489079, 2.286540253857699)
PRINT(LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into PlateSignature for PlateType: "'+@ClassifiedName+'".')



INSERT INTO PlateType (PlateTypeName, InstrumentName, Manufacturer, LotNumber, PartNumber, BarcodeLocation, Rows, Columns, BootstrapWell, BootstrapZ, SurveyToFRatio, A1OffsetX, A1OffsetY, SkirtHeight, CenterWell, CenterX, CenterY, PlateHeight, WellWidth, WellLength, XWellSpacing, YWellSpacing, WellCapacity, SoundVelocity, BottomInset, PlateUse, PlateFormat, Fluid, BottomThickness, ThicknessTolerance, IsDeleted, ParentPlate)
VALUES 
(@ClassifiedName, 'MEDMAN', 'Labcyte', '1', 'LP-0200', 'None', 16, 24, 'D10', 17000.0, 0.86, 12130.0, 8990.0, 2410.0, 'H12', 105119.703, 39553.414, 10400.0, 1540.0, 1540.0, 4500.0, 4506.0, 20.0, 2500.0, 4.5, 'HID', '384LDV', 'Glycerol', 0.0, 0.0, 0, NULL)
PRINT(LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into PlateType for PlateType: "'+@ClassifiedName+'".')



INSERT INTO ReferenceWaveforms (InstrumentName, PlateTypeName, TransducerName, Waveform, Directory, FileName, Configuration)
VALUES 
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 'LongWaveform', 'waveforms\7p5MHz_Kernel', '7p5MHz_GeneralKernel_081712.csv', '193,
nPoints,193
xIncr,2.00E-09
xZero,0.00E+00
xUnits,s
yMult,0.00E+00
yZero,0.00E+00
yOffset,0.00E+00
yUnits,v
,
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
('MEDMAN', @ClassifiedName, 'Transducer10MHz', 25.0, 25.0, 100000.0, 25.0, 500.0, 3.75, 15.0, 0.2, 'ToneX_25nl_3seg_1pt1chirp.cfg', '# This file was modified automatically on Fri Jan 21 13:53:55 2011
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
('MEDMAN', @ClassifiedName, 'V1.2', 'H12', 1, 500, 25, 0, 2250.0, -2250.0)
PRINT(LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into WellAdjustment for PlateType: "'+@ClassifiedName+'".')



INSERT INTO PlateRegistration (RegistrationDate, InstrumentName, TransducerName, PlateTypeName, CenterWell, CenterX, CenterY, XWellSpacing, YWellSpacing)
VALUES 
('2017-01-17 10:51:35', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105680.489, 39775.0016, 4500.0, 4506.0),
('2017-02-06 15:36:31', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105524.0, 39395.0, 4500.0, 4506.0),
('2018-05-25 14:55:15', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105146.07, 39571.0156, 4500.0, 4506.0),
('2018-05-25 14:58:54', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105137.281, 39571.0156, 4500.0, 4506.0),
('2018-05-25 15:01:25', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105146.07, 39562.2148, 4500.0, 4506.0),
('2018-05-25 15:03:05', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105119.703, 39553.414, 4500.0, 4506.0),
('2018-05-25 15:05:23', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105119.703, 39553.414, 4500.0, 4506.0),
('2018-05-25 15:05:39', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105137.281, 39553.414, 4500.0, 4506.0),
('2018-05-25 15:07:23', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105154.859, 39571.0156, 4500.0, 4506.0),
('2018-05-25 15:23:56', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105119.703, 39535.8124, 4500.0, 4506.0),
('2018-05-25 15:34:28', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105128.492, 39535.8124, 4500.0, 4506.0),
('2018-05-25 15:44:32', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105119.703, 39535.8124, 4500.0, 4506.0),
('2018-05-25 15:50:00', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105154.859, 39553.414, 4500.0, 4506.0),
('2018-05-25 15:56:53', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105119.703, 39535.8124, 4500.0, 4506.0),
('2018-05-25 16:03:13', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105154.859, 39562.2148, 4500.0, 4506.0),
('2018-05-25 16:07:57', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105146.07, 39562.2148, 4500.0, 4506.0),
('2018-05-25 16:12:35', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105128.492, 39544.6132, 4500.0, 4506.0),
('2018-05-25 16:16:55', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105119.703, 39544.6132, 4500.0, 4506.0),
('2018-05-25 16:21:12', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105119.703, 39544.6132, 4500.0, 4506.0),
('2018-05-25 16:32:54', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105119.703, 39544.6132, 4500.0, 4506.0),
('2018-05-25 16:37:27', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105154.859, 39571.0156, 4500.0, 4506.0),
('2018-05-25 16:42:45', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105154.859, 39571.0156, 4500.0, 4506.0),
('2018-05-25 16:47:09', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105119.703, 39544.6132, 4500.0, 4506.0),
('2018-05-25 16:51:34', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105119.703, 39544.6132, 4500.0, 4506.0),
('2018-05-25 16:55:21', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105119.703, 39544.6132, 4500.0, 4506.0),
('2018-06-15 10:57:47', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105172.437, 39597.4179, 4500.0, 4506.0),
('2018-06-15 11:08:51', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105163.648, 39615.0195, 4500.0, 4506.0),
('2018-06-15 11:12:25', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105128.492, 39606.2187, 4500.0, 4506.0),
('2018-06-15 11:16:44', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105128.492, 39571.0156, 4500.0, 4506.0),
('2018-06-15 11:20:38', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105119.703, 39571.0156, 4500.0, 4506.0),
('2018-06-15 11:23:48', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105154.859, 39615.0195, 4500.0, 4506.0),
('2018-06-21 15:54:34', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105146.07, 39535.8124, 4500.0, 4506.0),
('2018-06-21 15:59:56', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105146.07, 39535.8124, 4500.0, 4506.0),
('2018-06-21 16:15:26', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105119.703, 39562.2148, 4500.0, 4506.0),
('2018-06-21 16:19:07', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105146.07, 39544.6132, 4500.0, 4506.0),
('2018-06-21 18:49:24', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105137.281, 39615.0195, 4500.0, 4506.0),
('2018-06-21 18:54:42', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105137.281, 39571.0156, 4500.0, 4506.0),
('2018-06-21 19:00:04', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105137.281, 39615.0195, 4500.0, 4506.0),
('2018-06-21 19:05:23', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105137.281, 39571.0156, 4500.0, 4506.0),
('2018-06-21 19:10:52', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105137.281, 39571.0156, 4500.0, 4506.0),
('2018-06-21 19:16:10', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105137.281, 39615.0195, 4500.0, 4506.0),
('2018-06-21 19:21:32', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105137.281, 39615.0195, 4500.0, 4506.0),
('2018-06-21 19:26:44', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105137.281, 39615.0195, 4500.0, 4506.0),
('2018-06-21 19:31:52', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105137.281, 39571.0156, 4500.0, 4506.0),
('2018-06-21 19:36:47', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105137.281, 39571.0156, 4500.0, 4506.0),
('2018-06-21 19:41:41', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105137.281, 39615.0195, 4500.0, 4506.0),
('2018-06-21 19:45:39', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105137.281, 39615.0195, 4500.0, 4506.0),
('2018-06-21 19:50:57', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105137.281, 39615.0195, 4500.0, 4506.0),
('2018-06-21 19:56:27', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105128.492, 39615.0195, 4500.0, 4506.0),
('2018-06-21 20:01:45', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105137.281, 39615.0195, 4500.0, 4506.0),
('2018-06-21 20:07:06', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105137.281, 39615.0195, 4500.0, 4506.0),
('2018-06-21 20:12:24', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105137.281, 39615.0195, 4500.0, 4506.0),
('2018-06-21 20:17:41', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105128.492, 39615.0195, 4500.0, 4506.0),
('2018-06-21 20:22:47', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105128.492, 39571.0156, 4500.0, 4506.0),
('2018-06-21 20:27:49', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105137.281, 39615.0195, 4500.0, 4506.0),
('2018-06-21 20:32:38', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105137.281, 39606.2187, 4500.0, 4506.0),
('2018-06-21 21:29:11', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105128.492, 39527.0117, 4500.0, 4506.0),
('2018-06-21 21:32:07', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105137.281, 39535.8124, 4500.0, 4506.0),
('2018-06-21 21:35:01', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105128.492, 39535.8124, 4500.0, 4506.0),
('2018-06-21 21:37:58', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105128.492, 39535.8124, 4500.0, 4506.0),
('2018-06-21 21:40:53', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105137.281, 39535.8124, 4500.0, 4506.0),
('2018-06-21 21:43:51', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105128.492, 39535.8124, 4500.0, 4506.0),
('2018-06-21 21:46:45', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105128.492, 39535.8124, 4500.0, 4506.0),
('2018-06-21 21:49:44', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105146.07, 39535.8124, 4500.0, 4506.0),
('2018-06-21 21:52:39', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105137.281, 39553.414, 4500.0, 4506.0),
('2018-06-21 21:55:39', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105137.281, 39553.414, 4500.0, 4506.0),
('2018-06-22 13:36:06', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105137.281, 39535.8124, 4500.0, 4506.0),
('2018-06-22 13:40:52', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105128.492, 39535.8124, 4500.0, 4506.0),
('2018-06-22 13:45:43', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105119.703, 39535.8124, 4500.0, 4506.0),
('2018-06-22 13:49:45', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105119.703, 39535.8124, 4500.0, 4506.0),
('2018-06-22 13:53:50', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105119.703, 39562.2148, 4500.0, 4506.0),
('2018-06-22 13:58:27', 'MEDMAN', 'Transducer10MHz', @ClassifiedName, 'H12', 105137.281, 39535.8124, 4500.0, 4506.0)
PRINT(LTRIM(STR(@@ROWCOUNT)) + ' row(s) inserted into PlateRegistration for PlateType: "'+@ClassifiedName+'".')



IF (SELECT COUNT(*) FROM D2AMemory WHERE Waveform = 'PingBurst') != 0
	PRINT('D2AMemory waveform "PingBurst" already exists.  No need to insert.')
ELSE
	BEGIN
	
    DECLARE @FreeMemoryAddress INT
   
    SELECT @FreeMemoryAddress = MAX(MemoryAddress) + 1 FROM D2AMemory WHERE MemoryAddress < 80
    
    PRINT('Inserting new waveform at available memory address ' + CAST(@FreeMemoryAddress AS VARCHAR(4)) + '.')

 	

INSERT INTO D2AMemory (Waveform, MemoryAddress, Type, Length, Path, Description, Configuration)
VALUES 
('PingBurst', @FreeMemoryAddress, 'I', 16, '7pt5MHz_optping.cfg', 'simple ping', ':CUSTOM_TONEBURST_PARAMETERS

# Use ''Pragmatic'' for Pragmatic GPIB instrument
# Use ''???'' for Char Scientific PCI
D2A		STRING	"Tabor"

# 20 for 20 MHz Guassian filter, 50 for 50 MHz elliptic filter
FilterFreq	FLOAT	50.0

:CUSTOM_TONEBURST_DEFINITION

# If this is not "Null", then use the file referenced here to
# get waveform samples.  Note that this is not a fully-qualified
# path, and that we expect the file to be located in the
# COMMON conf directory.
#
# Format of this file is quite simple:
#
# N<CR>
# x1<CR>
# x2<CR>
#  .
#  .
#  .
# xN<CR>

# File		STRING	"7pt5MHz_optping5.csv"	 COMMENT CREATED BY EchoConfig
File		STRING	"Null"

# If File ~= "Null", then use this vector for the waveform samples

Samples		FLTVEC	0 -0.0051511 0.0023677 0.017729 0.0074864 -0.042689 -0.11175 -0.16642 -0.17827 -0.13232 -0.037364 0.072495 0.15653 0.18334 0.14902 0.077688 0.014064 0.00071716 0.052564 0.15001 0.23758 0.25011 0.1408 -0.0899 -0.38451 -0.64575 -0.76635 -0.6746 -0.36522 0.089708 0.56079 0.90429 1.0115 0.84808 0.46635 -0.01366 -0.44703 -0.71336 -0.75692 -0.59838 -0.32086 -0.032363 0.17528 0.25637 0.22324 0.12767 0.036698 -0.002022 0.024491 0.094048 0.16075 0.18317 0.14213 0.050389 -0.060253 -0.14747 -0.18011 -0.15717 -0.097585 -0.029691 0.01437 0.015404 -0.0070559 -0.015551 -0.0044209 0.0026431 -0.00026692 -0.0010613 0.00072076 2.01E-19 -0.00044284 0.00042732 4.62E-05 -0.00013795 0.00015105 3.76E-05 -9.08E-05 2.78E-05 8.77E-06 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0')
PRINT(LTRIM(STR(@@ROWCOUNT)) + '  row(s) inserted into D2AMemory for waveform: "PingBurst".')


	END

