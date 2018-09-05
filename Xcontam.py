import os
import matplotlib.pyplot as plt
import numpy as numpy
import pandas as pandas
import xlrd
import csv

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

if __name__ == "__main__":
    pl = ReadPickList("X_contam/X_contam/96PP_checks_00_RR00_100nL.csv")
    picklist = pl.getData()

    picklist = picklist.drop('Source',axis = 1)

    print (picklist)



    rf = GetReaderFiles("ReaderFiles/ReaderFiles/nL_Read/20180817_111853_RawVolumeOutput.xlsx")

    sheetnames = rf.GetSheetNames()

    rfsheet = rf.GetSheet(sheetnames[0])



    print(rfsheet[1][0])


