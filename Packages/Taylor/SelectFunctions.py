import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

import re

class SelectFunctionsCommand(sublime_plugin.TextCommand):
#
	def run(self, edit):
	#
		foundRegions = self.view.find_by_selector("entity.name.function")
		if (len(foundRegions) == 0):
		#
			print("No scopes matching entity.name.function found")
			return
		#
		
		newSelections = []
		for region in foundRegions:
		#
			lineRegion = self.view.line(region)
			indentationIndex = FindBeginOfLineAfterIndents(self.view, lineRegion)
			commentsIndex = FindEndOfLineBeforeComments(self.view, lineRegion)
			if (commentsIndex <= indentationIndex): commentsIndex = lineRegion.end()
			functionStr = self.view.substr(sublime.Region(indentationIndex, commentsIndex))
			function = CppFunction(functionStr)
			
			if (function.valid):
			#
				newSelections.append(sublime.Region(indentationIndex, commentsIndex))
			#
			else:
			#
				print("\"" + functionStr + "\" is not a valid function")
			#
		#
		
		if (len(newSelections) > 0):
		#
			self.view.sel().clear()
			self.view.sel().add_all(newSelections)
		#
	#
#