
# -*- coding: utf-8 -*-
import os
from aiohttp import web
import logging
from unittest.mock import MagicMock, patch
import asyncio
import random
# from smbus2 import SMBus
import smbus2
import math
import time
# import smbus
# from pcf8575 import PCF8575
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

@parameters([Property.Select(label="Address", options=["0x20"], description = "I2C Address"),
            Property.Select(label="GPIO", options=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15], description = "Output Number"),
            Property.Select(label="Inverted", options=["Yes", "No"],description="Yes: Active on high; No: Active on low"),
            # Property.Select(label="SamplingTime", options=[2,5],description="Time in seconds for power base interval (Default:5)")])
            ])

class PCF8575Actor(CBPiActor):
    # Custom property which can be configured by the user
    # @action("Set Power", parameters=[Property.Number(label="Power", configurable=True,description="Power Setting [0-100]")])
    # async def setpower(self,Power = 100 ,**kwargs):
    #     self.power=int(Power)
    #     if self.power < 0:
    #         self.power = 0
    #     if self.power > 100:
    #         self.power = 100           
    #     await self.set_power(self.power)      

    async def on_start(self):
        # global p1
        self.power = None
        self.inverted = True if self.props.get("Inverted") == "Yes" else False
        if self.inverted:
            self.p1on = False
            self.p1off = True
        else:
            self.p1on = True
            self.p1off = False
        self.gpio = int(self.props.get("GPIO"))
        # self.sampleTime = int(self.props.get("SamplingTime", 5))
        pcf_address = self.props.get("Address")
        self.address = int(pcf_address,16)
        # PCF8575(1,self.address).port[self.gpio] = self.p1off
        # PCF8575(1,self.address).port = [self.p1off,self.p1off,self.p1off,self.p1off,self.p1off,self.p1off,self.p1off,self.p1off,self.p1off,self.p1off,self.p1off,self.p1off,self.p1off,self.p1off,self.p1off,self.p1off]
        self.state = False


    async def on(self, power = None):
        # if power is not None:
        #     self.power = power
        # else: 
        #     self.power = 100
        # await self.set_power(self.power)

        # logger.info("ACTOR %s ON - GPIO %s " %  (self.id, self.gpio))
        # PCF8575(1,self.address).port[self.gpio] = self.p1on
        # PCF8575(1,self.address).set_output(self.gpio,self.p1on)
        
        PCF8575(1,self.address).set_output(self.gpio,self.p1on)
        self.state = True

    async def off(self):
        # logger.info("ACTOR %s OFF - GPIO %s " % (self.id, self.gpio))
        # PCF8575(1,self.address).port[self.gpio] = self.p1off
        # PCF8575(1,self.address).set_output(self.gpio,self.p1off)
        
        PCF8575(1,self.address).set_output(self.gpio,self.p1off)
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

class IOPort(list):
    """
    Represents the PCF8575 IO port as a list of boolean values.
    """
    def __init__(self, pcf8575, *args, **kwargs):
        super(IOPort, self).__init__(*args, **kwargs)
        self.pcf8575 = pcf8575

    def __setitem__(self, key, value):
        """
        Set an individual output pin.
        """
        self.pcf8575.set_output(key, value)

    def __getitem__(self, key):
        """
        Get an individual pin state.
        """
        return self.pcf8575.get_pin_state(key)

    def __repr__(self):
        """
        Represent port as a list of booleans.
        """
        state = self.pcf8575.bus.read_word_data(self.pcf8575.address, 0)
        ret = []
        for i in range(16):
            ret.append(bool(state & 1<<15-i))
        return repr(ret)

    def __len__(self):
        return 16

    def __iter__(self):
        for i in range(16):
            yield self[i]

    def __reversed__(self):
        for i in range(16):
            yield self[15-i]


class PCF8575(object):
    """
    A software representation of a single PCF8575 IO expander chip.
    """
    def __init__(self, i2c_bus_no, address):
        self.bus_no = i2c_bus_no
        self.bus = SMBus.SMBus(i2c_bus_no)
        self.address = address

    def __repr__(self):
        return "PCF8575(i2c_bus_no=%r, address=0x%02x)" % (self.bus_no, self.address)

    @property
    def port(self):
        """
        Represent IO port as a list of boolean values.
        """
        return IOPort(self)

    @port.setter
    def port(self, value):
        """
        Set the whole port using a list.
        """
        assert isinstance(value, list)
        assert len(value) == 16
        new_state = 0
        for i, val in enumerate(value):
            if val:
                new_state |= 1 << 15-i
        self.bus.write_byte_data(self.address, new_state & 0xff, (new_state >> 8) & 0xff)

    def set_output(self, output_number, value):
        """
        Set a specific output high (True) or low (False).
        """

        assert output_number in range(16), "Output number must be an integer between 0 and 15"
        current_state = self.bus.read_word_data(self.address, 0)
        bit = 1 << 15-output_number
        new_state = current_state | bit if value else current_state & (~bit & 0xff)
        # self.bus.write_byte_data(self.address, new_state & 0xff, (new_state >> 8) & 0xff)
        self.bus.write_byte_data(self.address, 0x00, 0x00)

    def get_pin_state(self, pin_number):
        """
        Get the boolean state of an individual pin.
        """
        assert pin_number in range(16), "Pin number must be an integer between 0 and 15"
        state = self.bus.read_word_data(self.address, 0)
        return bool(state & 1<<15-pin_number)
