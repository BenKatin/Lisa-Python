import os
if __package__ is None or __package__ == '':
    from pyCyte.ToolBox.NWayDBComparison import compareTables
else:
    from ..ToolBox.NWayDBComparison import compareTables

dbs = ['Alex_Tubes_1',
       'Alex_Tubes_2',
       'Alex_Tubes_3',
       'Alex_Tubes_4',
       'Alex_Tubes_5',
       'Alex_Tubes_6',
       'Alex_Tubes_7',
       'Alex_Tubes_8',
       'Alex_Tubes_9',
       'Alex_Tubes_10']

dbServer = 'lighthouse'
outputFileRoot = r'c:\compareDBs'

if not os.path.exists(outputFileRoot):
    os.makedirs(outputFileRoot)

# Leaving out CenterX and CenterT for PlateType.
compareTables(dbServer,
              dbs,
              'Axis',
              rowKeyFields=['AxisName'],
              ignoreFields=['AxisId'],  outputFilePath=os.path.join(outputFileRoot, 'Axis.txt'))

compareTables(dbServer,
              dbs,
              'Parameter',
              rowKeyFields=['PlateTypeName','GroupName', 'ParameterName'],
              ignoreFields=['ParameterId'],  outputFilePath=os.path.join(outputFileRoot, 'Parameter.txt'))

compareTables(dbServer,
              dbs,
              'PlateType',
              rowKeyFields=['PlateTypeName'],
              ignoreFields=['PlateTypeId', 'CenterX', 'CenterY'], outputFilePath=os.path.join(outputFileRoot, 'PlateType.txt'))

compareTables(dbServer,
              dbs,
              'MIPConfiguration',
              rowKeyFields=['PlateTypeName','ParameterName', 'ParameterGroup', 'Iteration'],
              ignoreFields=['MIPConfigurationID'],  outputFilePath=os.path.join(outputFileRoot, 'MIPConfiguration.txt'))

compareTables(dbServer,
              dbs,
              'Coefficient',
              rowKeyFields=['PlateTypeName','CoefficientName'],
              ignoreFields=['CoefficientId'],  outputFilePath=os.path.join(outputFileRoot, 'Coefficient.txt'))