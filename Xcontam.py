import os
import matplotlib.pyplot as plt
import numpy as numpy
import pandas as pandas
import xlrd
import csv
from scipy.stats import ttest_ind
from itertools import combinations
from scipy.stats import f_oneway

class ReadPickList:

    def __init__(self,filename):
        self.df = pandas.read_csv(filename, delimiter=',')


    def getData(self):
        return self.df



class GetReaderFiles:
    def __init__(self,filename):
        self.wb = pandas.ExcelFile(filename)

    def GetSheetNames(self):
        return self.wb.sheet_names

    def GetSheet(self, name):
        return self.wb.parse(name)

#Given a dataframe with 24 columns and collumn names as integers 1-24, returns all the unfilled wells for a few patterns
# datatype=0 means no filled wells, 1 = checkerboard, 2 = x2, 3 = x3
def extractZeros(data,datetype = 0):
    list = []
    if (datetype == 0):
        for x in range(1,25):
            dfList = data[x].tolist()
            list.extend(dfList)

    elif (datetype == 1):
        for x in range(1,25):
            dfList = data[x].tolist()
            if(x%2 == 0):
                list.extend(dfList[1::2])
            else:
                list.extend(dfList[::2])
    elif (datetype == 2):
        for x in range(1,25):
            dfList = data[x].tolist()
            if(x%2 == 0):
                list.extend(dfList)
            else:
                list.extend(dfList[1::2])
    elif (datetype == 3):
        for x in range(1,25):
            dfList = data[x].tolist()
            if(x%3 == 1):
                list.extend(dfList[1::3])
                list.extend(dfList[2::3])
            else:
                list.extend(dfList)
    return list



if __name__ == "__main__":
    #picking the picklist for target
    pl = ReadPickList("X_contam/X_contam/96PP_checks_00_RR00_100nL.csv")

    #getting the dataframe from the picklist
    picklist = pl.getData()

    #dropping the top row from the dataframe
    picklist = picklist.drop('Source',axis = 1)

    #picking the excel reader files
    rf = GetReaderFiles("ReaderFiles/ReaderFiles/nL_Read/20180817_111853_RawVolumeOutput.xlsx")

    #getting the sheetnames from the excel file
    sheetnames = rf.GetSheetNames()

    #getting dataframe from first sheet of excel file
    x2 = rf.GetSheet(sheetnames[0])

    # getting dataframe from second sheet of excel file
    x3 = rf.GetSheet(sheetnames[1])

    #getting blank data sheet from excel file
    blank = rf.GetSheet(sheetnames[4])

    #Extracting the positions that should be zero from the differnt sheets, Data type 1 = checkerboard, 2 = data every 2 spaces, 3 = data every 3 spaces
    x2Data = extractZeros(x2, datetype=2)
    x3Data = extractZeros(x3, datetype=3)
    blankData = extractZeros(blank, datetype=0)

    #performing test, testing if there is a difference between the mean values of the population  t = test value p = probability of outcome assuming no difference between means of population
    t, p = f_oneway(*{'x2': x2Data, 'x3': x3Data, 'blank' : blankData}.values())
    print("p value:" + str(p))
    print("t value: " + str(t))

    t, p = f_oneway(*{'x2': [1,2], 'x3': [1,2], 'blank': [1,2.001]}.values())
    print(p)
    print(t)




