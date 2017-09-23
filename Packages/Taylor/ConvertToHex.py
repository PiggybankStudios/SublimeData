import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

# This command convertes to and from Decimal to Hexidecimal.
# It works entirely on ASCII representations of numbers
class ConvertToHexCommand(sublime_plugin.TextCommand):
#
	def run(self, edit, undo=False):
	#
		for region in self.view.sel():
		#
			regionStr = self.view.substr(region)
			if (len(regionStr) == 0): continue
			
			if (undo):
			#
				try:
				#
					integerValue = int(regionStr, 16)
				#
				except ValueError:
				#
					print("Could not parse \"" + regionStr + "\" as Base 16 integer")
					continue
				#
				
				replaceStr = "%d" % (integerValue)
				self.view.replace(edit, region, replaceStr)
			#
			else:
			#
				try:
				#
					integerValue = int(regionStr)
				#
				except ValueError:
				#
					print("Could not parse \"" + regionStr + "\" as Base 10 integer")
					continue
				#
				
				replaceStr = "%X" % (integerValue)
				self.view.replace(edit, region, replaceStr)
			#
		#
	#
#
