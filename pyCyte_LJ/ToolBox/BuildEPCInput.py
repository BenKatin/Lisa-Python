# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 11:50:24 2017

@author: avandenbroucke
"""

import csv

class BuildEPC():
    def __init__(self):
        self.filecontent = []
        return
        
    def reset(self):
        self.filecontent = []
        return()

    def header(self,date, status='OK', statusdescription='Executed with no errors'):
        self.addline(line =  ['Processed on', date] )
        self.addline(line = ['Status', status] )
        self.addline(line = ['Status Description', statusdescription])
        self.addline([])
        return
        
    def addimages(self, title='Title', imagelist=[]):
        ''' Imagelist is a list of dictionaries for each image to be displayed 
            Required keys are 'filename' and 'description '''
        self.addline(['Visualize Tab', 'Images', title ])
        for imagedict in imagelist:
            self.addline([imagedict['filename'],imagedict['description']])
        self.addline([])
        return
            
    def addline(self,line):
        self.filecontent.append(line)
        return
        
    def writetofile(self,filename='Results.csv'):
        with open(filename, 'w') as myfile:
            wr = csv.writer(myfile, delimiter=',',lineterminator='\n')
            for line in self.filecontent:
                
                #line.append('\n')
                print(line)
                wr.writerow(line)
        return        