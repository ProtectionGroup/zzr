import RPi.GPIO as GPIO
import os
import urllib2
import commands
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
gsmPin = 13
count = 0

def internet_on(ip_adress):
    try:
          response=urllib2.urlopen(ip_adress,timeout=5)
          return True
    except urllib2.URLError as err:
          pass
    return False

while True:
    try:
        google_ip = 'http://google.com.ua/'
        if internet_on(google_ip) == 1:
            GPIO.setup(gsmPin, GPIO.LOW)
            count = 0
                #    print "ON-line"
        else:
            output = commands.getoutput('ps -A')
            GPIO.setup(gsmPin, GPIO.HIGH)
            #    print "OFF-line"
            if 'pppd' not in output:
                mod_com2="sudo pppd call zzr-internet &"
                os.system(mod_com2)
            #      print "CONNECTING..."
            count += 1
            #    print count
            mod_path='/dev/ttyUSB0'
            if not os.path.exists(mod_path):
                mod_com1 = "sudo /usr/sbin/usb_modeswitch -W -I -v 12d1 -p 15ca -M 55534243123456780000000000000011062000000101000100000000000000 > /dev/null &"
                os.system(mod_com1)
            if count >= 300:
                os.system('sudo killall pppd')
                count = 0
        #      print "RESET COUNTER"
            time.sleep(1)
    except:
        continue
