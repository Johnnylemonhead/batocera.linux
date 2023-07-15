#!/usr/bin/env python

import sys
import os

def writeCfgFile(filename, init_line, defaults_to_add, controls_to_add, gameResolution):
    if not os.path.isfile(filename):
        with open(filename, 'w') as file:
            file.write(init_line)
            for line in defaults_to_add:
                file.write(line)
            for line in controls_to_add:
                file.write(line)
    else:
        with open(filename, 'r+') as file:
            lines = file.readlines()
            file.seek(0)
            for line in lines:
                ## Set defaults every time
                # resolution
                if line.startswith('seta r_mode'):
                    line = 'seta r_mode "-1"\n'
                elif line.startswith('seta r_customwidth'):
                    line = f'seta r_customwidth "{gameResolution["width"]}"\n'
                elif line.startswith('seta r_customheight'):
                    line = f'seta r_customheight "{gameResolution["height"]}"\n'
                # controllers
                elif line.startswith('seta in_joystickUseAnalog'):
                    line = 'seta in_joystickUseAnalog "1"\n'
                elif line.startswith('seta in_joystick'):
                    line = 'seta in_joystick "1"\n'

                file.write(line)

            # Add the missing lines at the end of the file
            for line in defaults_to_add:
                if line not in lines:
                    file.write(line)
            for line in controls_to_add:
                if line not in lines:
                    file.write(line)

def writeCfgFiles(system, rom, playersControllers, gameResolution):
    # changes should align to quake3 arena & team fortress
    files = [
        "/userdata/system/configs/ioquake3/baseq3/q3config.cfg",
        "/userdata/system/configs/ioquake3/missionpack/q3config.cfg"
    ]

    init_line = '// generated by quake, do not modify\n'
    # minimum defaults
    defaults_to_add = [
        'seta r_mode "-1"\n',
        f'seta r_customwidth "{gameResolution["width"]}"\n',
        f'seta r_customheight "{gameResolution["height"]}"\n',
        'seta in_joystickUseAnalog "1"\n',
        'seta in_joystick "1"\n'
    ]

    # basic controller config
    controls_to_add = [
        'bind PAD0_A "+moveup"\n',
        'bind PAD0_X "+movedown"\n',
        'bind PAD0_Y "+button2"\n',
        'bind PAD0_LEFTSHOULDER "weapnext"\n',
        'bind PAD0_RIGHTSHOULDER "weapprev"\n',
        'bind PAD0_LEFTSTICK_LEFT "+moveleft"\n',
        'bind PAD0_LEFTSTICK_RIGHT "+moveright"\n',
        'bind PAD0_LEFTSTICK_UP "+forward"\n',
        'bind PAD0_LEFTSTICK_DOWN "+back"\n',
        'bind PAD0_RIGHTSTICK_LEFT "+left"\n',
        'bind PAD0_RIGHTSTICK_RIGHT "+right"\n',
        'bind PAD0_RIGHTSTICK_UP "+lookup"\n',
        'bind PAD0_RIGHTSTICK_DOWN "+lookdown"\n',
        'bind PAD0_LEFTTRIGGER "+speed"\n',
        'bind PAD0_RIGHTTRIGGER "+attack"\n'
    ]
    
    for filename in files:
        writeCfgFile(filename, init_line, defaults_to_add, controls_to_add, gameResolution)
