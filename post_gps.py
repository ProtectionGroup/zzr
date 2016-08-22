# -*- coding: utf-8 -*-
import os
from gps import *
import time
import threading
import requests
import re
import datetime
import RPi.GPIO as GPIO
import calendar
import logging
from get_id import getserial

import commands
#перевірити/створити папку для логів
logpath='/media/usb/logs'
if not os.path.exists(logpath):
    os.makedirs(logpath)
#  logging.info(logpath+" - dir already exist")
#  logging.info("created dir: "+logpath)



#рівень відладки для логування
LOG_LEVEL=logging.DEBUG

#логи в консоль
logging.basicConfig(format='%(levelname)s[%(asctime)s] %(message)s',level=LOG_LEVEL, datefmt='%m/%d/%Y %I:%M%p')

#логи у файл
#logging.basicConfig(filename='/media/usb/logs/post_gps.log',format='%(levelname)s[%(asctime)s] %(message)s',level=LOG_LEVEL, datefmt='%m/%d/%Y %I:%M%p')

#встановити режим роботи з GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#GPS LED
gpsPin = 6
#####gsmPin = 13
#GPS LED as OUT
GPIO.setup(gpsPin, GPIO.OUT)
#####GPIO.setup(gsmPin, GPIO.OUT)

rpi_id = getserial()

#адреса для відправки POST-запитів
adr="http://glob-control.com/"+rpi_id+".html"

#перевірка існування/створення каталогу для архівних записів
archpath='/media/usb/archive_gps'
if not os.path.exists(archpath):
    os.makedirs(archpath)
    logging.info("created dir: " + archpath)
else:
    logging.info(archpath+" - dir already exist")

#функція запису архівних даних, коли немає доступу до Інтернет
def if_err(filename):
  fn=open('/media/usb/archive_gps/'+filename, 'w')
  fn.write(str(rpi_id) + "\n")
  fn.write(str(time_utc) + "\n")
  fn.write(str(latitude) + "\n")
  fn.write(str(longitude) + "\n")
  fn.write("\n")
  fn.write("\n")
  fn.write("\n")
  fn.close()
  logging.info("create error file: " +filename)

#ініціалізація змінних та функцій для роботи з GPS модулем
gpsd = None
class GpsPoller(threading.Thread):
  def __init__(self):
      threading.Thread.__init__(self)
      global gpsd #bring it in scope
      gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
      self.current_value = None
      self.running = True #setting the thread running to true
#
  def run(self):
      global gpsd
      while gpsp.running:
          gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer

if __name__ == '__main__':
  gpsp = GpsPoller() # create the thread
  try:
      gpsp.start()

#цикл
      while True:
          time.sleep(2)

      #парсити дату
          now=datetime.datetime.now().strftime('%Y-%m-%d')
          dayname=rpi_id+'_'+now
          name=datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
          logging.info("getting date: "+ str(name))

      #назва для текстового файлу
          txt=rpi_id+'_'+name+'.txt'
          logging.info("getting file-txt name: "+ txt)

      #парсити широту, довготу
          latitude=str(gpsd.fix.latitude)
          latitude=latitude[0:7]
          logging.info("latitude: " +str(latitude))
#      print "-----------"
#      print str(gpsd.fix.latitude)
          longitude=str(gpsd.fix.longitude)
          longitude=longitude[0:7]
          logging.info("longitude: " +str(longitude))
#      print str(gpsd.fix.longitude)
      #системний час
          system_unix=calendar.timegm(time.gmtime())
          time_utc=system_unix
          logging.info("time: " +str(time_utc))

   #отримати кількість файлів(фото)

          photo_dir = '/media/usb/tmp'
          list = os.listdir(photo_dir)
          count=0
          for index in list:
              count+=1
          photo_limit = count
      #print photo_limit


          if latitude!='0.0' and latitude!='nan' and longitude!='0.0' and longitude!='nan':
        #засвітити світлодіодний індикатор
              GPIO.output(gpsPin, False)
              logging.info("LED on")
       #формувати GET-запит
              payload = {'rpi_id': rpi_id, 'time_gps': time_utc, 'latitude': latitude, 'longitude': longitude, 'photo_limit': photo_limit, 'fold_name': ' ', 'file_name': ' '}
              logging.debug("GET: " +str(payload))
              try:
          #надіслати запит
                  r = requests.get(adr, timeout=3, params=payload)
              except requests.exceptions.RequestException as e:
                  b = e
                  if_err(txt)
                  time.sleep(4)
                  continue
      #якщо координати некоректні, погасити світлодіодний індикатор
          if latitude=='0.0' or latitude=='nan' or longitude=='0.0' or longitude=='nan':
              GPIO.output(gpsPin, True)
              logging.info("LED off")
      #якщо каталог з архівними записами не пустий
          list_=os.listdir('/media/usb/archive_gps/')
          if list_ != []:
        #відкрити перший архівний файл
              archtxt='/media/usb/archive_gps/'+list_[0]
              f=open(archtxt, 'r')
        #зчитати перший архівний файл
              l=f.readlines()
              ln = len(l)
              f.close()
        #парсити перший архівний файл
              if ln>3:
                  rid = l[0]
                  rid = re.sub("^\s+|\n|\r|\s+$", '', rid)
                  ti = l[1]
                  ti = re.sub("^\s+|\n|\r|\s+$", '', ti)
                  la = l[2]
                  la = re.sub("^\s+|\n|\r|\s+$", '', la)
                  lo = l[3]
                  lo = re.sub("^\s+|\n|\r|\s+$", '', lo)
                  sp = l[4]
                  sp = re.sub("^\s+|\n|\r|\s+$", '', sp)
                  foln = l[5]
                  foln = re.sub("^\s+|\n|\r|\s+$", '', foln)
                  filn = l[6]
                  filn = re.sub("^\s+|\n|\r|\s+$", '', filn)

          #формувати запит з даними архівного файлу
                  payload2 = {'rpi_id': rid, 'time_gps': ti, 'latitude': la, 'longitude': lo, 'photo_limit': photo_limit, 'fold_name': foln, 'file_name': filn}
                  logging.debug("GET: " +str(payload2))
          #надіслати POST з архівними даними
                  try:
                    r2 = requests.get(adr, timeout=10, params=payload2)

                        #видалити перший архівний файл, якщо надіслано
                    os.remove(archtxt)

                  except requests.exceptions.RequestException as e:
                    a = e
                    continue
              else:
                  os.remove(archtxt)

  except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    gpsp.running = False
    gpsp.join() # wait for the thread to finish what it's doing
