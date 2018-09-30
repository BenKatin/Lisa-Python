import os
import time
import json
import winreg
import pyodbc
import numpy as np
import matplotlib.pyplot as plt

if os.path.basename(__file__):
    from pyCyte.NNCalibrate.NNCharacterizeTransducer import analyzeInstrument, plateIDs
else:
    from  .NNCharacterizeTransducer import analyzeInstrument, plateIDs

from   tkinter import Tk, filedialog

# Seems ot be best for functions to use their own connections... particularly
# around the dicy asyncronous backup/restore operations.
def getCursor(db=None):
    cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+dbServer+';Trusted_Connection=yes;')
    cnxn.autocommit = True  
    c = cnxn.cursor()
  
    if db:
        c.execute("USE " + db)
        
    return c

# Both backup and restore ops are asyncronous.
# This polls and only returns when all backup/retore ops are clear.
def waitForAsyncDBTransactions(dbName, pollSeconds = 0.2):
    cursor = getCursor()
    
    q = "SELECT * FROM sys.databases d, sys.dm_exec_requests r           \n\
          WHERE d.database_id = r.database_id                            \n\
            AND r.command LIKE 'Backup%' OR r.command LIKE 'Restore%'    \n\
            AND d.name = '"+dbName+"'"
   
    while True:
        if not cursor.execute(q).fetchall():
            print(' done.')
            return True
        
        time.sleep(pollSeconds)

def backupDatabase(dbName, backupPath):
    cursor = getCursor()
    print('Backing up database...', end='')   
    cursor.execute("BACKUP DATABASE "+ dbName + " TO DISK = '"+ backupPath +"'")
    waitForAsyncDBTransactions(dbName)
    
def restoreDatabase(dbName, backupPath):
    cursor = getCursor()
    
    # first make a list of its contents
    dbComponents = [(a.LogicalName,a.Type) for a in cursor.execute("RESTORE FILELISTONLY FROM DISK='" + backupPath + "'").fetchall()]
    moveStrings = ["MOVE '" + comp[0] + "' TO '" + settings['serverDataPath']+ "\\" + dbName + "_" + comp[0] + (".mdf" if comp[1] == 'D' else ".ldf") + "'" for comp in dbComponents]

    # wipe out destination database if already present.    
    cursor.execute("IF OBJECT_ID('" + dbName + "', 'U') IS NOT NULL DROP TABLE " + dbName)
    
    # then restore using content list
    print('Restoring as copy to ' + dbName + '...', end='')
    cursor.execute("RESTORE DATABASE " + dbName + " FROM DISK='" + backupPath + "' WITH " + ",".join(moveStrings))
    waitForAsyncDBTransactions(dbName)
    
    # delete the temp backup file
    cursor.execute("xp_cmdshell 'del \"" + backupPath + "\"'")
    
## Here's where we do inference from our simple models witout tensorflow.    
def NNPredict(desc, v):
    ## desc is the object contained in the model's info.txt
    if desc['activation_type'] != 'Tanh':
        raise Exception("Activation type " + desc['activation_type'] + " is unknown.  Can't infer from this model.")
        
    std       = np.asarray(desc['normalization_std'])
    mean      = np.asarray(desc['normalization_mean'])
    targ_std  = np.asarray(desc['normalization_targ_std'])
    targ_mean = np.asarray(desc['normalization_targ_mean'])
    
    weights = list(map(lambda x: np.asarray(x), desc['layerWeights']))
    biases  = list(map(lambda x: np.asarray(x), desc['layerBiases']))

    # This may be a problem for old models that use slopes and swichpoints (i.e. Albatross).  Might need to specify 
    result = np.divide(np.asarray(v) - mean, std ) # start with normalized input vector

    for i, _ in enumerate(weights[:-1]):       
        result = np.tanh(np.dot(result, weights[i]) + biases[i])
    
    # Output layer has linear activation
    result = np.dot(result, weights[-1]) + biases[-1]
    
    return ((result * targ_std) + targ_mean).tolist()    

def gatherCF1LocationsForPredictions( tx, cals ):
    return [[val['plateTypeName'],r[0],pId] for pId, val in tx['plateSpecific'].items() for r in val['rawToneX']['CF1'] if val['plateTypeName'] in cals ]

def gatherT2TLocationsForPredictions( tx, cals ):
    return [[val['plateTypeName'],r[0],r[1],pId] for pId, val in tx['plateSpecific'].items() for r in val['rawT2T'] if val['plateTypeName'] in cals ]

def injectCFPredictionsIntoDatabase(db, plateImpVec, CFVec):
    cursor = getCursor(db)

    for idx, val in enumerate(plateImpVec):
        q = "UPDATE LUT SET Y = " + str(np.round(CFVec[idx][0],3)) +       " WHERE PlateTypeName = '" + val[0] + "' AND LUTName = 'ToneX_CF_MHz' AND DESCRIPTION = 1 AND X = " + str(val[1])
        cursor.execute(q)
        
        q = "UPDATE LUT SET Y = " + str(np.round(0.9 * CFVec[idx][0],3)) + " WHERE PlateTypeName = '" + val[0] + "' AND LUTName = 'ToneX_CF_MHz' AND DESCRIPTION = 3 AND X = " + str(val[1])
        cursor.execute(q)

def injectT2TPredictionsIntoDatabase(db, plateImpVec, T2TVec):
    cursor = getCursor(db)
    for idx, val in enumerate(plateImpVec):
        q = "UPDATE LUT2D SET Z = " + str(np.round(T2TVec[idx][0],3)) + " WHERE PlateTypeName = '" + val[0] + "' AND LUT2DName = 'Thresh2XferdB' AND X = " + str(val[1]) + ' AND Y = ' + str(val[2])
        cursor.execute(q)

def plotCFSFromDB(db, ax, plateImpList, colorString=None, offset=0, note=''):
    cursor = getCursor(db)
    
    plates = set([i[0] for i in plateImpList])
    
    for plate in plates:
        out = np.asarray(cursor.execute("SELECT X + " + str(offset) + ", Y FROM LUT WHERE plateTypeName = '" + plate + "' AND LUTName = 'ToneX_CF_MHz' AND Description = 1").fetchall())
        if colorString != None: 
            ax[plateIDs[plate]].plot(out[:,0],out[:,1], '.', color=colorString, label=note) # label=db + ' ' + note)              
        else:
            ax[plateIDs[plate]].plot(out[:,0],out[:,1], '.', label=note) # label=db + ' ' + note)
     
def plotCFSFromPrediction(ax, plateImpList, CFVec, colorString=None, offset=0, note=''):  

    plates = set([i[0] for i in plateImpList])

    for plate in plates:       
        x = [ i[1] + offset  for      i in           plateImpList  if i[0] == plate ]
        y = [ CFVec[idx]     for idx, i in enumerate(plateImpList) if i[0] == plate ]
        
        if colorString != None: 
            ax[plateIDs[plate]].plot(x, y, '.', color=colorString, label=note)   
        else:
            ax[plateIDs[plate]].plot(x, y, '.', label=note)          
        
def plotT2TFromDB(db, ax, plateImpList, symbolString='.', offset=0, note='', impToLegend=True):
    colors=plt.cm.brg
    
    cursor = getCursor(db)
    
    plates = set([i[0] for i in plateImpList])
    
    for plate in plates:
        out = np.asarray(cursor.execute("SELECT X + " + str(offset) + ", Y, Z FROM LUT2D WHERE plateTypeName = '" + plate + "' AND LUT2DName = 'Thresh2XferdB'").fetchall())
        
        thicks = sorted(np.unique(out[:,1]))
        
        for ti, thick in enumerate(thicks):

            plotPoints = out[out[:,1] == thick]

            # Give legend a generic square for thickness legend
            ax[plateIDs[plate]].plot([],[], 'sk',  c=colors(ti/len(thicks)), ms=6, label=thick if impToLegend else None)     

            ax[plateIDs[plate]].plot(plotPoints[:,0]+ti*0.00125, plotPoints[:,2], symbolString,  c=colors(ti/len(thicks)), ms=10)              

        ax[plateIDs[plate]].legend(title='Thick. [mm]', fontsize='small')
  
def plotT2TFromPrediction(ax, plateImpList, T2TVec, symbolString='.', size=10, offset=0, note='', impToLegend=True):  
    colors=plt.cm.brg
    plates = set([i[0] for i in plateImpList])
    
    for plate in plates:
        thicks = set(list([ i[2]  for  i in plateImpList  if i[0] == plate ]))
        for ti, thick in enumerate(sorted(thicks)):        
            imps = [ i[1] + offset + ti*0.00125  for      i in plateImpList            if i[0] == plate and i[2] == thick ]
            t2ts = [ T2TVec[idx]    for idx, i in enumerate(plateImpList) if i[0] == plate and i[2] == thick ]

            # Give legend a generic square for thickness legend
            ax[plateIDs[plate]].plot([], [], 'sk', c=colors(ti/len(thicks)), ms=6, label=thick if impToLegend else None)

            ax[plateIDs[plate]].plot(imps, t2ts, symbolString, c=colors(ti/len(thicks)), ms=size)

def plotTrainingSets(trainingSets, compareWith = False, saveDir = None, savePlotNameMod = '', showPlot = True):
    print('Plotting training sets.', end='')
    if compareWith is not False:
        print(' (Computed characteristics of this transducer in red.)')    
    else:
        print('')

    datadim = len(trainingSets[0])
  
    fig, ax = plt.subplots(datadim)
    
    if type(ax) != type(np.asarray([])):
        ax = [ax]
    
    for dim1 in range(datadim):
        plot=datadim-dim1-1

        ax[plot].set_yticks([])
        ax[plot].set_ylabel(plot)
        if compareWith is not False:
            ax[plot].plot(compareWith[plot], 0,'ro', markerfacecolor='none', markeredgewidth=1.75)
        ax[plot].plot(trainingSets[:,plot], [0 for _ in trainingSets],'k+')
    
    plt.tight_layout()
    fig.set_size_inches(6,0.9 * datadim)
    if saveDir:
        plt.savefig(os.path.join(saveDir, 'trainingSets'+savePlotNameMod+'.png'), bbox_inches='tight')
    
    plt.show() if showPlot else plt.close()


def plotTrainingSetCorrelations(trainingSets, compareWith=False, saveDir=None, savePlotNameMod = '', showPlot = True):
    print('Plotting correlations in training data.')
    if compareWith is not False:
        print('Computed characteristics of this transducer in red.')
        
   # ts = np.asarray(trainingSets)[:,4:-1]    

    datadim = len(trainingSets[0])

    if datadim == 1:
        print('Only one data dimension... so no correlation plot for you.')
        return

    fig, ax = plt.subplots(datadim-1, datadim-1, sharex='col', sharey='row')

    for dim2 in range(datadim-1):
        for dim1 in range(datadim):
            if dim1 == datadim-1:
                ax[dim1-1, dim2].set_xlabel(dim2)
    
            if dim2 == 0:
                ax[dim1-1, dim2].set_ylabel(dim1)
            
            if dim2<dim1:
                ax[dim1-1, dim2].plot(trainingSets[:,dim2], trainingSets[:,dim1],'k+')
                if compareWith is not False:
                    ax[dim1-1, dim2].plot(compareWith[dim2], compareWith[dim1], 'ro', markerfacecolor='none', markeredgewidth=1.75)
                ax[dim1-1, dim2].axis('on')
            else:
                ax[dim1-1, dim2].axis('off')

    fig.set_size_inches(14,14)
    
    if saveDir:
        plt.savefig(os.path.join(saveDir, 'trainingSetsCorrelations'+savePlotNameMod+'.png'), bbox_inches='tight')
    
    plt.show() if showPlot else plt.close()

def NNAnalyze(**kwargs):
    """
    NNanalyze uses a neural network model to compute a calibration for an instrument
    and insert into the instrument's database. By default the function prompts
    for a focal sweep file and uses the 'SOFTWARE\Labcyte\Echo\Server\DATA_ACCESS\Database' 
    registry key as the source and destination database.  The database is changed
    in place; existing entries are clobbered by the modeled results.
    
    All arguments (below with defaults) are by keyword:
        
             'modelRoot' : os.path.join(os.path.dirname(__file__),'models'),
                 'model' : 'multi_1_455_Tanh',   # Which model to use?
        'showGoldInComp' : False,                # Include a gold database in comparison comp
         'goldDBForComp' : 'E1419_GoldDB_TS_4_3',# Gold database for comparison plot if shoGoldInComp is true
        'serverDataPath' : r'E:\LighthouseData', # If workOnDuplicateDB, where does database store db file
     'workOnDuplicateDB' : False,                # If true, source database is unmodified.  A duplicate is made
                                                 # and a .bak file is produced.
            'outputPath' : r'E:\TempEchoDBs' ,   # if workOnDuplicateDB, where should the output .bak be placed
                'DBName' : False,                # Database name to use.  If false, regkey is used.      
        'focalSweepPath' : False,                # Path to focal sweep.  If false, file browser popup appears.
              'dbServer' : 'localhost',          # Database server
        'defaultRegPath' : 'SOFTWARE\Labcyte\Echo\Server\DATA_ACCESS',# Regkey path for database name
        'defaultRegKey'  : 'Database'                                 # Regkey for database name
         'savePlotPath'  : None                  # Save .png plots this path.
    """

    global settings
    global dbServer
    global tx
    
    settings = {     'outputPath' : r'E:\TempEchoDBs' ,
                 'showGoldInComp' : False,
                  'goldDBForComp' : 'E1419_GoldDB_TS_4_3',
                 'serverDataPath' : r'E:\LighthouseData',
                      'modelRoot' : os.path.join(os.path.dirname(__file__),'models'),
                          'model' : 'albatross',
               'comparisonModels' : [],
              'workOnDuplicateDB' : False,
                         'DBName' : False,
                 'focalSweepPath' : False,
                'applyPrediction' : False,
                      'makePlots' : True,
          'showGraphicsInConsole' : False,
      'makeCharacterizationPlots' : False,
                      'predictCF' : True,
                     'predictT2T' : True,
                           'cals' : ['384PPL_DMSO2',
                                     '384PPG_DMSO2',
                                     '384LDVS_DMSO',
                                     '1536LDVS_DMSO'],
                       'dbServer' : 'localhost',
                 'defaultRegPath' : 'SOFTWARE\Labcyte\Echo\Server\DATA_ACCESS',
                 'defaultRegKey'  : 'Database',
                   'savePlotPath' : None,
                'savePlotNameMod' : ''}

    # Replate default settings.
    for key, value in kwargs.items():
        if key not in settings:
            raise Exception("I don't know argument: " + key + ".  Sorry quitting.")
        settings[key] = value

    if not settings['DBName']:
        try:
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, settings['defaultRegPath'])
            settings['DBName'] = winreg.QueryValueEx(k, settings['defaultRegKey'])[0]
            print('Selected database ' + settings['DBName'] + ' based on registry settings.')
        except:
            raise Exception('No target database specified and no entry found in ' + settings['defaultRegPath'] + '\\' + settings['defaultRegKey'] + '.' )
    
    if settings['savePlotPath'] and not os.path.exists(settings['savePlotPath']):
        os.makedirs(settings['savePlotPath'])
    
    dbServer = settings['dbServer']
        
    DBName = settings['DBName']
    
    focalSweepPath = settings['focalSweepPath']    
    
    if not settings['focalSweepPath']:
        print('Please select a focal sweep file using file browser (which is probably behind your Spyder window).')
        root = Tk()
        root.withdraw()
        focalSweepPath = filedialog.askopenfilename()
        print(focalSweepPath + ' selected.')
    
    tx = analyzeInstrument( dbServer, DBName, focalSweepPath, AmpDetails = [54.00671407,50.65038935,1.955707633], makePlots = settings['makeCharacterizationPlots'], showPlots = settings['showGraphicsInConsole'], plotSaveDir=settings['savePlotPath'] )
    
    ####
    ####
    #  Begin 
    #   CF
    ####
    ####
    
    if settings['predictCF']:
    
        plateImpList = gatherCF1LocationsForPredictions( tx, settings['cals'] )

        #########################
        ## Plot some things before (potentially) clobbering original
        #plt.close('all')
        fig, ax = plt.subplots(1,len(settings['cals']), sharey=True)
        
        ax[0].set_ylabel('CF1 [MHz]')
        ax[0].set_ylim(12,13)
    
        for i in range(len(settings['cals'])):
            ax[i].set_xlabel('Impedance [MRayl]')
            
        for plateName in set([i[0] for i in plateImpList]):
            ax[plateIDs[plateName]].set_title(plateName)
         
        if settings['showGoldInComp']:
            plotCFSFromDB(settings['goldDBForComp'], ax,  plateImpList, colorString='black')            # GoldDB
    
        plotCFSFromDB(DBName, ax,  plateImpList, colorString='black', offset=0, note='DB contents')     # initial state
        ###########################

        ###########################
        ## Lets do any comparison predictions

        idx = 0  # In case there's no comparison models.  

        for idx, comparisonModel in enumerate(settings['comparisonModels'],1):
            modelInfoPath = os.path.join(settings['modelRoot'], comparisonModel, 'info.CF.txt')
            
            if not os.path.exists(modelInfoPath):
                modelInfoPath = os.path.join(settings['modelRoot'], comparisonModel, 'info.txt')
    
            with open(modelInfoPath) as data_file:    
                modelInfo = json.load(data_file)
                
            buildFeatureVectorDynamic = eval(modelInfo['buildFeatureVector'].strip())    
            CFPredictions = [ NNPredict(modelInfo, buildFeatureVectorDynamic(tx, i[2], i[1], None)) for i in plateImpList ]
            plotCFSFromPrediction(ax, plateImpList, CFPredictions, colorString='red', offset=0.005*idx, note=comparisonModel)
                
        ###########################
        ## Lets do the primary prediction
        modelInfoPath = os.path.join(settings['modelRoot'], settings['model'], 'info.CF.txt')
            
        if not os.path.exists(modelInfoPath):
             modelInfoPath = os.path.join(settings['modelRoot'], settings['model'], 'info.txt')
    
        with open(modelInfoPath) as data_file:    
            modelInfo = json.load(data_file)
            
        buildFeatureVectorDynamic = eval(modelInfo['buildFeatureVector'].strip())

        print('\n')
        print(settings['model'] + ' [CF] uses the followign feature selector:\n')
        print('\t' + modelInfo['buildFeatureVector'].strip())
        print('\n')
        
        CFPredictions = [ NNPredict(modelInfo, buildFeatureVectorDynamic(tx, i[2], i[1], None)) for i in plateImpList ]
        
        idx+=1
        
        if settings['workOnDuplicateDB']:
    
            BackupName       = DBName + '.bak'
    
            InstrumentTempDB = DBName + '_NNMod' 
        
            OutputDBName     = DBName + '_NNMod.bak' 
            
            backupDatabase( DBName,           os.path.join(settings['outputPath'],BackupName))
            
            restoreDatabase(InstrumentTempDB, os.path.join(settings['outputPath'],BackupName))
            
        else: # Write directly to given databse (clobber existing database content).
            
            InstrumentTempDB = DBName 
        
        if settings['applyPrediction']:
            injectCFPredictionsIntoDatabase(InstrumentTempDB, plateImpList, CFPredictions)   
            idx+=1
            plotCFSFromDB(InstrumentTempDB, ax, plateImpList, colorString = 'blue', offset=0.005*idx, note=settings['model']) # Show final vals as in DB if prediction applied
        else:
            plotCFSFromPrediction(ax, plateImpList, CFPredictions, colorString='blue', offset=0.005*idx, note=settings['model']) # If not applying results, plot from the prediction directly.
    
        if settings['workOnDuplicateDB']:
         
            backupDatabase( InstrumentTempDB, os.path.join(settings['outputPath'], OutputDBName))
       
        ###################################
        
        ax[0].legend()
    
        fig.set_size_inches(15,4)
    
        plt.tight_layout()
    
        plt.suptitle(DBName + '\n' + focalSweepPath, fontsize=10, y=1.12)
    
        if settings['savePlotPath']:
             plt.savefig(os.path.join(settings['savePlotPath'], 'calibraton'+ settings['savePlotNameMod'] +'.png'), bbox_inches='tight')
    
        plt.show() if settings['showGraphicsInConsole'] else plt.close()
        
        if settings['makePlots']:
            train = np.asarray(modelInfo['train_dataset'])
            
            reducedFeatures = np.asarray([ buildFeatureVectorDynamic(tx, i[2], i[1], None) for i in plateImpList])[:,4:-1].tolist()
            reducedFeatures = np.asarray(list(set([ tuple(r) for r in reducedFeatures])))[0]
            
            if len(reducedFeatures) == train.shape[1]:
                trimmedTrain = train #
            else:        
                trimmedTrain = train [:,4:-1]

            trimmedTrain =  np.asarray(list(set([ tuple(r) for r in trimmedTrain])))

            plotTrainingSets(           trimmedTrain, compareWith=reducedFeatures, saveDir=settings['savePlotPath'], savePlotNameMod=settings['savePlotNameMod'] + '_CF', showPlot=settings['showGraphicsInConsole'] )
            plotTrainingSetCorrelations(trimmedTrain, compareWith=reducedFeatures, saveDir=settings['savePlotPath'], savePlotNameMod=settings['savePlotNameMod'] + '_CF', showPlot=settings['showGraphicsInConsole'] )
            
    ####
    ####
    #  Begin 
    #   T2T
    ####
    ####

    if settings['predictT2T']:
        
        plateImpList = gatherT2TLocationsForPredictions( tx, settings['cals'] )  # calName, imp, thick, calIdx

        #########################
        ## Plot some things before (potentially) clobbering original

        fig, ax = plt.subplots(1,len(settings['cals'])+1, sharey=True)
        
        ax[4].plot([],[],'ok',label='Orig. DB Contents')
        ax[4].set_axis_off()
 
        ax[0].set_ylabel('T2T [dB]')
        ax[0].set_ylim(0,1)
    
        for i in range(len(settings['cals'])):
            ax[i].set_xlabel('Impedance [MRayl]')
            
        for plateName in set([i[0] for i in plateImpList]):
            ax[plateIDs[plateName]].set_title(plateName)
         
        if settings['showGoldInComp']:
            plotT2TFromDB(settings['goldDBForComp'], ax,  plateImpList, colorString='black')            # GoldDB

        idx = 0        
        plotT2TFromDB(DBName, ax,  plateImpList, offset=0, note='DB contents')     # initial state
        ###########################
        
        ###########################
        ## Lets do any comparison predictions
        for idx, comparisonModel in enumerate(settings['comparisonModels'],1):

            modelInfoPath = os.path.join(settings['modelRoot'], comparisonModel, 'info.T2T.txt')

            idx += 1

            if not os.path.exists(modelInfoPath):
                raise Exception('Comparison model: ' + settings['model'] + ' has no threshold-to-transfer model.  No prediction available.')
    
            with open(modelInfoPath) as data_file:    
                modelInfo = json.load(data_file)
                
            buildFeatureVectorDynamic = eval(modelInfo['buildFeatureVector'].strip())    
            T2TPredictions = [ NNPredict(modelInfo, buildFeatureVectorDynamic(tx, i[3], i[1], i[2])) for i in plateImpList ]
            ax[4].plot([],[],'^k', label='Comparison: '+comparisonModel)
            plotT2TFromPrediction(ax, plateImpList, T2TPredictions, symbolString='^', size=6, offset=0.005*idx, note=comparisonModel, impToLegend=False)
        
        ###########################
        ## Lets do the primary T2T prediction
        modelInfoPath = os.path.join(settings['modelRoot'], settings['model'], 'info.T2T.txt')
            
        if not os.path.exists(modelInfoPath):
            raise Exception(settings['model'] + ' has no threshold-to-transfer model.  No prediction available.')
 
        with open(modelInfoPath) as data_file:    
            modelInfo = json.load(data_file)
       
        buildFeatureVectorDynamic = eval(modelInfo['buildFeatureVector'].strip())
        
        print('\n')
        print(settings['model'] + ' [T2T] uses the followign feature selector:\n')
        print('\t' + modelInfo['buildFeatureVector'].strip())
        print('\n')

        T2TPredictions = [ NNPredict(modelInfo, buildFeatureVectorDynamic(tx, i[3], i[1], i[2])) for i in plateImpList ]
       
        InstrumentTempDB = DBName 
        
        idx+=1
        
        ax[4].plot([],[],'+k', ms=7, label=settings['model'])
        
        if settings['applyPrediction']:
            injectT2TPredictionsIntoDatabase(InstrumentTempDB, plateImpList, T2TPredictions)   
            plotT2TFromDB(InstrumentTempDB, ax,  plateImpList, offset=0.005*idx, symbolString='+', note=settings['model'], impToLegend=False)
        else:
            plotT2TFromPrediction(ax,  plateImpList, T2TPredictions, offset=0.005*idx, symbolString='+', note=settings['model'], impToLegend=False)    
                   
        ax[4].legend(loc=6, edgecolor='white')
 
        plt.tight_layout(pad = -4)
        fig.set_size_inches(15,3)

        plt.show() if settings['showGraphicsInConsole'] else plt.close()
        
        if settings['makePlots']:               
            train = np.asarray(modelInfo['train_dataset'])
            
            reducedFeatures = np.asarray([ buildFeatureVectorDynamic(tx, i[2], i[1], None) for i in plateImpList])[:,4:-1].tolist()
            reducedFeatures = np.asarray(list(set([ tuple(r) for r in reducedFeatures])))[0]
            
            trimmedTrain = train [:,4:-2]

            trimmedTrain =  np.asarray(list(set([ tuple(r) for r in trimmedTrain])))

            plotTrainingSets(           trimmedTrain, compareWith=reducedFeatures, saveDir=settings['savePlotPath'], savePlotNameMod=settings['savePlotNameMod'] + '_T2T', showPlot=settings['showGraphicsInConsole'] )
            plotTrainingSetCorrelations(trimmedTrain, compareWith=reducedFeatures, saveDir=settings['savePlotPath'], savePlotNameMod=settings['savePlotNameMod'] + '_T2T', showPlot=settings['showGraphicsInConsole'] )

#from pyCyte.NNCalibrate.NNSwapAdjust import NNAnalyze
#NNAnalyze( DBName = 'AA_1055202', workOnDuplicateDB = False, dbServer = 'localhost', predictCF=True, predictT2T=False, focalSweepPath=r'c:\Users\jrubin\Desktop\FocalSweep_2018-03-30_13-57-53.csv', model='Bluebird', comparisonModels=['Albatross'], applyPrediction=False, makeCharacterizationPlots = False)
#NNAnalyze( DBName = 'B_1055202', applyPrediction=False, workOnDuplicateDB = False, dbServer = 'localhost', predictCF=False, predictT2T=True, focalSweepPath = r'\\seg\transducer\Transducers\TX1055202_MC0668224\Calibration_E1419\2018-05-23_14-40-48\HealthCheck\384PPL_DefaultSrc\RF\TransducerFocalSweep\FocalSweep_2018-05-23_16-22-41.csv', model='Bluebird', comparisonModels=[], showGraphicsInConsole=True, makeCharacterizationPlots = True, savePlotPath=r'c:\Users\jrubin\Desktop\temp')