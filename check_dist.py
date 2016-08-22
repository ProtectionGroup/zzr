# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import os 
import datetime
from gps import *
import threading
import pygame
import pygame.camera
import calendar
import logging
from get_id import getserial
import time

pygame.camera.init()
cam = pygame.camera.Camera("/dev/video-cam",(1080,720))

#рівень відладки для логування
LOG_LEVEL=logging.DEBUG

#логи в консоль
logging.basicConfig(format='%(levelname)s[%(asctime)s] %(message)s',level=LOG_LEVEL, datefmt='%m/%d/%Y %I:%M%p')

#встановити режим роботи з GPIO
GPIO.setmode(GPIO.BCM) 
GPIO.setwarnings(False)
GPIO.setup(19, GPIO.OUT)
#пін кнопки початку зйомки
distance_pin1 = 4 

#пін підсвітки камери
led_light1 = 26

rpi_id = getserial()
#логи у файл
logging.basicConfig(filename='/media/usb/logs/'+rpi_id+'_check_dist.log',format='%(levelname)s[%(asctime)s] %(message)s',level=LOG_LEVEL, datefmt='%m/%d/%Y %I:%M%p')

logging.info("id = "+rpi_id)

#останні коректні координати GPS
latitude_last = ''
longitude_last = ''

#адреса для відправки POST-запитів
adr="http://glob-control.com/"+rpi_id+".html"

#встановлення вхыдних/вихідних портів GPIO
GPIO.setup(distance_pin1,GPIO.IN) 
GPIO.setup(led_light1,GPIO.OUT)

#перевірка існування/створення каталогу для архівних записів 
archpath='/media/usb/archive'
if not os.path.exists(archpath):
    os.makedirs(archpath)
    logging.info("created dir: " + archpath)
else:
    logging.info(archpath+" - dir already exist")
#перевірити існування/створити директорію ID
idpath='/media/usb/'+rpi_id
if not os.path.exists(idpath):
    os.makedirs(idpath)
    logging.info("created dir: " + idpath)
else:
    logging.info(idpath+" - dir already exist")
#перевірити існування/створити директорію tmp
tmppath='/media/usb/tmp'
if not os.path.exists(tmppath):
    os.makedirs(tmppath)
    logging.info("created dir: " + tmppath)
else:
    logging.info(tmppath+" - dir already exist")
#функція запису архівних даних, коли немає доступу до Інтернет
def if_err(filename):
    fn=open('/media/usb/archive/'+filename, 'w')
    fn.write(str(rpi_id) + "\n")
    fn.write(str(time_utc) + "\n")
    fn.write(str(latitude) + "\n")
    fn.write(str(longitude) + "\n")
    fn.write(str(photo_counter) + "\n")
    fn.write(ren_f+"\n")
    fn.write(txt+"\n")
    fn.close()
    logging.info("create error file: " +filename)

#fifo_path = "/home/pi/zzr/my_program.fifo"
#def read_pipe():
#  fifo = open(fifo_path, "r")
#  for line in fifo:
#    line = line[0:1]
#  fifo.close()
#  return line


#ініціалізація змінних та функцій для роботи з GPS модулем
gpsd = None
class GpsPoller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        global gpsd #bring it in scope
        gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
        self.current_value = None
        self.running = True #setting the thread running to true

    def run(self):
        global gpsd
        while gpsp.running:
          gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer

if __name__ == '__main__':
    gpsp = GpsPoller()
    gpsp.start()

    status = 0
    #cam.start()
    try:
    #цикл
        while True:
            time.sleep(0.5)

            if GPIO.input(distance_pin1)==1:
                status = 0
       #якщо натиснута кнопка для фото
            if GPIO.input(distance_pin1)==0 and status == 0:
                start = calendar.timegm(time.gmtime())
                GPIO.output(led_light1, True)
               #запустити програму, яка робить фото
                cam.start()
                not_end = True
                n = 0
                while not_end:
                    now = time.strftime("%Y-%m-%d_%H-%M-%S")
                    filename = str(now)
                    img = cam.get_image()
                    time.sleep(1.8)
                    jpname = "/media/usb/tmp/"+filename#+"_"+str(n)
                    pygame.image.save(img, jpname+".jpeg")
                   # n = n + 1
                    next = calendar.timegm(time.gmtime())
                    end = next - start
                    #print end
            #        cam_term = read_pipe()
            #        cam_term = str(cam_term)
                    #print cam_term
                    if end >= 3600:# or cam_term == '2':
                        not_end = False
                    #    cam.stop()
                        status = 1
                  #    cam.start()
                      #print "TIME IS OUT!!!"
                    if (GPIO.input(distance_pin1)==1):
                        not_end = False
                    #    cam.stop()
                        path_check = '/media/usb/tmp'
                        if len(os.listdir(path_check)) == 0:
                            continue
                          #print "TMP IS EMPTY"
                        else:
                            pass
                        #print "TMP IS NOT EMPTY"
                cam.stop()

                  #вимкнути світлодіод підсвітки
                GPIO.output(led_light1, False)
               #парсити дату
                now=datetime.datetime.now().strftime('%Y-%m-%d')
                dayname=rpi_id+'_'+now
                name=datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                #перевірити існування/створити директорію з поточною датою
                daypath='/media/usb/'+rpi_id+'/'+dayname
                if not os.path.exists(daypath):
                    os.makedirs(daypath)
               #отримати список файлів(фото)
                directory = '/media/usb/tmp'
                list_ = os.listdir(directory)
                txtname=daypath+'/'+rpi_id+'_'+name +'.txt'
                with open(txtname, 'w') as f:
                    count=0
                    for index in list_:
                        f.write(index + '\n')
                        in_file = directory+'/'+index
                        out_file = daypath+'/'+index
                        os.rename(in_file, out_file)
                        count+=1
                        photo_counter = count
                        txt=rpi_id+'_'+name+'.txt'
                        #парсити широту і довготу з GPS
                        latitude=str(gpsd.fix.latitude)[0:7]
                        #latitude=latitude[0:7]
                        longitude=str(gpsd.fix.longitude)[0:7]
                        #longitude=longitude[0:7]
                        logging.info("latitude = " + latitude + " longitude = " + longitude)
                       #записати у ren_f поточну дату для відправки POST
                        ren_f=dayname
                       #отримати системний час в UNIX форматі
                        system_unix=calendar.timegm(time.gmtime())
                        time_utc=system_unix
                        logging.debug("get system time: " + str(time_utc))
                   #якщо координати коректні, запам'ятати їх як останні коректні
                        if latitude=='nan' or latitude=='0.0':
                            latitude=latitude_last
                        if longitude=='0.0' or longitude=='nan':
                            longitude=longitude_last
                        #зберегти дані
                        if_err(txt)
      #    cam.stop()
    except KeyboardInterrupt:
        GPIO.cleanup()
        gpsp.running = False
        gpsp.join() # wait for the thread to finish what it's doing
