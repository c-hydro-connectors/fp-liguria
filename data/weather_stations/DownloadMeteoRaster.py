

# -------------------------------------------------------------------------------------
# Complete library
import time
import datetime
import argparse
import json
import logging
import os
import subprocess

from lib_utils_logging import setLoggingFile
from lib_utils_time import getTimeNow, getTimeFrom, getTimeTo, \
    getTimeSteps, getTimeRun, computeTimeRestart

# -------------------------------------------------------------------------------------
# Method to get script argument(s)
def GetArgs():
    oParser = argparse.ArgumentParser()
    oParser.add_argument('-settingfile', action="store", dest="sSettingFile")
    sScriptName = oParser.prog
    oParserValue = oParser.parse_args()

    if oParserValue.sSettingFile:
        sSettingsFile = oParserValue.sSettingFile
    else:
        sSettingsFile = 'hyde_configuration_LiguriaMeteo.json'

    return sScriptName,sSettingsFile

# -------------------------------------------------------------------------------------
# Script Main
def main():

    # -------------------------------------------------------------------------------------
    # Version and algorithm information
    sProgramVersion = '1.0.0'
    sProjectName = 'HYDE'
    sAlgType = 'DataDynamic'
    sAlgName = 'Meteo data raster from Liguria DB'
    # Time algorithm information
    dStartTime = time.time()
    oDateNow = datetime.datetime.utcnow()

    sTimeArg=oDateNow.strftime('%Y%m%d%H%M')
 # Get script argument(s)
    [sScriptName, sFileSetting] = GetArgs()

    oInputData = json.load(open(sFileSetting))


    #oDrv_Data_Settings = DataAlgorithm(sFileSetting)
    #[oData_Settings, oData_Path, oData_Flags, oData_ColorMap] = oDrv_Data_Settings.getDataSettings()


    # Set logging file
    #oLogStream = setLoggingFile(oData_Path['log'])
    sFileLog=oInputData['data']['log']['folder']+oInputData['data']['log']['filename']
    oLogStream = setLoggingFile(sFileLog)


    # Define if real time or offline
    iRT= int(oInputData['time']['time_RT'])
    iDTvar= int(oInputData['time']['time_var'])
    if(iRT != 1):
        sTimeArg=oInputData['time']['time_now']

    oDateNow = datetime.datetime(int(sTimeArg[0:4]), int(sTimeArg[4:6]), int(sTimeArg[6:8]),
                                 int(sTimeArg[8:10]), int(sTimeArg[10:12]))
    iMin = oDateNow.minute;
    #iMinTimeStep=int(oData_Settings['time']['time_delta'])/60
    iMinTimeStep = int(oInputData['time']['time_delta']) / 60
    iMin = int(int(iMin /iMinTimeStep) * iMinTimeStep)  # Define the radar data time step
    oDateNow = oDateNow.replace(minute=iMin, second=0, microsecond=0)

    #iSecPast=int(oData_Settings['time']['time_delta'])*int(oData_Settings['time']['time_step'])
    iSecPast = int(oInputData['time']['time_delta']) * int(oInputData['time']['time_step'])


    oDateFrom = oDateNow - datetime.timedelta(seconds=iSecPast);
    sTimeFrom = oDateFrom.strftime('%Y%m%d%H%M')


    # Define the list of time step
    a1oTimeStep = getTimeSteps(sTimeFrom=sTimeFrom, sTimeTo=sTimeArg,
                               iTimeDelta=int(oInputData['time']['time_delta']))

    oLogStream.info(' --> Set time data ... DONE')

    #Define list of variables
    a1oVar = oInputData['algorithm']['Downloader']['Var']

    #Parameters to build command line
    sLanguage= oInputData['algorithm']['Downloader']['language']
    sScript= oInputData['algorithm']['Downloader']['script']
    sDiVar= oInputData['algorithm']['Downloader']['DiVar']
    spathgrid = oInputData['algorithm']['Downloader']['pathgrid']
    minLON= oInputData['algorithm']['Downloader']['minLON']
    maxLON = oInputData['algorithm']['Downloader']['maxLON']
    minLAT = oInputData['algorithm']['Downloader']['minLAT']
    maxLAT = oInputData['algorithm']['Downloader']['maxLAT']
    deltaGrid = oInputData['algorithm']['Downloader']['deltaGrid']
    Lambda = oInputData['algorithm']['Downloader']['lambda']
    iScaleFactor = oInputData['algorithm']['Downloader']['iScaleFactor']
    spathSave = oInputData['algorithm']['Downloader']['pathSave']
    folders = oInputData['algorithm']['Downloader']['folders']
    sDomain = oInputData['algorithm']['Downloader']['sDomain']
    sFormat = oInputData['algorithm']['Downloader']['Format']

    # -------------------------------------------------------------------------------------
    # Iterate over time steps
    a1oTimeStep = a1oTimeStep[::-1] #Reverse order of time steps
    for sTimeStep in a1oTimeStep:
        print(sTimeStep)
        oLogStream.info(sTimeStep)
        oDateNow = datetime.datetime(int(sTimeStep[0:4]), int(sTimeStep[4:6]), int(sTimeStep[6:8]),
                                    int(sTimeStep[8:10]), int(sTimeStep[10:12]))
        oDateFrom = oDateNow - datetime.timedelta(seconds=iDTvar);
        sTimeFrom = oDateFrom.strftime('%Y%m%d%H%M')
    # Iterates on variables
        for sVar in a1oVar:

            sLine=sLanguage+' '
            sLine+=sScript+' '
            sLine+=sTimeFrom+' '
            sLine+=sTimeStep+' '
            sLine+=sVar+' '
            sLine+=sDiVar+' '
            sLine+=spathgrid+sDomain+' '
            sLine+=minLON+' '
            sLine+=maxLON+' '
            sLine+=minLAT+' '
            sLine+=maxLAT+' '
            sLine+=deltaGrid+' '
            sLine+=Lambda+' '
            sLine+=iScaleFactor+' '
            sLine+=spathSave
            if folders == "3" :
                sLine+=sTimeStep[0:4]+'/'+sTimeStep[4:6]+'/'+sTimeStep[6:8]+'/'
                sFolderOut=spathSave+sTimeStep[0:4]+'/'+sTimeStep[4:6]+'/'+sTimeStep[6:8]+'/'
            sLine+=' '+sFormat

            #Build output folder
            check = os.path.exists(sFolderOut)
            if (check == False):
                oLogStream.info('Create folder for meteo data ARPAL')
                #os.makedirs(sFolderOut)
            #Execute Rscript to download files
            try:
                print(sLine);
                os.system(sLine)
            except:
                oLogStream.info('Impossible to execute R download procedure')
                oLogStream.info(sLine);

            # -------------------------------------------------------------------------------------
    # Get data time
    #oLogStream.info(' --> Set time data ... ')
    #oDrv_Time = DataTime(sTimeArg,
    #                     iTimeStep=int(oData_Settings['time']['time_step']),
    #                     iTimeDelta=int(oData_Settings['time']['time_delta']),
    #                     oTimeRefHH=oData_Settings['time']['time_refHH'])
    #oData_Time = oDrv_Time.getDataTime()
    oLogStream.info(' --> End Download Procedure')
    print("Sono qui")

#Rscript mapGRISO_griglia.R 201411101900 201411102000 RAINC 10 /home/drift/GRISO/GRISO_variabili/Grid/ 0 0 0 0 0 20 10 /home/drift/ModelloBilancio/EntellaDomain/LandData/EntellaDomain

# ----------------------------------------------------------------------------
# Call script from external library
if __name__ == "__main__":
    main()

