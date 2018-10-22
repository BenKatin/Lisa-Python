import Ejectsweep as ejsw
import matplotlib.pyplot as plt

EJ = ejsw.EjectSweep("EjectSweep/20180830_162258_RawVolumeOutput.xlsx") #instantiates am instance of the EjectSweep class, passes in local directory of excel file

print(EJ.getSheets()) #returns sheet names

EJ.chooseSheet('01_1445_BP_50_ES.xls') #chooses which sheet of excel file to use

Data = EJ.getData() # returns full unprocessed dataframe containing all data in the excel sheet

processedData = EJ.getProcessedData() #returns dataframe containing 3 collumns, power mean and standard deviation

#EJ.boxGraph() #function to create graph from data

Data.plot.box() #code to create graph from unprocessed data
plt.show()

