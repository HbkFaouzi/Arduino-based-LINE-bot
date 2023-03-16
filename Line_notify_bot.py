#!/usr/bin/python
#coding:utf-8
#python -m serial.tools.list_ports #Check which PORT can be used
import datetime
import time
import serial
import urllib.request
import os
import csv
import requests

# Modify according to the content of your scepter
token = 'your Token'


SaveFile_Path =  "PATH"' # File path to save

def lineNotifyMessage(token, msg):
    headers = {
        "Authorization": "Bearer " + token, 
        "Content-Type" : "application/x-www-form-urlencoded"
    }
    
    payload = {'message': msg}
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
    return r.status_code

def Process_Data(Data):
    Character_Coordinate = Data.find('Data')
    Data = Data[Character_Coordinate + 5:]
    Character_Coordinate_2 = Data.find(',')
    Data = Data[:Character_Coordinate_2]
    return Data

def Save_csv(Data):
    csv_TIME = datetime.datetime.now().strftime('%m')
    Time_read = datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')
    td_Data = list()
    td_Data.append(Time_read)
    if Data == 0:
        td_Data.append('signal 0')
        td_Data.append(0)
    else:
        td_Data.append('signal 1')
        td_Data.append(1)
    if not os.path.exists(SaveFile_Path+'%s.csv' % csv_TIME):
        f = open(SaveFile_Path+'%s.csv' % csv_TIME,"w",encoding="utf-8")
        f.close()
        # Open the output CSV file
        with open(SaveFile_Path+'%s.csv' % csv_TIME, 'w', newline='') as csvFile:
            writer = csv.writer(csvFile)# Create CSV File Writer
            writer.writerow(['Time','In/Out','Value'])# Write out - title
        print('------ "%s" Build Success  ------' % (SaveFile_Path+'%s.csv' % csv_TIME))
    else:
        print('~~~~~~ "%s" Already set up ~~~~~~' % (SaveFile_Path+'%s.csv' % csv_TIME))
    with open(SaveFile_Path+'%s.csv' % csv_TIME, 'a', newline='') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(td_Data)# Write data
    print('Store Success!!!')


COM_PORT = 'COM4'    # Specify the port name
BAUD_RATES = 9600    # Set transmission rate
ser = serial.Serial(COM_PORT, BAUD_RATES)   # Initialize serial communication ports
Status = 0 
ONcounter = 0 
OFFcounter = 0 
while True:
    try:
        ser.write(str.encode('M'))
        time.sleep(0.5)
        while ser.in_waiting:          # While serial data is received…
            data = ser.readline()  
            data = data.decode()   # Use the default UTF-8 decoding
            data = Process_Data(data)
            data = int(data)
            Time_read = datetime.datetime.now().strftime('%m/%d(%H:%M:%S)')
            Time_lineNotify = datetime.datetime.now().strftime('%H:%M')
            if data >=  273:
                ONcounter = ONcounter + 1
                OFFcounter = 0
                if Status == 0:
                    print("%d.Value:%d (%s)"%(ONcounter,data,Time_read))
            
            elif data <= 273:
                OFFcounter = OFFcounter + 1
                ONcounter = 0
                if Status == 1:
                    print("%d.Value:%d (%s)"%(OFFcounter,data,Time_read))
            
            if ONcounter == 13 and Status == 0:
                ONcounter = 0
                OFFcounter = 0
                Status = 1
                Save_csv(1)
                print("\\\\\\\***-----%s Enter Event!-----***////////" % str(Time_read))
                lineNotifyMessage(token, '% Someone broke into my house. !!!' % Time_lineNotify)
                url = " link " # The link of your linebot linked to herokuapp.com/TextSendMessage/come
                urllib.request.urlopen(url)
            elif OFFcounter == 13 and Status == 1:
                ONcounter = 0
                OFFcounter = 0
                Status = 0
                Save_csv(0)
                print("\\\\\\\***-----%s Leave event!-----***////////" % str(Time_read))
                lineNotifyMessage(token, '%s The robber departed from the house.~' % Time_lineNotify)
                url = " link " # The link of your linebot linked to herokuapp.com/TextSendMessage/back
                urllib.request.urlopen(url) 
    
    
    
    except Exception as e:
        print(e)
        ser.close()    # Clear serial communication object
        print('\\\\\\\\\\\\\Abnormal wit!//////////////')
        ser.open()
    