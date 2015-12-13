#!/usr/bin/env python
from evdev import InputDevice, categorize, ecodes, KeyEvent

def start_controller():

    event0 = InputDevice('/dev/input/event0')
    event1 = InputDevice('/dev/input/event1')
    event2 = InputDevice('/dev/input/event2')
    event3 = InputDevice('/dev/input/event3')
    
    controller_name = "Logitech Gamepad F310"
    if event0.name == controller_name:
        gamepad = event0
    elif event1.name == controller_name:
        gamepad = event1
    elif event2.name == controller_name:
        gamepad = event2
    elif event3.name == controller_name:
        gamepad = event3
    else:
        print("controller not found")

    return gamepad
