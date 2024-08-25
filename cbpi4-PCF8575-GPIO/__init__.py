
# -*- coding: utf-8 -*-
import os
from aiohttp import web
import logging
from unittest.mock import MagicMock, patch
import asyncio
import random
from smbus2 import SMBus
import math
import time
from pcf8575 import PCF8575
from cbpi.api import *
from cbpi.api.config import ConfigType
from cbpi.api.dataclasses import Props
from cbpi.api.base import CBPiBase

logger = logging.getLogger(__name__)

# creates the PCF_IO object only during startup. All sensors are using the same object
# def PCFActor(address):
#     global p1
#     i2c_port_num = 1
#     # pcf_address = 0x20
#     pcf = PCF8575(i2c_port_num,address)

#     pins=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
#     logger.info("***************** Start PCF Actor on I2C address {} ************************".format(hex(address)))
#     try:
#         # create to object with the defined address
#         # All pins are set to input at start -> set them to output and low
#         for pin in pins:
#             # p1.pin_mode(pin,"OUTPUT")
#             # p1.write(pin, "LOW")
#             pcf.port[pin] = False
#         pass
#     except:
#         p1 = None
#         logging.info("Error. Could not activate PCF8575 on I2C address {}".format(address))
#         pass


# check if PCF address parameter is included in settings. Add it to settings if it not already included.
# call PCFActor function once at startup to create the PCF Actor object
# class PCF8575(CBPiExtension):

#     def __init__(self,cbpi):
#         self.cbpi = cbpi
#         self._task = asyncio.create_task(self.init_actor())

#     async def init_actor(self):
#         await self.PCF8575_Address()
        # logger.info("Checked PCF Address")
        # PCF8575_Address = self.cbpi.config.get("PCF8575_Address", "0x20")
        # address=int(PCF8575_Address,16)
        # PCFActor(address)

    # async def PCF8575_Address(self): 
    #     global PCF8575_address
    #     plugin = await self.cbpi.plugin.load_plugin_list("cbpi4-PCF8575-GPIO")
    #     self.version=plugin[0].get("Version","0.0.0")
    #     self.name=plugin[0].get("Name","cbpi4-PCF8575-GPIO")

    #     self.PCF8575_update = self.cbpi.config.get(self.name+"_update", None)


    #     PCF8575_Address = self.cbpi.config.get("PCF8575_Address", None)
    #     if PCF8575_Address is None:
    #         logger.info("INIT PCF8575_Address")
    #         try:
    #             await self.cbpi.config.add('PCF8575_Address', '0x20', type=ConfigType.STRING, 
    #                                        description='PCF8575 I2C Bus address (e.g. 0x20). Change requires reboot',
    #                                        source=self.name)
    #             PCF8575_Address = self.cbpi.config.get("PCF8575_Address", None)
    #         except Exception as e:
    #                 logger.warning('Unable to update config')
    #                 logger.warning(e)
    #     else:
    #         if self.PCF8575_update == None or self.PCF8575_update != self.version:
    #             try:
    #                 await self.cbpi.config.add('PCF8575_Address', PCF8575_Address, type=ConfigType.STRING, 
    #                                        description='PCF8575 I2C Bus address (e.g. 0x20). Change requires reboot',
    #                                        source=self.name)
    #             except Exception as e:
    #                 logger.warning('Unable to update config')
    #                 logger.warning(e)
                    
    #     if self.PCF8575_update == None or self.PCF8575_update != self.version:
    #         try:
    #             await self.cbpi.config.add(self.name+"_update", self.version, type=ConfigType.STRING,
    #                                        description="PCF8575 Plugin Version",
    #                                        source='hidden')
    #         except Exception as e:
    #             logger.warning('Unable to update config')
    #             logger.warning(e)
    #         pass                

@parameters([Property.Select(label="Address", options=[0x20], description = "I2C Address"),
             Property.Select(label="GPIO", options=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15], description = "Output Pin")
            #  Property.Select(label="Inverted", options=["Yes", "No"],description="No: Active on high; Yes: Active on low"),
            #  Property.Select(label="SamplingTime", options=[2,5],description="Time in seconds for power base interval (Default:5)")])
            ])

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
        # self.inverted = True if self.props.get("Inverted", "No") == "Yes" else False
        # self.p1off = False if self.inverted == False else True
        # self.p1on  = True if self.inverted == False else False
        self.gpio = int(self.props.get("GPIO"))
        # self.sampleTime = int(self.props.get("SamplingTime", 5))
        self.address = self.props.get("Address")
        # PCF8575(1,self.address).port(self.gpio) = False
        self.state = False

    async def on(self, power = None):
        # if power is not None:
        #     self.power = power
        # else: 
        #     self.power = 100
        # await self.set_power(self.power)

        # logger.info("ACTOR %s ON - GPIO %s " %  (self.id, self.gpio))
        # """ p1.write(self.gpio, self.p1on)
        # self.state = True """
        PCF8575(1,self.address).port[self.gpio] = True
        self.state = True

    async def off(self):
        # logger.info("ACTOR %s OFF - GPIO %s " % (self.id, self.gpio))
        # """ p1.write(self.gpio, self.p1off)
        # self.state = False """
        PCF8575(1,self.address).port[self.gpio] = False
        self.state = False
        
    def get_state(self):
        return self.state
        
    async def run(self):
        while self.running == True:
            # if self.state == True:
            #     heating_time=self.sampleTime * (self.power / 100)
            #     wait_time=self.sampleTime - heating_time
            #     if heating_time > 0:
            #         #logging.info("Heating Time: {}".format(heating_time))
            #         p1.write(self.gpio, self.p1on)
            #         await asyncio.sleep(heating_time)
            #     if wait_time > 0:
            #         #logging.info("Wait Time: {}".format(wait_time))
            #         p1.write(self.gpio, self.p1off)
            #         await asyncio.sleep(wait_time)
            # else:
                await asyncio.sleep(1)


    async def set_power(self, power):
        # self.power = power
        # await self.cbpi.actor.actor_update(self.id,power)
        pass

def setup(cbpi):
    cbpi.plugin.register("PCF8575Actor", PCF8575Actor)
    # cbpi.plugin.register("PCF8575_Config",PCF8575)
    pass
