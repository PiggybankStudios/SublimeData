import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

# This command takes any selection and turns it into a string of Hexadecimal numbers
# For example, "Hello" becomes "0x48 0x65 0x6C 0x6C 0x6F"
# The prefix and seperator string can be defined as whatever string you want
# If undo is true then we will attempt to take the selected string of hex numbers
# and convert them back into ASCII characters. This process can produce invalid ASCII
# characters so be careful with it. It will also only work with spaces and "0x" prefixes 
class AsciiToHexCommand(sublime_plugin.TextCommand):
#
	def run(self, edit, undo=False, prefix="0x", seperator=" "):
	#
		for region in self.view.sel():
		#
			regionStr = self.view.substr(region)
			if (undo):
			#
				replaceStr = ""
				cIndex = 0
				while (cIndex < len(regionStr)):
				#
					currentChar = regionStr[cIndex]
					nextChar = 0
					if (cIndex < len(regionStr)-1):
					#
						nextChar = regionStr[cIndex+1]
					#
					
					if (currentChar == ' '):
					#
						cIndex += 1
						continue
					#
					elif (currentChar == '0' and nextChar == 'x'):
					#
						cIndex += 2
						continue
					#
					elif (cIndex >= len(regionStr)-1 or
						not IsHexChar(currentChar) or not IsHexChar(nextChar)):
					#
						replaceStr += '?'
						cIndex += 1
						continue
					#
					else:
					#
						hexStr = currentChar + nextChar
						hexValue = int(hexStr, 16)
						newChar = chr(hexValue)
						replaceStr += newChar
						
						cIndex += 2 
					#
				#
				self.view.replace(edit, region, replaceStr)
			#
			else:
			#
				replaceStr = ""
				wasNewLine = False
				for cIndex in range(0, len(regionStr)):
				#
					if (regionStr[cIndex] =='\n' or regionStr[cIndex] == '\r'):
					#
						replaceStr += regionStr[cIndex]
						wasNewLine = True
					#
					else:
					#
						if (cIndex != 0 and wasNewLine == False):
							replaceStr += seperator
						replaceStr += prefix
						
						charNum = ord(regionStr[cIndex])
						replaceStr += ("%02X" % charNum)
						
						wasNewLine = False
					#
				#
				
				self.view.replace(edit, region, replaceStr)
			#
		#
	#
#
