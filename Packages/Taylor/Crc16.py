import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

def PrintHexString(inputStr):
#
	for cIndex in range(0, len(inputStr)):
	#
		if (cIndex > 0): sys.stdout.write(" ")
		sys.stdout.write("%02X" % ord(inputStr[cIndex]))
	#
	sys.stdout.flush()
#

def CalculateCrc16(inputStr):
#
	crcTable = (0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50A5, 0x60C6, 0x70E7, 0x8108, 0x9129, 0xA14A, 0xB16B, 0xC18C, 0xD1AD, 0xE1CE, 0xF1EF)
	result = 0x0000
	
	for char in inputStr:
	#
		byteValue = ord(char)
		if (byteValue > 0xFF): byteValue = 0xFF
		print("%02X" % byteValue)
		
		temp = 0xFFFFFFFF & ((result >> 12) ^ (byteValue >> 4))
		result = 0xFFFF & (crcTable[temp & 0x0F] ^ (result << 4))
		temp = 0xFFFFFFFF & ((result >> 12) ^ (byteValue >> 0))
		result = 0xFFFF & (crcTable[temp & 0x0F] ^ (result << 4))
	#
	
	return result
#

# Replaces all selected regions with the MD5 hash of the text in HEX
class Crc16Command(sublime_plugin.TextCommand):
	def run(self, edit, convert_to_hex=False):
	#
		for region in self.view.sel():
		#
			regionStr = self.view.substr(region)
			if (convert_to_hex):
			#
				regionStr = ConvertStrToHex(regionStr)
				sys.stdout.write("Converted Hex String: [%u]{" % len(regionStr))
				PrintHexString(regionStr)
				print("}")
			#
			crc16 = CalculateCrc16(regionStr)
			crc16Str = ("%04X" % crc16)
			self.view.replace(edit, region, crc16Str)
		#
	#
#