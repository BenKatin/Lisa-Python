import sys, getopt
#from pyCyte.PlateQC import barCodes
import datetime
import time
if __package__ is None or __package__ == '':
    from pyCyte.Devices import IntelliCap
else:
    from ..Devices import IntelliCap


def main(argv):
 #  outdir = 'C:\Temp\\'
 #  SNFile = outdir + 'PlateMaking_SN.csv'
 #  indexfile = outdir + 'Tempo__barcodes_idx.csv'
 #  InfoFile = os.path.dirname(sys.argv[0]) + '/SolutionsPlateLotVenue.csv'
   date =  datetime.datetime.now().strftime('%Y%m%d')
   ic = IntelliCap.IntelliCap()
   
 #  lutdate = ''
 #  cavity = '0'
 #  lot = '0'
 #  loc = 'B' 
 #  plastic = ''
#   desc = False
#   dummyRun = False
#   nsets = 1
#   concentration = '-'
#   volume = '-'
#   version = 2
#   sorting = True
#prepopulate venue, platelot and lutdate 
#   print(' Looking for file: ',  InfoFile)
#   
#   if ( os.path.isfile(InfoFile) ):
#       Meta = {}
#       for index, row in enumerate(csv.reader(open(InfoFile))):
#        #print(row[0], row[1])
#           Meta[row[0]] = row[1]
#       for field in Meta.keys():
#           print(' field: ', field, ', val: ', Meta[field])
#           if field.lower() == 'venue' :
#               loc = Meta[field][0].upper()
#           if field.lower() == 'platelot' :
#               lot = Meta[field]
#           if field.lower() == 'lutdate' :
#               lutdate = Meta[field]
#           if field.lower() == 'plastic' :
#               plastic = Meta[field]
#           if field.lower() == 'cavity' :
#               cavity = Meta[field]
               
   try:
      opts, args = getopt.getopt(argv,"hvC:p:",["Command="])
   except getopt.GetoptError:
      print( 'Unknown argument .. please specify: ') 
      print( 'runIntelliCap.py -v -h -C <Command>')
      sys.exit(2)
      
   for opt, arg in opts:
      if opt == '-h':
         print(' Help function .. ')
         print( 'runIntelliCap.py -h -v -C <Command>')
         print( ' -v :: verbose mode ')
         print( 'Supported Commands are : ')
         print( ic.getValidCommands() )
         sys.exit(2)
      elif opt in ("-C", "--Command"):
         Command = arg
      elif opt in ("-p", "--port"):
         serialport = arg  	  
         ic.setSerialPort(port=serialport)
      elif opt == '-v' :
         ic.verbose = True
       
      else:
         print(' Unknown option ', opt)
         print(' Exiting ')
         sys.exit(2)
     
   if Command not in ic.getValidCommands() :
       print(' Command ', Command, ' is not supported.')
       print(' Supported commands are case sensitive : ')
       print(ic.getValidCommands())
       sys.exit(2)
         
   #open port
   ret = ic.openSerialPort()
   
   if ret < 0 :
       print('Error opening port')
       print('Exiting')
       sys.exit(2)
   stat = ic.status()
   
   
   ret = 0
   
   if Command == 'cap':
       print(' Caveat: No way to detect if already capped !')
       ret = ic.cap()
   elif Command == 'decap':
       # check if already decapped
       stat = ic.status()
       stat = ic.status()
       if 'StatusRecap' not in stat:
           ret = ic.decap()
       else:
           print('Already decapped !')
   elif Command == 'openTray':
       stat = ic.status()
       stat = ic.status()
       if 'StatusRecap' in stat:
           print('Tray already open')
       else:    
           ret = ic.openTray()
   elif Command == 'closeTray':
       ret = ic.closeTray()
   elif Command == 'status':
       ret = ic.status()
       print('Status :: ', ret)
   elif Command == 'beReady' :
       stat = ic.status()
       stat = ic.status()
       if 'StatusSleep' in stat:
           ret = ic.beReady()
           if not(isinstance(ret, str)):
              if ret == 0 :
       # there is no return to catch. Just sleeping some 15 sec,if beReady didn't timeout
                   time.sleep(15)
       else:
           print('Device not in Sleep Mode ') 
   elif Command == 'standby' :
       stat = ic.status()
       stat = ic.status()
       if 'StatusSleep' not in stat:
           if 'StatusRecap' in stat:
               print('Can\'t go to Standby mode: Caps present in Device')
           else:          
               ret = ic.standby()
       else:
           print('Device already in sleep mode')
       
   
   ic.closeSerialPort()
    
   if not(isinstance(ret, str)):
       if ret < 0 :
           print('Command ', Command, ' not succesfully executed.')
           print('Exiting')
           sys.exit(2)
       
   return    
       
       
   
   return   
       
if __name__ == "__main__":
   main(sys.argv[1:])