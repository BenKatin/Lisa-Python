import os
import matplotlib.pyplot as plt
import numpy as numpy
import pandas as pandas
import xlrd
import csv
import Xcontam as Xcon

"""
Takes in the local directory of a csv and an Excel file, and returns a dataframe containing the power range, mean value and standard deviation of each collumn of the excel file

"""
class EjectSweep:
    """
    Instantiate class with exceldate = "local_directory.xls"

    """
    def __init__(self, exceldata, picklist = None):
        if(picklist!= None):
            self.picklist = Xcon.ReadPickList(picklist)

        self.sheets = Xcon.GetReaderFiles(exceldata)

    """
    returns the Sheets from the excel file
    """
    def getSheets(self):
        return self.sheets.GetSheetNames()

    """
    Chooses which sheet in the excel file to calculate data on
    """
    def chooseSheet(self,sheetname):
        self.output = self.sheets.GetSheet(sheetname)

    """
    returns a DataFrame with 3 collumns and 24 rows using the current chosen sheet
    """
    def getProcessedData(self):
        col_names = ['power', 'mean', 'std']

        means = []
        std = []
        powers = list(x * 4 / 100 for x in range(-11, 13))


        for num in range(1, 25):
            means.append(self.output[num].mean())
            std.append(self.output[num].std())

        graphData = pandas.DataFrame(
            {'power': powers,
             'mean': means,
             'std': std
             })


        return graphData

    def getData(self):
        return self.output

    def boxGraph(self):
        self.output.plot.box()
        plt.show()

if __name__ == "__main__":

    EJ = EjectSweep("EjectSweep/20180830_162258_RawVolumeOutput.xlsx")

    print(EJ.getSheets())

    EJ.chooseSheet('01_1445_BP_50_ES.xls')

    print(EJ.getProcessedData())

