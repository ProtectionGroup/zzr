import commands
import os
from get_id import getserial

rpi_id = getserial()
output = commands.getoutput('ps -A')

if 'wput'not in output:  
#    comftp="sudo /usr/bin/ncftpput -t 10 -DD -R -d /media/usb/logs/ncftp.log -u zzr_api -p or-za.com7711 5.58.15.83 / /media/usb/"+rpi_id+" > /dev/null &"
    comftp="cd /media/usb/ && wput -B -u -R -a /media/usb/logs/wput.log "+rpi_id+" ftp://zzr_api:or-za.com7711@5.58.15.83"
    os.system(comftp)
