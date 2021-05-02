#!/usr/bin/env python3
########################################################################
# Filename    : SteppingMotor.py
# Description : Drive SteppingMotor
# Author      : www.freenove.com
# modification: 2019/12/27
########################################################################
import RPi.GPIO as GPIO
import time
from ADCDevice import *
import math


adc = ADCDevice()
motorPins = (12, 16, 18, 22)    # define pins connected to four phase ABCD of stepper motor
#CCWStep = (0x01,0x02,0x04,0x08) # define power supply order for rotating anticlockwise
CCWStep = (0x01,0x02,0x04,0x08) # define power supply order for rotating anticlockwise 
#CWStep = (0x08,0x04,0x02,0x01)  # define power supply order for rotating clockwise
CWStep = (0x08,0x04,0x02,0x01)  # define power supply order for rotating clockwise
fstep_matrix = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
hstep_matrix = [[1,1,0,0,0,0,0,1],[0,1,1,1,0,0,0,0],[0,0,0,1,1,1,0,0],[0,0,0,0,0,1,1,1]]

def setup():
    global adc
    if(adc.detectI2C(0x4b)):
        adc = ADS7830()
    else :
        print("No I2C adress found")
        exit(-1)
    GPIO.setmode(GPIO.BOARD)       # use PHYSICAL GPIO Numbering
    for pin in motorPins:
        GPIO.setup(pin,GPIO.OUT)

#define tic() toc() function to measure time interval
def TicTocGenerator():
    
    ti = 0
    tf = time.time()
    while True:
        ti = tf
        tf = time.time()
        yield tf-ti
        
TicToc = TicTocGenerator()

def toc(tempBool = True):
    tempTimeInterval = next(TicToc)
    if tempBool:
        print("Elapsed time: %f seconds.\n" %tempTimeInterval)

def tic():
    toc(False)
# as for four phase stepping motor, four steps is a cycle. the function is used to drive the stepping motor clockwise or anticlockwise to take four steps    
def moveOnePeriod(direction):
    ms = 6
    if(ms<3):       # the delay can not be less than 3ms, otherwise it will exceed speed limit of the motor
        ms = 3
    tic()
    GPIO.output(motorPins[0], hstep_matrix[0][0])
    GPIO.output(motorPins[1], hstep_matrix[1][0])
    GPIO.output(motorPins[2], hstep_matrix[2][0])
    GPIO.output(motorPins[3], hstep_matrix[3][0])
    time.sleep(ms*0.001)
    GPIO.output(motorPins[0], hstep_matrix[0][1])
    GPIO.output(motorPins[1], hstep_matrix[1][1])
    GPIO.output(motorPins[2], hstep_matrix[2][1])
    GPIO.output(motorPins[3], hstep_matrix[3][1])
    time.sleep(ms*0.001)
    GPIO.output(motorPins[0], hstep_matrix[0][2])
    GPIO.output(motorPins[1], hstep_matrix[1][2])
    GPIO.output(motorPins[2], hstep_matrix[2][2])
    GPIO.output(motorPins[3], hstep_matrix[3][2])
    time.sleep(ms*0.001)
    GPIO.output(motorPins[0], hstep_matrix[0][3])
    GPIO.output(motorPins[1], hstep_matrix[1][3])
    GPIO.output(motorPins[2], hstep_matrix[2][3])
    GPIO.output(motorPins[3], hstep_matrix[3][3])
    time.sleep(ms*0.001)
    toc()
    #for j in range(0,4,1):      # cycle for power supply order
    #    tic()
    #    GPIO.output(motorPins[0], hstep_matrix[0][j])
    #    GPIO.output(motorPins[1], hstep_matrix[1][j])
    #    GPIO.output(motorPins[2], hstep_matrix[2][j])
    #    GPIO.output(motorPins[3], hstep_matrix[3][j])
    #    toc()
        #for i in range(0,4,1):  # assign to each pin
        #    if (direction == 1):# power supply order clockwise
        #        #print('Clockwise Full Step')
        #        GPIO.output(motorPins[i],((CCWStep[j] == 1<<i)))
        #    else :              # power supply order anticlockwise
        #        #print('CounterClockWise Full Step')
        #        GPIO.output(motorPins[i],((CWStep[j] == 1<<i)))
        if(ms<3):       # the delay can not be less than 3ms, otherwise it will exceed speed limit of the motor
            ms = 3
        time.sleep(ms*0.001)
  
def moveOnePeriod_hstep(direction):
    ms = 6
    for j in range(0,8,1):
        for i in range(0,4,1):
            if (direction == 1):
                #print('Clockwise')
                GPIO.output(motorPins[i], hstep_matrix[i][j])
            else :
                #print('CounterClockWise')
                GPIO.output(motorPins[i], hstep_matrix[i][-j+1])
        ms = motorSpeed()/2.0
        if (ms<3.0):
            ms = 3.0
        time.sleep(ms*0.001)
# continuous rotation function, the parameter steps specifies the rotation cycles, every four steps is a cycle
def moveSteps(direction,mode,steps):
    
    if mode == 'full':
        for i in range(steps):
            moveOnePeriod(direction)
    elif mode == 'half':
        for i in range(steps):
            moveOnePeriod_hstep(direction)
    else :
        print('please enter a valid step mode ''full'' or ''half')
        
# function used to stop motor
def motorStop():
    for i in range(0,4,1):
        GPIO.output(motorPins[i],GPIO.LOW)

def motorSpeed():
        value = adc.analogRead(0)
        
        if value > 0.0:
            ms = 6.0*math.sqrt(value) #6 = minimal step time
            speed = 1000.0/(ms*200.0)*60.0 #200steps motor
            print('millsecond : %.2f value : %d speed(rpm): %.2f' %(ms,value,speed))
        else:
            ms = 6.0
            speed = 1000.0/(ms*200.0)*60.0 #200steps motor
            print('millsecond : %.2f value : %d speed(rpm): %.2f' %(ms,value,speed))
        return ms

def loop():
    motorStop()
    while True:
        #moveSteps(1,'half',motorSpeed(),50) # rotating 360 deg clockwise, a total of 2048 steps in a circle, 512 cycles
        
        moveSteps(1,'full',50)
        time.sleep(5000)
        #moveSteps(0,'full',motorSpeed(),50)  # rotating 360 deg anticlockwise
        #moveSteps(0,'half',50)
        #time.sleep(0.5)
        

def destroy():
    motorStop()
    GPIO.cleanup()             # Release resource

if __name__ == '__main__':     # Program entrance
    print ('Program is starting...')
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        destroy()


