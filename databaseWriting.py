# -*- coding: utf-8 -*-
"""
Created on 11/14/2019

@author: will


"""

import mysql.connector
import re
import glob
import os
from datetime import datetime
import time
import urllib.request
import sys
import json

global DB_ADDRESS, DB_USERNAME, DB_PASSWORD, DB_NAME, inverterLogDirPath

DB_ADDRESS = "128.153.21.86"
DB_USERNAME = "pythondev"
DB_PASSWORD = "WMDccp2018!"
DB_NAME = "blackboard_gui"

inverterLogDirPath = 'C:\\Users\\Labadmin\\Documents\\Inverter\\inverter_log_files'

def findLastEntry():
    global DB_ADDRESS, DB_USERNAME, DB_PASSWORD, DB_NAME, inverterLogDirPath
    
    mydb = mysql.connector.connect(host=DB_ADDRESS, user=DB_USERNAME, passwd=DB_PASSWORD, database=DB_NAME)
    mycursor = mydb.cursor()
    sql = ("SELECT MAX(time) FROM inverterWeatherData")
    mycursor.execute(sql)
    result = mycursor.fetchone()
    mycursor.close()
    mydb.close()

    return result[0]

def roundTimeUpMinute(timestampObject):
    # Rounds the time up by one minute and returns the year,month,day,hour,and minute as strings
    timestamp = datetime.strftime(timestampObject, '%Y-%m-%d %H:%M')
    year = int(timestamp[0:4])
    month = int(timestamp[5:7])
    day = int(timestamp[8:10])
    minute = int(timestamp[14:16])
    hour = int(timestamp[11:13])

    months = [31,28,31,30,31,30,31,31,30,31,30,31]

    minute = minute + 1
    if minute == 60:
        minute = 0
        hour = hour + 1
        if hour == 24:
            hour = 0
            day = day + 1
            leapYear = 0
            if month == 2:
                leapCheck = year % 4
                if leapCheck == 0:
                    leapYear = 1
            if leapYear == 1 and day == 29 and month == 2:
                j = 1
            else:
                daysOfMonth = months[month - 1]      
                if day >= daysOfMonth + 1:
                    day = 1
                    month = month + 1
                    if month == 13:
                        month = 1
                        year = year + 1
                
    year = str(year)
    if month < 10:
        month = '0' + str(month)
    else:
        month = str(month)
    if day < 10:
        day = '0' + str(day)
    else:
        day = str(day)
    if hour < 10:
        hour = '0' + str(hour)
    else:
        hour = str(hour)
    if minute < 10:
        minute = '0' + str(minute)
    else:
        minute = str(minute)

    return [year,month,day,hour,minute]

def getWeatherData(lastEntryTimeObject):
    lastEntryTime = datetime.strftime(lastEntryTimeObject, '%Y-%m-%d %H:%M')
    year = lastEntryTime[0:4]
    month = lastEntryTime[5:7]
    day = lastEntryTime[8:10]
    time = lastEntryTime[11:16]
    if time == '23:58':
        timestamp = year+'-'+month+'-'+day+' 23:59'
        [year,month,day,hour,minute] = roundTimeUpMinute(datetime.strptime(timestamp, '%Y-%m-%d %H:%M'))
        urlDate = year + '-' + month + '-' + day
        newTimeStamp = timestamp
    else:
        [year,month,day,hour,minute] = roundTimeUpMinute(lastEntryTimeObject)
        urlDate = year + '-' + month + '-' + day
        newTimeStamp = year+'-'+month+'-'+day+' '+hour+':'+minute

    url = 'https://cuwx.clarkson.edu/json/NoaaExt-' + urlDate + '.json'
    data = urllib.request.urlopen(url)
    jData = data.read()
    fullJsonData = jData.decode()

    length = int(len(fullJsonData))

    # find the ends of each json in the daily file
    ends = [e.start(0) for e in re.finditer('}{',fullJsonData)]
    i = 0
    while i < len(ends):
        ends[i] = ends[i] + 1
        i = i + 1
    ends.append(length)

    # uses the ends to create an array of json strings
    jsons = []
    j = 0
    lengthCheck = len(fullJsonData[0:ends[0]])
    while j < len(ends):
        k = j - 1
        if j == 0:
            singleJson = fullJsonData[0:ends[0]]
        else:
            singleJson = fullJsonData[ends[k]:ends[j]]
            
        leng = len(singleJson)
        if lengthCheck < (leng - (lengthCheck/2)):
            invalid = fullJsonData.find('Invalid Request!')
            fullJsonData = re.sub('Invalid Request!', '', fullJsonData)

            n = 1
            while n < (len(ends)-j):
                ends[k+n] = ends[k+n]-16
                n = n + 1
                
            ends = ends[:j] + [invalid] + ends[j:]
            j = j - 1
        else:
            jsons.append(singleJson)
        j = j + 1
    
    # loads the data from each json in the array
    weatherData = []
    m = 0
    while m < len(jsons):
        singleWeatherData = json.loads(jsons[m])
        weatherData.append(singleWeatherData)
        m = m + 1

    # grabs specific data from the weather data arrays
    times = []
    windSpeedsMS = []
    tempsC = []
    windDirection = []
    pressure = []
    humidity = []
    dewpointC = []
    returnedWeatherData = []
    p = 0
    
    while p < len(weatherData):
        # Records wether there are 2 digits in the day or not for indexing
        if weatherData[p]['observation_time_rfc822'][6].isdigit():
            dayCheck = 1
        else:
            dayCheck = 0
        if dayCheck:
            singleTimeString = weatherData[p]['observation_time_rfc822'][5:22]
        else:
            singleTimeString = weatherData[p]['observation_time_rfc822'][5:21]
        singleTime = datetime.strptime(singleTimeString, '%d %b %Y %H:%M')
        if singleTime == datetime.strptime(newTimeStamp, '%Y-%m-%d %H:%M'):
            n = p
            break
        elif p == len(weatherData) - 1:
            [year,month,day,hour,minute] = roundTimeUpMinute(datetime.strptime(newTimeStamp, '%Y-%m-%d %H:%M'))
            newTimeStamp = year+'-'+month+'-'+day+' '+hour+':'+minute
            q = 0
            while q < len(weatherData):
                if dayCheck:      
                    singleTimeString = weatherData[q]['observation_time_rfc822'][5:22]
                else:
                    singleTimeString = weatherData[q]['observation_time_rfc822'][5:21]
                singleTime = datetime.strptime(singleTimeString, '%d %b %Y %H:%M')
                if singleTime == datetime.strptime(newTimeStamp, '%Y-%m-%d %H:%M'):
                    n = q + 1
                    break
                else:
                    q = q + 1
            break
        else:
            p = p + 1
            n = 0
    
    while n < len(weatherData):
        if dayCheck:            # Checks wether the day is one or two digits for indexing date
            singleTimeString = weatherData[n]['observation_time_rfc822'][5:22]
        else:
            singleTimeString = weatherData[n]['observation_time_rfc822'][5:21]            
        singleTimeObject = datetime.strptime(singleTimeString, '%d %b %Y %H:%M')
        singleTime = datetime.strftime(singleTimeObject, '%Y-%m-%d %H:%M')
        singleWindSpeedMS = 0.44704*float(weatherData[n]['wind_mph'])
        singleTempC = float(weatherData[n]['temp_c'])
        singleWindDir = int(weatherData[n]['wind_degrees'])
        singlePressure = float(weatherData[n]['pressure_mb'])
        singleHumidity = float(weatherData[n]['relative_humidity'])
        singleDewpointC = float(weatherData[n]['dewpoint_c'])
        singleWeatherData = [singleTime,singleTempC,singleWindSpeedMS,
                             singleWindDir,singlePressure,
                             singleHumidity,singleDewpointC]

        # Only appends lines where date object is later than most recent database
        if singleTimeObject > datetime.strptime(lastEntryTime,'%Y-%m-%d %H:%M'):
            #times.append(singleTime)
            #windSpeedsMS.append(singleWindSpeedMS)
            #tempsC.append(singleTempC)
            #windDirection.append(singleWindDir)
            #pressure.append(singlePressure)
            #humidity.append(singleHumidity)
            #dewpointC.append(singleDewpointC)
            returnedWeatherData.append(singleWeatherData)
        n = n + 1

    d = 0
    while d < len(returnedWeatherData) - 1:
        if returnedWeatherData[d][0] == returnedWeatherData[d+1][0]:
            del returnedWeatherData[d+1]
            d = d - 1
        if returnedWeatherData[d][0] == lastEntryTime:
            del returnedWeatherData[d]
            d = d - 1
        d = d + 1

    return returnedWeatherData

def chooseInverterLogFile(lastEntryTime):
    global DB_ADDRESS, DB_USERNAME, DB_PASSWORD, DB_NAME, inverterLogDirPath
    
    fileList = glob.glob(inverterLogDirPath + '\\*.log')
    fileTimeStamp = roundTimeUpMinute(lastEntryTime)
    fileDate = fileTimeStamp[0]+'-'+fileTimeStamp[1]+'-'+fileTimeStamp[2]
    if fileTimeStamp[3]+':'+fileTimeStamp[4] == '23:59':
        rU = fileTimeStamp[0]+'-'+fileTimeStamp[1]+'-'+fileTimeStamp[2]+' '+fileTimeStamp[3]+':'+fileTimeStamp[4]
        roundedUp = roundTimeUpMinute(datetime.strptime(rU, '%Y-%m-%d %H:%M'))
        fileDate = roundedUp[0]+'-'+roundedUp[1]+'-'+roundedUp[2]
        
    inverterLogFilePath = ''
    i = 0
    while i < len(fileList):
        if fileList[i] == inverterLogDirPath + '\\' + fileDate + '.log':
            inverterLogFilePath = fileList[i]
        i = i + 1

    return inverterLogFilePath

def getInverterData(lastEntryTime):
    global DB_ADDRESS, DB_USERNAME, DB_PASSWORD, DB_NAME, inverterLogDirPath
    
    inverterLogFilePath = chooseInverterLogFile(lastEntryTime)

    if inverterLogFilePath == '':
        print('ERROR-001: Could not find next expected inverter file')
        endEnergy = 0
        #cont = input('Would you like to continue? (y/n)')
        cont = 'y'
        if cont == 'y' or cont == 'Y' or cont == 'yes' or cont =='Yes':
            inverterData = []
        else:
            sys.exit()

    else:
        inverterFile = open(inverterLogFilePath)  
        inverterLines = inverterFile.read().splitlines()

        inverterDateString = re.search('Date: \d+/\d+/\d+',inverterLines[2]).group(0)[6:]
        inverterDate = datetime.strptime(inverterDateString, '%d/%m/%Y')
        usefulLines = []
        i = 0
        while i < len(inverterLines):
            try:
                if inverterLines[i][0].isdigit():
                    usefulLines.append(inverterLines[i])
            except:
                pass
            i = i + 1

        endSemis = [s.start(0) for s in re.finditer(';',usefulLines[-1])]
        endEnergy = float(usefulLines[-1][endSemis[14]+1:endSemis[15]])
        inverterTime = []
        VDC1 = []
        IDC1 = []
        PDC1 = []
        VDC2 = []
        IDC2 = []
        PDC2 = []
        VAC = []
        IAC = []
        PAC = []
        TINV = []
        TINT = []
        ENERGY = []
        RISO = []
        ILEAK = []
        IRR = []
        GENFREQ = []
        inverterData = []
        j = 0
        while j < len(usefulLines):
            semis = [s.start(0) for s in re.finditer(';',usefulLines[j])]
            singleInverterTimeString = usefulLines[j][0:5]
            singleInverterTimeObject = datetime.strptime(inverterDateString+'-'+singleInverterTimeString, '%d/%m/%Y-%H:%M')
            singleInverterTime = datetime.strftime(singleInverterTimeObject, '%Y-%m-%d %H:%M')
            singleVDC1 = float(usefulLines[j][semis[3]+1:semis[4]])
            singleIDC1 = float(usefulLines[j][semis[4]+1:semis[5]])
            singlePDC1 = float(usefulLines[j][semis[5]+1:semis[6]])
            singleVDC2 = float(usefulLines[j][semis[6]+1:semis[7]])
            singleIDC2 = float(usefulLines[j][semis[7]+1:semis[8]])
            singlePDC2 = float(usefulLines[j][semis[8]+1:semis[9]])
            singleVAC = float(usefulLines[j][semis[9]+1:semis[10]])
            singleIAC = float(usefulLines[j][semis[10]+1:semis[11]])
            singlePAC = float(usefulLines[j][semis[11]+1:semis[12]])
            singleTINV = float(usefulLines[j][semis[12]+1:semis[13]])
            singleTINT = float(usefulLines[j][semis[13]+1:semis[14]])
            singleENERGY = float(usefulLines[j][semis[14]+1:semis[15]])
            singleRISO = float(usefulLines[j][semis[15]+1:semis[16]])
            singleILEAK = float(usefulLines[j][semis[16]+1:semis[17]])
            singleIRR = float(usefulLines[j][semis[17]+1:semis[18]])
            singleGENFREQ = float(usefulLines[j][semis[18]+1:semis[19]])
            singleInverterData = [singleInverterTime,singleVDC1,singleIDC1,
                                  singlePDC1,singleVDC2,singleIDC2,
                                  singlePDC2,singleVAC,singleIAC,singlePAC,
                                  singleTINV,singleTINT,singleENERGY,singleRISO,
                                  singleILEAK,singleIRR,singleGENFREQ]

            #inverterTime.append(singleInverterTime)
            #VDC1.append(singleVDC1)
            #IDC1.append(singleIDC1)
            #PDC1.append(singlePDC1)
            #VDC2.append(singleVDC2)
            #IDC2.append(singleIDC2)
            #PDC2.append(singlePDC2)
            #VAC.append(singleVAC)
            #IAC.append(singleIAC)
            #PAC.append(singlePAC)
            #TINV.append(singleTINV)
            #TINT.append(singleTINT)
            #ENERGY.append(singleENERGY)
            #RISO.append(singleRISO)
            #ILEAK.append(singleILEAK)
            #IRR.append(singleIRR)
            #GENFREQ.append(singleGENFREQ)
            inverterData.append(singleInverterData)

            j = j + 1
            
    return [inverterData,endEnergy]

def alignData(lastSQLEntry):
    weatherData = getWeatherData(lastSQLEntry)
    [inverterData,endEnergy] = getInverterData(lastSQLEntry)
    lengthWeather = len(weatherData)
    lengthInverter = len(inverterData)
    
    fullData = []
    i = 0
    if lengthInverter == 0:
        while i < lengthWeather:
            singleFullData = weatherData[i] + [0,0,0,0,0,0,0,0,0,0,0,endEnergy,0,0,0,0]
            fullData.append(singleFullData)
            i = i + 1
    else:
        while i < lengthWeather:
            j = 0
            while j < lengthInverter:
                if weatherData[i][0] == inverterData[j][0]:
                    singleFullData = weatherData[i] + inverterData[j][1:]
                    fullData.append(singleFullData)
                    break
                elif j == lengthInverter - 1:
                    singleFullData = weatherData[i] + [0,0,0,0,0,0,0,0,0,0,0,endEnergy,0,0,0,0]
                    fullData.append(singleFullData)
                j = j + 1
            i = i + 1

    return fullData

def sendData(data):
    global DB_ADDRESS, DB_USERNAME, DB_PASSWORD, DB_NAME, inverterLogDirPath

    mydb = mysql.connector.connect(host=DB_ADDRESS, user=DB_USERNAME, passwd=DB_PASSWORD, database=DB_NAME)
    mycursor = mydb.cursor()
    sql = ("INSERT INTO inverterWeatherData "
           "(time, TempC, windSpeedMS, WindDir, PressureMB, Humidity, DewpointC, VDC1, IDC1, PDC1, VDC2, IDC2, PDC2, VAC, IAC, PAC, TINV, TINT, ENERGY, RISO, ILEAK, IRR, GENFREQ) "
           "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

    insertData = (data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7],
                  data[8],data[9],data[10],data[11],data[12],data[13],data[14],data[15],
                  data[16],data[17],data[18],data[19],data[20],data[21],data[22])
    mycursor.execute(sql,insertData)
        
    mydb.commit()
    mycursor.close()
    mydb.close()


def runRepeatedly():
    while True:
        pickupTime = time.time()
        lastSQLEntry = findLastEntry()
        data = alignData(lastSQLEntry)
        k = 0
        while k < len(data):
            insertData = data[k]
            sendData(insertData)
            k = k + 1
        #break
        timeDiff = time.time() - pickupTime
        while True:
            if timeDiff >= 60:
                break
            else:
                time.sleep(60-timeDiff)
                break

runRepeatedly()
