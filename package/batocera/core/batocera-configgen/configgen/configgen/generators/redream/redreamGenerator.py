#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
from shutil import copyfile
import os
import batoceraFiles
import filecmp
import codecs
from utils.logger import get_logger

eslog = get_logger(__name__)

redream_file = "/usr/bin/redream"
redreamConfig = batoceraFiles.CONF + "/redream"

class RedreamGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        redream_exec = redreamConfig + "/redream"

        if not os.path.exists(redreamConfig):
            os.makedirs(redreamConfig)

        if not os.path.exists(redream_exec) or not filecmp.cmp(redream_file, redream_exec):
            copyfile(redream_file, redream_exec)
            os.chmod(redream_exec, 0o0775)
        
        configFileName = redreamConfig + "/redream.cfg"
        f = codecs.open(configFileName, "w")
        # set the roms path
        f.write("gamedir=/userdata/roms/dreamcast\n")
        # force fullscreen
        f.write("mode=borderless fullscreen\n")
        f.write("fullmode=borderless fullscreen\n")
        
        # configure controller
        # examples:
        # port - port0=dev:4,desc:03000000c82d00000660000011010000,type:controller
        # ctrl - profile0=name:03000000c82d00000660000011010000,type:controller,deadzone:12,crosshair:1,a:joy1,b:joy0,x:joy4,y:joy3,start:joy11,dpad_up:hat0,dpad_down:hat1,dpad_left:hat2,dpad_right:hat3,ljoy_up:-axis1,ljoy_down:+axis1,ljoy_left:-axis0,ljoy_right:+axis0,ltrig:axis2,rtrig:axis3,turbo:joy10,turbo:f6,menu:escape,lcd:f5,screenshot:f12,exit:joy12
        
        ButtonMap = {
            "a":      "b",
            "b":      "a",
            "x":      "y",
            "y":      "x",
            "start":  "start",
            "select": "turbo",
            #hotkey = exit (redream doesn't accecpt button combo's)
            "hotkey": "exit"
        }

        HatMap = {
            "up":    0,
            "down":  1,
            "left":  2,
            "right": 3
        }

        AxisMap = {
            "joystick1left": 0,
            "joystick1up":   1,
            # use input.id for l2/r2
            "l2":            2,
            "r2":            3
        }

        nplayer = 1
        for index in playersControllers:
            controller = playersControllers[index]
            if nplayer <= 4:
                # dev = ? seems to be 4+
                ctrlport = "port{}=dev:{},desc:{},type:controller".format(controller.index, 4 + controller.index, controller.guid)
                f.write((ctrlport)+ "\n")
                
                ctrlprofile = "profile{}=name:{},type:controller,deadzone:12,crosshair:1".format(controller.index, controller.guid)
                fullprofile = ctrlprofile
                
                eslog.debug("CONTROLLER: {} - {}".format(controller.index, controller.guid))
                
                for index in controller.inputs:
                    input = controller.inputs[index]
                    eslog.debug("Name: {}, Type: {}, ID: {}, Code: {}".format(input.name, input.type, input.id, input.code))
                    
                    # [buttons]
                    if input.type == "button" and input.name in ButtonMap:
                        buttonname = ButtonMap[input.name]
                        fullprofile = fullprofile + ","
                        fullprofile = fullprofile + "{}:joy{}".format(buttonname, input.id)
                    #on rare occassions when triggers are buttons
                    if input.type == "button" and input.name == "l2":
                        fullprofile = fullprofile + ","
                        fullprofile = fullprofile + "ltrig:joy{}".format(input.id)
                    if input.type == "button" and input.name == "r2":
                        fullprofile = fullprofile + ","
                        fullprofile = fullprofile + "rtrig:joy{}".format(input.id)
                    #on occassions when dpad directions are buttons
                    if input.type == "button":
                        if input.name == "up" or input.name == "down" or input.name == "left" or input.name == "right":
                            fullprofile = fullprofile + ","
                            fullprofile = fullprofile + "dpad_{}:joy{}".format(input.name, input.id)
                    
                    # [hats]
                    if input.type == "hat" and input.name in HatMap:
                        hatid = HatMap[input.name]
                        fullprofile = fullprofile + ","
                        fullprofile = fullprofile + "dpad_{}:hat{}".format(input.name, hatid)
                    
                    # [axis]
                    if input.type == "axis" and input.name in AxisMap:
                        axisid = AxisMap[input.name]
                        #l2/r2 as axis triggers
                        if input.name == "l2":
                            fullprofile = fullprofile + ","
                            fullprofile = fullprofile + "ltrig:+axis{}".format(input.id)
                        if input.name == "r2":
                            fullprofile = fullprofile + ","
                            fullprofile = fullprofile + "rtrig:+axis{}".format(input.id)
                        #handle axis l,r,u,d
                        if input.name == "joystick1left":
                            fullprofile = fullprofile + ","
                            fullprofile = fullprofile + "ljoy_left:-axis{}".format(axisid)
                            fullprofile = fullprofile + ","
                            fullprofile = fullprofile + "ljoy_right:+axis{}".format(axisid)
                        if input.name == "joystick1up":
                            fullprofile = fullprofile + ","
                            fullprofile = fullprofile + "ljoy_up:-axis{}".format(axisid)
                            fullprofile = fullprofile + ","
                            fullprofile = fullprofile + "ljoy_down:+axis{}".format(axisid)
                    
                f.write((fullprofile)+ "\n")
                nplayer = nplayer + 1
        
        # change settings as per users options
        # [video]
        f.write("width={}\n".format(gameResolution["width"]))
        f.write("height={}\n".format(gameResolution["height"]))
        f.write("fullwidth={}\n".format(gameResolution["width"]))
        f.write("fullheight={}\n".format(gameResolution["height"]))
        if system.isOptSet("redreamResolution"):
            f.write("res={}".format(system.config["redreamResolution"]) + "\n")
        else:
            f.write("res=2\n")
        if system.isOptSet("redreamRatio"):
            f.write("aspect={}".format(system.config["redreamRatio"]) + "\n")
        else:
            f.write("aspect=4:3\n")
        if system.isOptSet("redreamFrameSkip"):
            f.write("frameskip={}".format(system.config["redreamFrameSkip"]) + "\n")
        else:
            f.write("frameskip=0\n")
        if system.isOptSet("redreamVsync"):
            f.write("vysnc={}".format(system.config["redreamVsync"]) + "\n")
        else:
            f.write("vsync=0\n")
        if system.isOptSet("redreamPolygon"):
            f.write("autosort={}".format(system.config["redreamPolygon"]) + "\n")
        else:
            f.write("autosort=0\n")
        # [system]
        if system.isOptSet("redreamRegion"):
            f.write("region={}".format(system.config["redreamRegion"]) + "\n")
        else:
            f.write("region=usa\n")
        if system.isOptSet("redreamLanguage"):
            f.write("language={}".format(system.config["redreamLanguage"]) + "\n")
        else:
            f.write("language=english\n")
        if system.isOptSet("redreamBroadcast"):
            f.write("broadcast={}".format(system.config["redreamBroadcast"]) + "\n")
        else:
            f.write("broadcast=ntsc\n")
        if system.isOptSet("redreamCable"):
            f.write("cable={}".format(system.config["redreamCable"]) + "\n")
        else:
            f.write("cable=vga\n")
        
        f.write
        f.close()

        commandArray = [redream_exec, rom]
        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers),
                'SDL_JOYSTICK_HIDAPI': '0'
            })
