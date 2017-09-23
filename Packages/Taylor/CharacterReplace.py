import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

# Replaces the selected characters in the file with a specified character
# This function skips replaces new line characters and tabs
class CharacterReplaceCommand(sublime_plugin.TextCommand):
	def run(self, edit, character="#"):
	#
		for region in self.view.sel():
		#
			for cIndex in range(region.begin(), region.end()):
			#
				charRegion = sublime.Region(cIndex, cIndex+1)
				currentChar = self.view.substr(charRegion)
				if (currentChar != '\n' and currentChar != '\r' and currentChar != '\t'):
				#
					self.view.replace(edit, charRegion, character)
				#
			#
		#
	#
#
