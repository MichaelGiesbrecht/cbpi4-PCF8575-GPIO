# CraftBeerPi4 PCF8575 IO Actor Plugin 

### PCF8575 based Actor

Plugin is a modified version of the PCF8574 plugin that will add an PCF8575Actor which has to possibility to define up 16 additional actors to your pi. The board needs to be connected via I2C
Theoretically, multiple boards (up to 8) could be connected with different addresses to make up to 128 IO ports available. However, the pulgin currently supports one board.

### Installation: 
- sudo pip3 install cbpi4-PCF8575-GPIO
- or install from repo: sudo pip3 install https://github.com/MichaelGiesbrecht/cbpi4-PCF8575-GPIO/archive/refs/heads/main.zip
	
### Usage:

- Configure the PCF8575 I2C Address in the cbpi global settings. 

![PCF8574 I2C address Settings](https://github.com/PiBrewing/cbpi4-PCF8574-GPIO/blob/main/PCF8574_Address_Settings.png?raw=true)

- Add an actor under Hardware/Actor and select PCF8575Actor
- Select the pin you want to switch (p0 to p15)
- Select 2 or 5 seconds for the Samplingtime (Will define the 'Resolution' for Power settings)
- Select Inverted yes or no. No means, that the pin will be on high if the sensor is active

### Hardware requirements:

Some information can be found here: https://www.instructables.com/PCF8574-GPIO-Extender-With-Arduino-and-NodeMCU/
Connect the device to 5 Volt, GND and your I2C bus. Check the Address ans set it to a different address if required
According to the datasheet, the pins can handle up to 25 mA. If you want to trigger an SSR or a relais, it is recommended to add a darlington array like the ULN2308

### Changelog:

- 08-17-24: (0.0.1) Initial release for testing
