#!/usr/bin/python
#coding:utf-8
#python -m serial.tools.list_ports #哪些PORT可以使用
import datetime
import time
import serial
import urllib.request
import os
import csv
import requests

# 修改為你的權杖內容
token = 'rtNskOVlgiuSeaxeFOYyCvG02AcsZeBfGJUiBWOlrZn'


SaveFile_Path =  r'D:/RichRong/' #要儲存的檔案路徑

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
        td_Data.append('離開')
        td_Data.append(0)
    else:
        td_Data.append('進入')
        td_Data.append(1)
    if not os.path.exists(SaveFile_Path+'%s.csv' % csv_TIME):
        f = open(SaveFile_Path+'%s.csv' % csv_TIME,"w",encoding="utf-8")
        f.close()
        # 開啟輸出的 CSV 檔案
        with open(SaveFile_Path+'%s.csv' % csv_TIME, 'w', newline='') as csvFile:
            writer = csv.writer(csvFile)# 建立 CSV 檔寫入器
            writer.writerow(['Time','進出','Value'])# 寫出-標題
        print('------ "%s"建立成功 ------' % (SaveFile_Path+'%s.csv' % csv_TIME))
    else:
        print('~~~~~~ "%s"已經建立 ~~~~~~' % (SaveFile_Path+'%s.csv' % csv_TIME))
    with open(SaveFile_Path+'%s.csv' % csv_TIME, 'a', newline='') as csvFile:
        writer = csv.writer(csvFile)# 建立 CSV 檔寫入器
        writer.writerow(td_Data)# 寫出資料
    print('儲存成功!!!')


COM_PORT = 'COM4'    # 指定通訊埠名稱
BAUD_RATES = 9600    # 設定傳輸速率
ser = serial.Serial(COM_PORT, BAUD_RATES)   # 初始化序列通訊埠
Status = 0 
ONcounter = 0 
OFFcounter = 0 
while True:
    try:
        ser.write(str.encode('M'))
        time.sleep(0.5)
        while ser.in_waiting:          # 若收到序列資料…
            data = ser.readline()  # 讀取一行
            data = data.decode()   # 用預設的UTF-8解碼
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
                print("\\\\\\\***-----%s 進入事件!-----***////////" % str(Time_read))
                lineNotifyMessage(token, '%s目標進入!!!' % Time_lineNotify)
                url = "https://richrongbot.herokuapp.com/TextSendMessage/come"
                urllib.request.urlopen(url)
            elif OFFcounter == 13 and Status == 1:
                ONcounter = 0
                OFFcounter = 0
                Status = 0
                Save_csv(0)
                print("\\\\\\\***-----%s 離開事件!-----***////////" % str(Time_read))
                lineNotifyMessage(token, '%s目標離開~' % Time_lineNotify)
                url = "https://richrongbot.herokuapp.com/TextSendMessage/back"
                urllib.request.urlopen(url) 
    
    
    
    except Exception as e:
        print(e)
        ser.close()    # 清除序列通訊物件
        print('\\\\\\\\\\\\\異常!異常!異常!//////////////')
        ser.open()
    