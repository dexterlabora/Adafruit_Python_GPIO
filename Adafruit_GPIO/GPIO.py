# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import platform


OUT 	= 0
IN 		= 1
HIGH 	= True
LOW 	= False


class BaseGPIO(object):
	"""Base class for implementing simple digital IO for a platform.
	Implementors are expected to subclass from this and provide an implementation
	of the setup, output, and input functions."""

	def setup(self, pin, mode):
		"""Set the input or output mode for a specified pin.  Mode should be
		either OUT or IN."""
		raise NotImplementedError

	def output(self, pin, value):
		"""Set the specified pin the provided high/low value.  Value should be
		either HIGH/LOW or a boolean (true = high)."""
		raise NotImplementedError

	def input(self, pin):
		"""Read the specified pin and return HIGH/true if the pin is pulled high,
		or LOW/false if pulled low."""
		raise NotImplementedError

	def set_high(self, pin):
		"""Set the specified pin HIGH."""
		self.output(pin, HIGH)

	def set_low(self, pin):
		"""Set the specified pin LOW."""
		self.output(pin, LOW)

	def is_high(self, pin):
		"""Return true if the specified pin is pulled high."""
		return self.input(pin) == HIGH

	def is_low(self, pin):
		"""Return true if the specified pin is pulled low."""
		return self.input(pin) == LOW


class RPiGPIOAdapter(BaseGPIO):
	"""GPIO implementation for the Raspberry Pi using the RPi.GPIO library."""

	def __init__(self, rpi_gpio, mode=None):
		self.rpi_gpio = rpi_gpio
		# Suppress warnings about GPIO in use.
		rpi_gpio.setwarnings(False)
		if mode == rpi_gpio.BOARD or mode == rpi_gpio.BCM:
			rpi_gpio.setmode(mode)
		elif mode is not None:
			raise ValueError('Unexpected value for mode.  Must be BOARD or BCM.')
		else:
			# Default to BCM numbering if not told otherwise.
			rpi_gpio.setmode(rpi_gpio.BCM)

	def setup(self, pin, mode):
		"""Set the input or output mode for a specified pin.  Mode should be
		either OUTPUT or INPUT.
		"""
		self.rpi_gpio.setup(pin, self.rpi_gpio.IN if mode == IN else \
								 self.rpi_gpio.OUT)

	def output(self, pin, value):
		"""Set the specified pin the provided high/low value.  Value should be
		either HIGH/LOW or a boolean (true = high).
		"""
		self.rpi_gpio.output(pin, value)

	def input(self, pin):
		"""Read the specified pin and return HIGH/true if the pin is pulled high,
		or LOW/false if pulled low.
		"""
		return self.rpi_gpio.input(pin)


class AdafruitBBIOAdapter(BaseGPIO):
	"""GPIO implementation for the Beaglebone Black using the Adafruit_BBIO
	library.
	"""

	def __init__(self, bbio_gpio):
		self.bbio_gpio = bbio_gpio

	def setup(self, pin, mode):
		"""Set the input or output mode for a specified pin.  Mode should be
		either OUTPUT or INPUT.
		"""
		self.bbio_gpio.setup(pin, self.bbio_gpio.IN if mode == IN else \
								  self.bbio_gpio.OUT)

	def output(self, pin, value):
		"""Set the specified pin the provided high/low value.  Value should be
		either HIGH/LOW or a boolean (true = high).
		"""
		self.bbio_gpio.output(pin, value)

	def input(self, pin):
		"""Read the specified pin and return HIGH/true if the pin is pulled high,
		or LOW/false if pulled low.
		"""
		return self.bbio_gpio.input(pin)


def get_platform_gpio(plat=platform.platform(), **keywords):
	"""Attempt to return a GPIO instance for the platform which the code is being
	executed on.  Currently supports only the Raspberry Pi using the RPi.GPIO
	library and Beaglebone Black using the Adafruit_BBIO library.  Will throw an
	exception if a GPIO instance can't be created for the current platform.  The
	returned GPIO object is an instance of BaseGPIO.
	"""
	if plat is None:
		raise RuntimeError('Could not determine platform type.')
	
	# TODO: Is there a better way to check if running on BBB or Pi?  Relying on
	# the architecture name is brittle because new boards running armv6 or armv7
	# might come along and conflict with this simple identification scheme.
	
	# Handle Raspberry Pi
	# Platform output on Raspbian testing/jessie ~May 2014:
	# Linux-3.10.25+-armv6l-with-debian-7.4
	if plat.lower().find('armv6l-with-debian') > -1:
		import RPi.GPIO
		return RPiGPIOAdapter(RPi.GPIO, **keywords)

	# Handle Beaglebone Black
	# Platform output on Debian ~May 2014:
	# Linux-3.8.13-bone47-armv7l-with-debian-7.4
	if plat.lower().find('armv7l-with-debian') > -1:
		import Adafruit_BBIO.GPIO
		return AdafruitBBIOAdapter(Adafruit_BBIO.GPIO, **keywords)

	# Couldn't determine platform, raise error.
	raise RuntimeError('Unsupported platform: {0}'.format(plat))