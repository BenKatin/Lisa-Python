# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 15:58:11 2017

@author: avandenbroucke
"""

import serial
import io
import time

class IntelliCap():
    def __init__(self):
       self.ser = serial.Serial()
       self.ser.baudrate = 9600
       self.ser.port='COM1'
       self.ser.timeout = 1
       self.ser_io = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser, 1),  newline = '\r',  line_buffering = True)
       self.verbose = False
       return
       
    def setSerialPort(self,port='COM1'):
        self.ser.port = port
        return
        
    def openSerialPort(self):    
        try:
            self.ser.open()
            if self.verbose:
                print(' opening serial port ', self.ser.port, ' ser.is_open: ', self.ser.is_open)
        except Exception as e:
            print('Failed to set port # ' , self.ser.port)
            print(e)
            return -1 
        return 0
            
        
    def closeSerialPort(self):
        self.ser.close()
        return 0
    
    def initialize(self):
        try:
            self.ser_io.write('Z')
        except Exception as e:
            print('unable to initalize device ')
            print(e)
            return -1
        return 0
    
    def standby(self):
        try:
            self.ser_io.write('j')
            return  self.checkStatus('Standby')
        except Exception as e:
            print(' Unsuccesfull standby request')
            print(e)
            return -1    
        return 0
    
    def beReady(self):
        #note :: ready gives status 'Ready' before tray is out
        try:
            self.ser_io.write('k')
            return self.checkStatus('Ready')
        except Exception as e:
            print(' Not able to be ready ')
            print(e)
            return -1
        return 0
    
    def decap(self):
        '''Retract, Decap Tubes, present'''
        ret = self.ser_io.write('h')
        out = self.ser_io.readline()
        return self.checkStatus('DecapOK')
            
     
    def cap(self):
        '''Retract, Cap Tubes, Present'''
        ret = self.ser_io.write('i')
        out = self.ser_io.readline()
        return self.checkStatus('RecapOK')
           
        
        
    def closeTray(self):
        try:
            ret = self.ser_io.write('g')
            return self.checkStatus('StatusOK')
        except Exception as e:
            print(' Failed to close Tray ')
            print(e)
            return -1
        return
    
    def openTray(self):
        try:
            ret = self.ser_io.write('f')
            return self.checkStatus('StatusOK')
        except Exception as e:
            print(' Failed to open Tray')
            print(e)
            return -1
        return
        
    def status(self):
        try:
            self.ser_io.write('a')
            stat = self.ser_io.readline()
            if self.verbose:
                print('status:: ',stat)
        except Exception as e:
            print(' Failed to get status')
            print(e)
            return -1 
        return stat
        
    def checkStatus(self,string='DecapOK', maxtime=80, sleepInSec = 1):
        runtime = 0
        while (1):
            stat = self.status()
            if (string in stat) or (runtime > maxtime):
                if runtime > maxtime:
                   print('Timeout -- time: ', runtime, ' stat:: ', stat)
                   return -1
                else:    
                   print('Done --    time: ', runtime, ' stat:: ', stat)
                   return 0
                break
            else:
               if self.verbose:
                   print(    'Busy --    time: ', runtime, ' stat:: ', stat)
               time.sleep(sleepInSec)
               runtime += sleepInSec
        return    
     
    def getValidCommands(self,print=True):
         listOfCommands = ['cap','decap','openTray','closeTray','status','initialize','standby','beReady']
         return listOfCommands  