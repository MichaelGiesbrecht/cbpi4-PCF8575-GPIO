
# -*- coding: utf-8 -*-
import os
from aiohttp import web
import logging
from unittest.mock import MagicMock, patch
import asyncio
import random
from smbus2 import SMBus
import math
from cbpi.api import *
from cbpi.api.config import ConfigType
from cbpi.api.dataclasses import Props
from cbpi.api.base import CBPiBase

logger = logging.getLogger(__name__)

# creates the PCF_IO object only during startup. All sensors are using the same object
def PCFActor(address):
    global p1
    pins=["p0","p1","p2","p3","p4","p5","p6","p7","p8","p9","p10","p11","p12","p13","p14","p15"]
    logger.info("***************** Start PCF Actor on I2C address {} ************************".format(hex(address)))
    try:
        # create to object with the defined address
        p1 = PCF(address)
        # All pins are set to input at start -> set them to output and low
        for pin in pins:
            p1.pin_mode(pin,"OUTPUT")
            p1.write(pin, "LOW")

        pass
    except:
        p1 = None
        logging.info("Error. Could not activate PCF8575 on I2C address {}".format(address))
        pass


# check if PCF address parameter is included in settings. Add it to settings if it not already included.
# call PCFActor function once at startup to create the PCF Actor object
class PCF8575(CBPiExtension):

    def __init__(self,cbpi):
        self.cbpi = cbpi
        self._task = asyncio.create_task(self.init_actor())

    async def init_actor(self):
        await self.PCF8575_Address()
        logger.info("Checked PCF Address")
        PCF8575_Address = self.cbpi.config.get("PCF8575_Address", "0x20")
        address=int(PCF8575_Address,16)
        PCFActor(address)

    async def PCF8575_Address(self): 
        global PCF8575_address
        plugin = await self.cbpi.plugin.load_plugin_list("cbpi4-PCF8575-GPIO")
        self.version=plugin[0].get("Version","0.0.0")
        self.name=plugin[0].get("Name","cbpi4-PCF8575-GPIO")

        self.PCF8575_update = self.cbpi.config.get(self.name+"_update", None)


        PCF8575_Address = self.cbpi.config.get("PCF8575_Address", None)
        if PCF8575_Address is None:
            logger.info("INIT PCF8575_Address")
            try:
                await self.cbpi.config.add('PCF8575_Address', '0x20', type=ConfigType.STRING, 
                                           description='PCF8575 I2C Bus address (e.g. 0x20). Change requires reboot',
                                           source=self.name)
                PCF8575_Address = self.cbpi.config.get("PCF8575_Address", None)
            except Exception as e:
                    logger.warning('Unable to update config')
                    logger.warning(e)
        else:
            if self.PCF8575_update == None or self.PCF8575_update != self.version:
                try:
                    await self.cbpi.config.add('PCF8575_Address', PCF8575_Address, type=ConfigType.STRING, 
                                           description='PCF8575 I2C Bus address (e.g. 0x20). Change requires reboot',
                                           source=self.name)
                except Exception as e:
                    logger.warning('Unable to update config')
                    logger.warning(e)
                    
        if self.PCF8575_update == None or self.PCF8575_update != self.version:
            try:
                await self.cbpi.config.add(self.name+"_update", self.version, type=ConfigType.STRING,
                                           description="PCF8575 Plugin Version",
                                           source='hidden')
            except Exception as e:
                logger.warning('Unable to update config')
                logger.warning(e)
            pass                

@parameters([Property.Select(label="GPIO", options=["p0","p1","p2","p3","p4","p5","p6","p7","p8","p9","p10","p11","p12","p13","p14","p15"]),
             Property.Select(label="Inverted", options=["Yes", "No"],description="No: Active on high; Yes: Active on low"),
             Property.Select(label="SamplingTime", options=[2,5],description="Time in seconds for power base interval (Default:5)")])
class PCF8575Actor(CBPiActor):
    # Custom property which can be configured by the user
    @action("Set Power", parameters=[Property.Number(label="Power", configurable=True,description="Power Setting [0-100]")])
    async def setpower(self,Power = 100 ,**kwargs):
        self.power=int(Power)
        if self.power < 0:
            self.power = 0
        if self.power > 100:
            self.power = 100           
        await self.set_power(self.power)      

    async def on_start(self):
        self.power = None
        self.inverted = True if self.props.get("Inverted", "No") == "Yes" else False
        self.p1off = "LOW" if self.inverted == False else "HIGH"
        self.p1on  = "HIGH" if self.inverted == False else "LOW"
        self.gpio = self.props.get("GPIO", "p0")
        self.sampleTime = int(self.props.get("SamplingTime", 5))
        #p1.pin_mode(self.gpio,"OUTPUT")
        p1.write(self.gpio, self.p1off)
        self.state = False

    async def on(self, power = None):
        if power is not None:
            self.power = power
        else: 
            self.power = 100
        await self.set_power(self.power)

        logger.info("ACTOR %s ON - GPIO %s " %  (self.id, self.gpio))
        p1.write(self.gpio, self.p1on)
        self.state = True

    async def off(self):
        logger.info("ACTOR %s OFF - GPIO %s " % (self.id, self.gpio))
        p1.write(self.gpio, self.p1off)
        self.state = False

    def get_state(self):
        return self.state

    async def run(self):
        while self.running == True:
            if self.state == True:
                heating_time=self.sampleTime * (self.power / 100)
                wait_time=self.sampleTime - heating_time
                if heating_time > 0:
                    #logging.info("Heating Time: {}".format(heating_time))
                    p1.write(self.gpio, self.p1on)
                    await asyncio.sleep(heating_time)
                if wait_time > 0:
                    #logging.info("Wait Time: {}".format(wait_time))
                    p1.write(self.gpio, self.p1off)
                    await asyncio.sleep(wait_time)
            else:
                await asyncio.sleep(1)


    async def set_power(self, power):
        self.power = power
        await self.cbpi.actor.actor_update(self.id,power)
        pass

def setup(cbpi):
    cbpi.plugin.register("PCF8575Actor", PCF8575Actor)
    cbpi.plugin.register("PCF8575_Config",PCF8575)
    pass



class PCF:

    def __init__(self, address):
        self.address = address
        self.status = True
        self.pinModeFlag = 0x00
        self.smBusNum = 1
        PCF85setup(address, self.smBusNum, self.status)

    def pin_mode(self, PinName, Mode):
        self.pinModeFlag = PCF85pin_mode(PinName, Mode, self.pinModeFlag)

    def read(self, PinName):
        return PCF85digitalRead(PinName, self.smBusNum, self.address)

    def write(self, PinName, Val):
        PCF85digitalWrite(PinName, Val, self.address, self.pinModeFlag, self.smBusNum)

    def set_i2cBus(self, port):
        self.smBusNum = port
    
    def get_i2cBus(self):
        return self.smBusNum
    
    def get_pin_mode(self, PinName):
        return PCF85get_pin_mode(PinName,self.pinModeFlag)
        
    def is_pin_output(self, PinName):
        return PCF85is_pin_output(PinName,self.pinModeFlag)
    
    def get_all_mode(self):
        return PCF85get_all_mode(self.pinModeFlag)


def PCF85setup(PCFAdd, smBus, status):
    if status:
        with SMBus(smBus) as bus:
            bus.write_byte(PCFAdd, 0xFF)
    elif not status:
        with SMBus(smBus) as bus:
            bus.write_byte(PCFAdd, 0x00)


def PCF85pin_mode(pinName, mode, flg):
    pn = pinNameToNum(pinName)
    return set_mode(pinName, mode, int(math.pow(2, pn)), flg)
    


def set_mode(pinName, mode, rValue, flg):
    pn = pinNameToNum(pinName)
    if "INPUT" in mode.strip() and isKthBitSet(flg, pn + 1):
        flg = flg - rValue
        return flg
    elif "OUTPUT" in mode.strip() and not isKthBitSet(flg, pn + 1):
        flg = flg + rValue
        return flg
    else:
        return flg


def PCF85digitalRead(pinName, smbs, addr):
    with SMBus(smbs) as bus:
        b = bus.read_byte(addr)
    if isKthBitSet(b, pinNameToNum(pinName) + 1):
        return True
    else:
        return False


def pinNameToNum(pinName):
    try:
        pn = int(pinName.strip().replace("p", "").strip())
        if pn in range(16):
            return pn
        else:
            print("Wrone pin name!")
    except:
        raise Exception("Wrone pin name!")


def isKthBitSet(n, k):
    if n & (1 << (k - 1)):
        return True
    else:
        return False


def PCF85digitalWrite(pinName, val, addr, flg, smbs):
    if isKthBitSet(flg, pinNameToNum(pinName) + 1):
        if "HIGH" in val.strip():
            write_data(pinNameToNum(pinName), 1, smbs, flg, addr)
        elif "LOW" in val.strip():
            write_data(pinNameToNum(pinName), 0, smbs, flg, addr)
        else:
            print("Wrong pin mode for pin",pinName)
    else:
        print("You can't write input pin")


def write_data(pnNum, val, smbs, flg, addr):
    if isKthBitSet(flg, pnNum + 1):
        with SMBus(smbs) as bus:
            wr = bus.read_byte(addr)
        if val == 0 and isKthBitSet(wr, pnNum + 1):
            wr = wr - int(math.pow(2, pnNum))
            with SMBus(smbs) as bus:
                bus.write_byte(addr, wr)
        elif val == 1 and not isKthBitSet(wr, pnNum + 1):
            wr = wr + int(math.pow(2, pnNum))
            with SMBus(smbs) as bus:
                bus.write_byte(addr, wr)

def PCF85get_pin_mode(pinName,flg):
    pn = pinNameToNum(pinName)
    if isKthBitSet(flg,pn+1):
        return "OUTPUT"
    else:
        return "INPUT"

def PCF85is_pin_output(pinName,flg):
    pn = pinNameToNum(pinName)
    return isKthBitSet(flg,pn+1)

def PCF85get_all_mode(flg):
    mlist = []
    for i in range(0,8):
        if isKthBitSet(flg,i+1):
            mlist.append("OUTPUT")
        else:
            mlist.append("INPUT")
    return mlist
