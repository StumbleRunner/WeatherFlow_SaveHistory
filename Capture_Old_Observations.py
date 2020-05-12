# -*- coding: utf-8 -*-
import os
import os.path
import string
import time
#import urllib.request, urllib.error, urllib.parse
import requests
import json
import sys
import math

import pymysql

from time import sleep
from time import ctime
from time import time as TIME
from datetime import datetime,date,time,timedelta

#convert celsius to fahrenheit
def C2F(itemp):
    ctemp = itemp*1.8+32
    return ctemp

#compute heat index
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

#compute wind chill
def WindChill(T,G):
    WindChill = 35.74+(0.6215*T)-(35.75*(G**0.16))+(0.4275*T*(G**0.16))
    return WindChill
    
proxies = {
}

# device info
airDeviceID = "3781"
skyDeviceID = "10632"
API_Key = "api-key"

#database info
db_host = "localhost"
db_user = "root"
db_pass = "password"
database= "Weather"

#convert meters per second into miles per hour, if you like mps set this to 1
mps2mph = 2.237

print("Capturing Observations for stations air(%s), sky(%s) to database: %s" %(airDeviceID,skyDeviceID,database))
try:
    conn = pymysql.connect(host = db_host,
                           user=db_user,
                           passwd=db_pass,
                           db = database)
except pymysql.Error as e:
    print("Error %d: %s" % (e.args[0],e.args[1]))
    sys.exit(1)

conn.autocommit = True
cursor = conn.cursor(pymysql.cursors.DictCursor)

ThreeHours=3*3600

requestStrAir='https://swd.weatherflow.com/swd/rest/observations/device/%s?api_key=%s8&day_offset=' % (airDeviceID,API_Key)
requestStrSky='https://swd.weatherflow.com/swd/rest/observations/device/%s?api_key=%s8&day_offset=' % (skyDeviceID,API_Key)

daysBack = 1

if len(sys.argv)>1:
    daysBack = int(sys.argv[1])

dayRange = list(range(daysBack,-1,-1))

#compute dew point parameter
ldp = lambda t,rh: math.log((rh+0.1)/100.0)+17.62*t/(243.12+t)

#create date string from time delta
dtl = lambda day: date.strftime(datetime.now()-timedelta(day),"%a %b %d %Y")

T=0
Feels=0

for day in dayRange:
    #
    # Get Air Device data
    #
    requestStr=requestStrAir+str(day)
    #print requestStr
    response = requests.get(requestStr, proxies=proxies)
    page = response.text
    data = json.loads(page)
    try:
        d = data['obs']
    except:
        st=sys.exc_info()[0]
        se=sys.exc_info()[1]
        print(data)
        print(st)
        print(se)
        x=1/0
            
    if (data['obs']):
        print("(%d) %s\tAir (%d)" %(day,dtl(day),len(data['obs'])))
        for obs in data['obs']:
            timeA = obs[0]
            press = obs[1]
            temp  = obs[2]
            humid = obs[3]
            light = obs[4]
            ldist = obs[5]
            batt  = obs[6]

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
            
            # need to pull the pressure data from three hours ago to compute the pressure trend
            query = "select TimeStamp,Pressure from AirObs where TimeStamp="+str(timeA-ThreeHours)
            #print query
            cursor.execute(query)
            row = cursor.fetchone()
            Ptrnd = 0
            if (row):
                Ptrnd = press - row['Pressure']

            query = 'insert into AirObs\
                    (TimeStamp,Pressure,AirTemp,RelHumidty,LightningCount,LightningLastDist,Battery,DeltaT,DewPoint,FeelsLike,HeatIndex,PressureTrend,SeaLevelPressure,VaporPressure,WetBulbTemp) values("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")'\
                    %(timeA, press, T, humid, light, ldist, batt, deltaT, dewpt, Feels, HeatIdx, Ptrnd, psea2, vapor, wetb)
            #print query
            try:
                cursor.execute(query)
                conn.commit()
            except:
                st=sys.exc_info()[0]
                se=sys.exc_info()[1]
                if (se.args[0] != 1062):
                    print("==")
                    print("Query: ",query)
                    print("Exception:",st," [",se,"]")
                    print("==")
                #break
                
    else:
        print(day,": ")

    #
    # Get Sky Device data
    #
    requestStr=requestStrSky+str(day)
    #print requestStr
    response = requests.get(requestStr, proxies=proxies)
    page = response.text
    data = json.loads(page)
    try:
        d = data['obs']
    except:
        st=sys.exc_info()[0]
        se=sys.exc_info()[1]
        print(data)
        print(st)
        print(se)
        x=1/0

    if (data['obs']):
        print("(%d) %s\tSky (%d)" %(day,dtl(day),len(data['obs'])))
        for obs in data['obs']:
            timeS  = obs[0]
            lux    = obs[1]
            uv_idx = obs[2]
            rain   = obs[3]
            wind_l = obs[4]
            wind_a = obs[5]
            wind_g = obs[6]
            wind_d = obs[7]
            batt   = obs[8]
            solar  = obs[10]

            if (wind_d == "None"):
                x=1/0
                
            rain_rate = rain*60.0

            # need to pull the recent temp data from the airobs table to compute the windchill
            query = "select TimeStamp,AirTemp,FeelsLike from AirObs where TimeStamp=" +str(timeS)
            cursor.execute(query)
            row = cursor.fetchone()

            wc    = T
            if (row):
                T     = row['AirTemp']
                Feels = row['FeelsLike']
                wc    = T
                windSpd = wind_g*mps2mph
                if (T<=50) and (windSpd>=5): # Wind chill only applies if the temperature is 50 degrees or less and the wind speed is 5 mph or higher
                    wc = WindChill(T,windSpd)
                    Feels = wc
                    query = "update AirObs set FeelsLike = %s where TimeStamp= %s" % (Feels,timeS)
                    cursor.execute(query)


            query = 'insert into SkyObs\
                    (TimeStamp,Lux,UVindex,PrecipAccum,WindLull,WindAvg,WindGust,WindDirection,WindChill,Battery,RainRate,SolarRadiation) values("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")'\
                    %(timeS, lux, uv_idx, rain, wind_l, wind_a, wind_g, wind_d, wc, batt, rain_rate, solar)
            try:
                cursor.execute(query)
                conn.commit()
            except:
                st=sys.exc_info()[0]
                se=sys.exc_info()[1]                
                if (se.args[0] != 1062):
                    print("==")
                    print("Query: ",query)
                    print("Exception:",st," [",se,"]")
                    print("==")
                #break

print()
print("All done")
# Fini!
