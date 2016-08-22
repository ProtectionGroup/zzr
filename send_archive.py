# -*- coding: utf-8 -*-
import requests
import re
import os
import datetime
import time
import calendar
import logging
from get_id import getserial

#рівень відладки для логування
LOG_LEVEL=logging.DEBUG


#логи в консоль
logging.basicConfig(format='%(levelname)s[%(asctime)s] %(message)s',level=LOG_LEVEL, datefmt='%m/%d/%Y %I:%M%p')

#логи у файл
logging.basicConfig(filename='/media/usb/logs/send_archive.log',format='%(levelname)s[%(asctime)s] %(message)s',level=LOG_LEVEL, datefmt='%m/%d/%Y %I:%M%p')

#підтягнути ID пристрою з файлу
#f=open('/boot/id.txt', 'r')
#s=f.readlines()
#ln = len(s)
#f.close()
#rpi_id = s[0]
#rpi_id = re.sub("^\s+|\n|\r|\s+$", '', rpi_id)
rpi_id = getserial()
logging.info("id = "+rpi_id)

#адреса для відправки POST-запитів
adr="http://glob-control.com/"+rpi_id+".html"
while True:
    time.sleep(3)
#якщо каталог з архівними записами не пустий
    list_=os.listdir('/media/usb/archive/')
    if len(list_) != 0:
  #відкрити перший архівний файл
        archtxt='/media/usb/archive/'+list_[0]
        logging.info("file is reading: " +list_[0])
        with open(archtxt, 'r') as f:
            #зчитати перший архівний файл
            l=f.readlines()
            ln = len(l)
  #парсити перший архівний файл
            if ln>3:
                rid = l[0]
                rid = re.sub("^\s+|\n|\r|\s+$", '', rid)
                logging.info("rpi_id: " +rid)
                ti = l[1]
                ti = re.sub("^\s+|\n|\r|\s+$", '', ti)
                logging.info("time: " +ti)
                la = l[2]
                la = re.sub("^\s+|\n|\r|\s+$", '', la)
                logging.info("latitude: " +la)
                lo = l[3]
                lo = re.sub("^\s+|\n|\r|\s+$", '', lo)
                logging.info("longitude: " +lo)
                photo_counter = l[4]
                photo_counter = re.sub("^\s+|\n|\r|\s+$", '', photo_counter)
                logging.info("photo_counter: " +photo_counter)
                foln = l[5]
                foln = re.sub("^\s+|\n|\r|\s+$", '', foln)
                logging.info("foulder name: " +foln)
                filn = l[6]
                filn = re.sub("^\s+|\n|\r|\s+$", '', filn)
                logging.info("filename: " +filn)
            #формувати запит з даними архівного файлу
                payload2 = {'rpi_id': rid, 'time_gps': ti, 'latitude': la, 'longitude': lo, 'photo_counter': photo_counter, 'fold_name': foln, 'file_name': filn}
                logging.debug("POST data: " +str(payload2))
        #надіслати POST з архівними даними
                try:
                    r2 = requests.post(adr, timeout=10, data=payload2)

                  #видалити перший архівний файл, якщо надіслано
                    os.remove(archtxt)
                    logging.info("file: was removed " +list_[0])
                except requests.exceptions.RequestException as e:
                    b = e
            else:
                rid=rpi_id
                logging.info("rpi_id: " +rid)
                system_unix=calendar.timegm(time.gmtime())
                ti=str(system_unix)
                logging.info("time: " +ti)
                filn=list_[0]
                logging.info("filename: " +filn)
                now=datetime.datetime.now().strftime('%Y-%m-%d')
                foln=rpi_id+'_'+now
                logging.info("foldername: " +foln)
                payload3 = {'rpi_id': rid, 'time_gps': ti, 'latitude': '0.0', 'longitude': '0.0', 'photo_counter': ' ', 'fold_name': foln, 'file_name': filn}
                logging.debug("POST data: " +str(payload3))
            #надіслати POST з архівними даними
                try:
                    r3 = requests.post(adr, timeout=10, data=payload3)

              #видалити перший архівний файл, якщо надіслано
                    os.remove(archtxt)
                    logging.info("file: was removed " + list_[0])
                except requests.exceptions.RequestException as e:
                    b = e
                if ln>3:
                    os.remove(archtxt)
