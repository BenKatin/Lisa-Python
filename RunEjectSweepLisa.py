import Ejectsweep as ejsw
import matplotlib.pyplot as plt
import os
#from pyCyte_EXP.ToolBox import SimpleTools

thisdir = '\\\\seg\\data\\96SP_Feasibility\\Experiments\\20180831_SP_Recal_1445\\07_CF6.85_RR200_VolTune\\ReaderFiles2'
os.chdir(thisdir)

fl = os.listdir()
for f in fl:
    if 'Raw' in f:
        dFile = f
#rfiles =  SimpleTools.getFileList('*RawVolumeOutput.xlsx')
EJ = ejsw.EjectSweep(dFile) #instantiates am instance of the EjectSweep class, passes in local directory of excel file
#EJ = ejsw.EjectSweep("EjectSweep/20180830_162258_RawVolumeOutput.xlsx") #instantiates am instance of the EjectSweep class, passes in local directory of excel file

#print(EJ.getSheets()) #returns sheet names

#EJ.chooseSheet('01_1445_BP_50_ES.xls') #chooses which sheet of excel file to use

#EJ.multiPlot([0,1,2,3,4,5,6,7,8,9],2,5)  
#EJ.multiPlot([4,5,6,7,8,9],2,3,rotation = 90,textsize = 5,title="E1445 SP Recal 08-31-18")  

EJ.multiPlot([4,5,6,7,8,9],2,3,textsize = 5,title="E1445 SP Recal 08-31-18")  


#Data = EJ.getData() # returns full unprocessed dataframe containing all data in the excel sheet

#processedData = EJ.getProcessedData() #returns dataframe containing 3 collumns, power mean and standard deviation

#EJ.boxGraph() #function to create graph from data

#Data.plot.box() #code to create graph from unprocessed data
#plt.show()

