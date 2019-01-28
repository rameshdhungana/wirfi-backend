#!/usr/bin/env python
from subprocess import call
from subprocess import check_output
from time import sleep

#enable the module for PWM
#seems to be fine calling this every time
call(["insmod", "gpio-pwm-ar9331"])

#fails if not connected....
#seems to work now.
#is python cool with a function definition in the middle like this?
def getSignalStrengthPercent():
     try:
          output = check_output(["iwinfo", "wlan0", "info"])
          sigLoc = output.find("Signal: ")
          dbmString = output[sigLoc+8:sigLoc+11]
          dbm = int(dbmString)
          print dbm
          returnVal = 2 * (dbm + 100)
          if (dbm <= -100):
               returnVal = 0
          if (dbm >= -50):
               returnVal = 100
          print returnVal
          return returnVal
     except:
          return 0 

#enable GPIO 18? This is the one that controls the color
#No, the PWM command takes care of it.
#value = open("/sys/class/gpio/export","w")
#value.write(str(18))
#value.close()

#value = open("/sys/class/gpio/gpio18/direction","w")
#value.write("out")
#value.close()

#enable GPIO19. This is output on/off (ie. brightness)
try:
     value = open("/sys/class/gpio/export","w")
     value.write(str(19))
     value.close()
except:
     print "failed to export GPIO, already exists?"

try:
     value = open("/sys/class/gpio/gpio19/direction","w")
     value.write("out")
     value.close()
except:
     print "failed to set GPIO 19 direction"

#try:
ledOn = open("/sys/class/gpio/gpio19/value","w")
ledOn.write("1")
ledOn.flush()
#     value.close()
#except:
#     print "failed to set GPIO 19 value"


#call(["/sys/class/gpio/echo 18 > export"})
#/sys/class/gpio/gpio18/echo "out" > direction
#/sys/class/gpio/

#set PWM paramters
channel = 0
gpio = 18
frequency = 10000
dutyCycle = 50.0
dir = 1
value = open("/sys/kernel/debug/pwm-ar9331","w")
while 1 :
#	dutyCycle += (10 * dir)
#	if dutyCycle >= 100.0 :
#		#dutyCycle = 0.1
#		dir = dir * -1
#		dutyCycle += (10 * dir)
#	if dutyCycle <= 0.0 :
#	     dir = dir * -1
#	     dutyCycle += (10 * dir)
	#value = open("/sys/kernel/debug/pwm-ar9331","w")
	#ledOn.write("0")
	#ledOn.flush()
	outputVal = "+ " + str(channel) + " " + str(gpio) + " " + str(frequency) + " " + str(int(float(getSignalStrengthPercent()) / 100 * 65535)) + "\n"
	print outputVal
	value.write(outputVal)
	value.flush()
	#sleep(0.05)
	#ledOn.write("1")
	#ledOn.flush()
	#print(outputVal, file
	sleep(0.5)
#echo "+ 0 18 10000 30000" > pwm-ar9331
