import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

import re

class SelectLineCommand(sublime_plugin.TextCommand):
#
	def run(self, edit):
	#
		newSelections = []
		for region in self.view.sel():
		#
			lineRegion = self.view.line(region)
			indentationIndex = FindBeginOfLineAfterIndents(self.view, lineRegion)
			commentsIndex = FindEndOfLineBeforeComments(self.view, lineRegion)
			if (commentsIndex < indentationIndex): commentsIndex = indentationIndex
			
			if (indentationIndex == commentsIndex): #It's a line of only comments
			#
				if (region.begin() == indentationIndex and region.end() == lineRegion.end()):
				#
					newSelections.append(sublime.Region(lineRegion.begin(), lineRegion.end()))
				#
				else:
				#
					newSelections.append(sublime.Region(indentationIndex, lineRegion.end()))
				#
			#
			else:
			#
				if (region.begin() == indentationIndex and region.end() == commentsIndex):
				#
					newSelections.append(sublime.Region(lineRegion.begin(), lineRegion.end()))
				#
				else:
				#
					newSelections.append(sublime.Region(indentationIndex, commentsIndex))
				#
			#
		#
		
		self.view.sel().clear()
		self.view.sel().add_all(newSelections)
	#
#