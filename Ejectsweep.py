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
    def chooseSheet(self,sheetIdentifier):

        self.output = self.sheets.GetSheet(sheetIdentifier)

    """
    returns a DataFrame with 3 collumns and 24 rows using the current chosen sheet
    """
    def getProcessedData(self, sheetIdentifier):
        self.chooseSheet(sheetIdentifier)
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

    def getData(self, sheetIdentifier):
        self.chooseSheet(sheetIdentifier)
        return self.output

    def boxPlot(self, sheetIdentifier):
        self.chooseSheet(sheetIdentifier)
        self.output.boxplot(return_type=dict)
        plt.show()

    def multiPlot(self,pagenumbers, rows, cols,name=None):
        self.count = 0
        fig, axes = plt.subplots(rows, cols,sharex=True,sharey=True)  # posible argument:
        sheetnames = self.getSheets()

        nums = list(x for x in range(1, 25))
        powers = list(x * 4 / 100 for x in range(-11, 13))
        count = 0
        for item in powers:
            if not(count % 10 == 0) :
                count = None

        for x in range(0,rows):
            for y in range(0,cols):
                data =self.sheets.GetSheet(sheetnames[pagenumbers[self.count]])
                data.boxplot(ax=axes[x,y],showfliers=False)
                axes[x, y].set_title(sheetnames[pagenumbers[self.count]])
                axes[x,y].tick_params(axis='both', which='both', labelsize=6)
                axes[x,y].set_xticklabels(powers)


                self.count += 1
        
        fig.subplots_adjust(hspace=.5)
        plt.xticks(nums, powers)


if __name__ == "__main__":


    EJ = EjectSweep("EjectSweep/20180830_162258_RawVolumeOutput.xlsx")  # select an excel file as the file to be
                                                                        # used by the EjectSweepClass

    pgZero = EJ.getData(0)  # pass in either the sheet name or the sheet index starting
                            # from 0 and get the raw dataframe containing the data


    sheets = EJ.getSheets() # returns a list containing all the sheet names

    EJ.multiPlot([0,1,2,3],2,2)     # passes in a list containing the sheets to be made into graphs,
                                    # and the dimensions to create the resulting grid of graphs

    plt.show()                      #left out of main program, because apparently it causes spyder to crash?
                                    #honestly I dont know how this entire system will work with your setup

                                    # Also when I do plt.show on my machine a popup comes up containing the graph that has
                                    # a download button so I'm not going to work on download button in case that works



