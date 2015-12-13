#!/usr/bin/env python

#CONTROLLER TEST

'''

THE READING IN OF SERVO POSITION IS INSANLY SLOW!
I don't know how to fix it but it does need to be fixed.

IF someone gets it working it means that we have a lot more options
available to do even more cool stuff. : )

'''

from emuBot import *
from controller import *
import time

# for camera
import picamera
import os
import subprocess

#initialise emuBot ... functions in emuBot.py

#Wheels are 1,2,3,4
wheelMode(1) 
wheelMode(2)
wheelMode(3)
wheelMode(4)

#Joints are 5,6,7, 8
jointMode(5) #Limit 200 to 800 (512 is middle)
jointMode(6) #Limit 50 to 970 (650 if ID:5 is 200)
jointMode(7) #Limit 200 to 800

# Gun trigger
#wheelMode(8) 


#start controller ... functions in controller.py
gamepad = start_controller()

slowed = False

# servos:[position, min, max, moving]
poses = {1:[0, 0, 0, False], 2:[0, 0, 0, False], 3:[0, 0, 0, False], 4:[0, 0, 0, False], 5:[201, 200, 950, False], 6:[51, 50, 970, False], 7:[512, 200, 800, False], 8:[530, 0, 1023, False]}
# servos:[default position]
defaultPos = {1:[0], 2:[0], 3:[0], 4:[0], 5:[201], 6:[51], 7:[512], 8:[530]}

# Camera settings (not all are necessary)
camera = picamera.PiCamera()
camera.preview_fullscreen = False
camera.preview_window = (600, 320, 640, 480)
camera.resolution = (640, 480)

camera.sharpness = 10
camera.contrast = 30
camera.vflip = True
camera.hflip = True
camera.exposure_mode = "auto"
camera.brightness = 60

def startCamera():
    print("Camera started")
    camera.start_preview()
    
    '''
    fps = 5
    clientIP = "192.168.100.117"
    port = 5000
    height = 360
    width = 640
    time = 0
    start_command = "/opt/vc/bin/raspivid -vf -fps %s -o - -w %s -h %s -t %s | nc.traditional %s %s" % (fps, width, height, time, clientIP, port)
    subprocess.call(start_command, shell = True)'''

def stopCamera():
    camera.stop_preview()
    camera.close()
    print("Camera stopped")
    
    '''
    os.system("killall -9 raspivid")
    os.system("killall -9 netcat")'''

def start_pos():
    ready = True
    print("Moving to start positions...")
    for i in range(5, 8):
        moveJoint(i, defaultPos[i][0], 100)
        '''# checking if Emubot is ready
        if readDxl(i, "j") != defaultPos[i][0]:
            ready = False
        else:
            ready = True

    if ready == True:
        print("EmuBot ready...")
    else:
        print("not ready")'''
        
    print("EmuBot ready...")

start_pos()

def stop(ID):
    print("stopping servo")
    #moveJoint(ID, 512, 0)
    # setting joint to speed: 0, results in it going at its maximum speed

def gunSetup():
    jointMode(8)
    moveJoint(8, 512, 150)
    delay(1.5)
    wheelMode(8)
gunSetup()

def fireGun():
    gunSetup()
    
    moveWheel(8, 201)
    delay(8)
    stopGun()

def reloadGun():
    moveWheel(8, -201)
    delay(8)
    
    stopGun()
    
    gunSetup()

def stopGun():
    moveWheel(8, 0)

def changePos(ID, incriment, speed):
    maxx = poses[ID][2]
    minn = poses[ID][1]
    poses[ID][0] = int(poses[ID][0]) + incriment

    # checking for min/max ranges
    if poses[ID][0] < minn:
        poses[ID][0] = minn
        
    elif poses[ID][0] > maxx:
        poses[ID][0] = maxx

    # moving servo
    moveJoint(ID, poses[ID][0], speed)

def continueMovingToPos(ID, speed, started):
    poses[ID][3] = started
    if poses[ID][3] == True:
        changePos(ID, 2, 25)

def move(speed, direction, slowed):
    if speed > 1000:
        speed = 1000
    if slowed == True:
        speed = speed/2
    if speed > 200:
        if direction == 'forward' or direction == 'back':
            if direction == 'back':
                speed = -speed
            moveWheel(1, speed)
            moveWheel(2, -speed)
            moveWheel(3, -speed)
            moveWheel(4, speed)
        else:
            if direction == 'left':
                speed = -speed
            for i in range(1, 5):
                moveWheel(i, speed)
    else:
        for i in range(1, 5):
                moveWheel(i, speed)

def leftTurn(speed):
    moveWheel(2, speed)
    moveWheel(3, speed)

def rightTurn(speed):
    moveWheel(1, speed)
    moveWheel(4, speed)

for event in gamepad.read_loop():
    # ---------- TRIGGERS ----------
    # ----- Right Trigger -----
    if event.code == 5:
        leftTurn(-((event.value*1000)/255))
    
    # ----- Left Trigger -----
    elif event.code == 2:
        rightTurn(((event.value*1000)/255))

    # ---------- BUMPERS ----------
    if event.type == ecodes.EV_KEY:
        keyevent = categorize(event)
        if keyevent.keystate == KeyEvent.key_down:
            if event.code == 311:
                leftTurn(1000)
            elif event.code == 310:
                rightTurn(-1000)
        else:
            if event.code == 311:
                leftTurn(0)
            elif event.code == 310:
                rightTurn(0) 
          
    # ---------- THUMBSTICKS ----------
    # ----- Right Stick ----- Up/Down
    if event.code == 4:
        if event.value > 1000:
            move((event.value/30), 'back', slowed)
        if event.value < -1000:
            move((-event.value/30), 'forward', slowed)

    # ----- Right Stick ----- Left/Right
    elif event.code == 3:
        if event.value > 1000:
            move((event.value/30), 'right', slowed)
        if event.value < -1000:
            move((-event.value/30), 'left', slowed)

    # ----- Left Stick -----
    '''elif event.code == 1:
    # check out event.code == 0        
        # --- Move the camera ---
        if event.value < 10000 and event.value > 500:
            #Camera Left
            moveJoint(7, 700, 100)
            
        elif event.value < -500 and event.value > -10000:
            #Camera Right
            moveJoint(7, 200, 100)
            
        elif event.value > -500 and event.value < 500:
            #Camera Centre
            moveJoint(7,512,100)
            
        # --- Tilt the camera ---
        elif event.value > 10000:
            moveJoint(7, 650, 100)
        elif event.value < -10000:
            moveJoint(7, 200, 100)
        elif event.value < 10000 and event.value > -10000:
            moveJoint(7, 512, 100)'''

    # ---------- BUTTONS ----------
    
    if event.type == ecodes.EV_KEY:
        keyevent = categorize(event)
        if keyevent.keystate == KeyEvent.key_down:
            print(keyevent.keycode)
            # --- Servo 5 ---
            if keyevent.keycode == "BTN_Y": # up
                changePos(5, 5, 25)
            elif keyevent.keycode[0] == "BTN_A": # down
                changePos(5, -5, 25)

            # --- Servo 8 ---
            if keyevent.keycode == "BTN_X": # up
                fireGun()
            elif keyevent.keycode == "BTN_B": # down
                reloadGun()

            # --- Home button ---
            if keyevent.keycode == "BTN_MODE": # logitech button
                start_pos()
                gunSetup()

            # --- camera ---
            if keyevent.keycode == "BTN_START": # start button
                try:
                    startCamera()
                except:
                    print("Camera couldn't start")
            elif keyevent.keycode == "BTN_SELECT": # back button
                try:
                    stopCamera()
                except:
                    print("Camera couldn't stop")
                    
        elif keyevent.keystate == KeyEvent.key_up:
            # --- Servo 5 ---
            if keyevent.keycode == "BTN_Y": # up
                changePos(5, 5, 25)
            if keyevent.keycode[0] == "BTN_A": # down
                changePos(5, -5, 25)

            # --- Servo 8 ---
            '''if keyevent.keycode == "BTN_X": # up
                changePos(8, 8, 25)
            if keyevent.keycode == "BTN_B": # down
                changePos(8, -8, 25)'''
                
    # ----- Arrows -----
    if event.code == 17:
        # --- Down ---
        if event.value == 1:
            changePos(6, 15, 25)

        # --- Up ---
        elif event.value == -1:
            changePos(6, -15, 25)
    
    if event.code == 16:
        # --- Right ---
        if event.value == 1:
            changePos(7, -15, 25)

        # --- Left ---
        elif event.value == -1:
            changePos(7, 15, 25)

    # ----- Back Button -----
    '''
    if event.code == 314:
        start_pos()
    '''



'''
How to deal with buttons when reading position is faster:

if blah blah blah
    moveJoint(ID, readDxl(ID, "j") + 15, 100)
'''



