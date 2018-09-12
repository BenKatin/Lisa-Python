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
    pl = ReadPickList("X_contam/X_contam/96PP_checks_00_RR00_100nL.csv")
    picklist = pl.getData()

    picklist = picklist.drop('Source',axis = 1)

    rf = GetReaderFiles("ReaderFiles/ReaderFiles/nL_Read/20180817_111853_RawVolumeOutput.xlsx")

    sheetnames = rf.GetSheetNames()

    x2 = rf.GetSheet(sheetnames[0])

    x3 = rf.GetSheet(sheetnames[1])

    blank = rf.GetSheet(sheetnames[4])
    x2Data = extractZeros(blank, datetype=2)
    x3Data = extractZeros(blank, datetype=3)
    blankData = extractZeros(blank, datetype=0)

    x3Data = x3Data[:len(x2Data)]
    blankData = blankData[:len(x2Data)]

    t, p = f_oneway(*{'x2': x2Data, 'x3': x3Data, 'blank' : blankData}.values())
    print(p)
    print(t)

    t, p = f_oneway(*{'x2': [1,2], 'x3': [1,2], 'blank': [1,2.001]}.values())
    print(p)
    print(t)




    #print(ttest_ind(x2['values'], blank['values']))

    #print(ttest_ind(x3['values'], blank['values']))



    #print(x3)


