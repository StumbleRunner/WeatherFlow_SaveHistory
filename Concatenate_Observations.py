# -*- coding: utf-8 -*-
import os
import os.path
import fnmatch
import string
import time
#import openpyxl
import urllib.request, urllib.error, urllib.parse
import requests
import json
import sys
import math
import pymysql

from time import sleep
from time import ctime
from pprint import pprint

from sqlalchemy import create_engine
from sqlalchemy.types import VARCHAR
from sqlalchemy_utils import create_database, database_exists, drop_database

from html.parser import HTMLParser
from html.entities import name2codepoint
from datetime import datetime,date,time

def C2F(itemp):
    ctemp = itemp*1.8+32
    return ctemp

def Hidx(T,R):
    T2=T*T
    R2=R*R
    c1= -42.379
    c2= 2.04901523
    c3= 10.14333127
    c4= -0.22475541
    c5= -6.83783e-3
    c6= -5.481717e-2
    c7= 1.22874e-3
    c8= 8.5282e-4
    c9= -1.99e-6
    Hidx = c1+c2*T+c3*R+c4*T*R+c5*T2+c6*R2+c7*T2*R+c8*T*R2+c9*T2*R2
    return Hidx

def WindChill(T,G):
    WindChill = 35.74+(0.6215*T)-(35.75*(G**0.16))+(0.4275*T*(G**0.16))
    return WindChill
    
ldp = lambda t,rh: math.log((rh+0.1)/100.0)+17.62*t/(243.12+t)


# device info
stationID = "2049"
airDeviceID = "3781"
skyDeviceID = "10632"
API_Key = "api-key"

#database info
db_host = "localhost"
db_user = "root"
db_pass = "password"
database= "Weather"


try:
    conn = pymysql.connect(host = db_host,
                           user=db_user,
                           passwd=db_pass,
                           db = database)
except e:
    print(("Error %d: %s" % (e.args[0],e.args[1])))
    sys.exit(1)
 
conn.autocommit = True
cursor = conn.cursor(pymysql.cursors.DictCursor)

ThreeHours=3*3600

requestStr='https://swd.weatherflow.com/swd/rest/observations/station/%s?api_key=%s' % (stationID,API_Key)
requestStrAir='https://swd.weatherflow.com/swd/rest/observations/device/%s?api_key=%s8&day_offset=' % (airDeviceID,API_Key)
requestStrSky='https://swd.weatherflow.com/swd/rest/observations/device/%s?api_key=%s8&day_offset=' % (skyDeviceID,API_Key)

while (1==1):
    try:
        response = requests.get(requestStrAir)
        page = response.text
        #parser.feed(page)
        #print json.dumps(page)
        print("======================================")
        AirData = json.loads(page)
        response = requests.get(requestStrSky)
        page = response.text
        SkyData = json.loads(page)
        #pprint(data)
        if (AirData['obs']):
            obsA = AirData['obs'][0]
            obsS = SkyData['obs'][0]

            timeA = obsA[0]
            press = obsA[1]
            temp  = obsA[2]
            humid = obsA[3]
            light = obsA[4]
            ldist = obsA[5]
            battA = obsA[6]
            #dewpt = 234.04*(math.log(humid/100.0)+17.625*temp/(243.04+temp))/(17.625-math.log(humid/100.0)-17.625*temp/(243.04+temp))
            dpp = ldp(temp,humid)
            dewpt = C2F(243.12*dpp/(17.62-dpp))
            vapor = (humid/100.0)*6.112*math.exp(17.67*temp/(temp+243.5))

            # compute sea level pressure
            P0 = 1013.25
            Psta = press
            Rd = 287.05
            GammaS = 0.0065
            g = 9.80665
            T0 = 288.15
            Elev = 806.4*0.3048 # meters
            psea2 = Psta * (1 + ((P0/Psta)**((Rd*GammaS)/g)) * ((GammaS*Elev)/T0))**(g/(Rd*GammaS))

            # compute wet bulb temperature
            tw = temp
            rhs = humid+1.0
            patm = press/P0
            while (rhs>humid):
                tw = tw-0.001
                A = 611.2*math.exp(17.502*tw/(240.97+tw))-66.8745*(1+0.00115*tw)*patm*(temp-tw)
                B = 6.112*math.exp(17.502*temp/(240.97+temp))
                rhs = A/B
            wetb = C2F(tw)
            deltaT = C2F(temp)-wetb

            # compute heat index
            T=C2F(temp)
            R=humid
            HeatIdx=T
            Feels=T
            if (T>=80 and R>=40):
                HeatIdx = Hidx(T,R)
                if (HeatIdx>T):
                    Feels = HeatIdx
            
            query = "select TimeStamp,Pressure from AirObs where TimeStamp="+str(timeA-ThreeHours)
            cursor.execute(query)
            row = cursor.fetchone()
            Ptrnd = 0
            if (row):
                Ptrnd = press - row['Pressure']

            WindChill=C2F(temp)

            timeS  = obsS[0]
            lux    = obsS[1]
            uv_idx = obsS[2]
            rain   = obsS[3]
            wind_l = obsS[4]
            wind_a = obsS[5]
            wind_g = obsS[6]
            wind_d = obsS[7]
            battS  = obsS[8]
            solar  = obsS[10]

            print('-')
            print(obsS)
            print('-')

            if (wind_d==None):
                wind_d = -1
            rain_rate = rain*60.0
            temp = C2F(temp)
            wc=temp

            if (temp<=50) and (wind_g>=5):
                 wc = WindChill(temp,wind_g)
 
            if (temp>=80):
                feels = HeatIdx
            elif (temp<=50) and (wind_g>=5):
                feels = wc
            else:
                feels = temp

            print("time: ", ctime(timeA))
            print("temp: ", temp)
            print("dew:  ", C2F(dewpt))
            print("delta:", deltaT*1.8)
            print("feels like: ",feels)
            print("heat index: ",HeatIdx)
            print()
            print("humidity:", humid,"%")
            print()
            print("UV Index:  ",uv_idx)
            print("solar rad: ",solar)
            print("brightnss: ",lux)
            print()
            print("pressure:", press)
            print("SL press:", psea2)
            print("air dens: ", vapor)
            print()
            print("Avg Wind:  ",wind_a)
            print("Wind Gust: ",wind_g)
            print("Wind Lull: ",wind_l)
            print("Wind Chill: ",wc)
            print("Wind Dir  : ",wind_d)

            query = 'insert into AirObs\
                    (TimeStamp,Pressure,AirTemp,RelHumidty,LightningCount,LightningLastDist,Battery,DeltaT,DewPoint,FeelsLike,HeatIndex,PressureTrend,SeaLevelPressure,VaporPressure,WetBulbTemp) values("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")'\
                    %(timeA, press, temp, humid, light, ldist, battA, deltaT*1.8, C2F(dewpt), feels, HeatIdx, Ptrnd, psea2, vapor, C2F(wetb))

            #print query
            cursor.execute(query)

            query = 'insert into SkyObs\
                    (TimeStamp,Lux,UVindex,PrecipAccum,WindLull,WindAvg,WindGust,WindDirection,WindChill,Battery,RainRate,SolarRadiation) values("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")'\
                    %(timeS, lux, uv_idx, rain, wind_l, wind_a, wind_g, wind_d, wc, battS, rain_rate, solar)
            #print query
            cursor.execute(query)
            conn.commit()

    except:
        x=1
        print("==")
        print("Exception:",sys.exc_info()[0]," [",sys.exc_info()[1],"]")
        print("==")
#    finally:
#        x=1
#        print "=="
    sleep(60)
     
print()
print("All done")
# Fini!
