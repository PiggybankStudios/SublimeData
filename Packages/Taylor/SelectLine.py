import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

import re

def FindBeginOfLineAfterIndents(view, region):
#
	result = region.begin()
	while (result < view.size() and result < region.end()):
	#
		c = view.substr(result)
		if (c == '\t' or c == ' '): result += 1
		else: break
	#
	return result
#

def FindEndOfLineBeforeComments(view, region):
#
	result = region.end()
	while (result > 0 and result > region.begin()):
	#
		scopeNames = view.scope_name(result-1).split(" ")
		isComment = False
		for scope in scopeNames:
		#
			scopeParts = scope.split(".")
			if (len(scopeParts) > 0 and scopeParts[0] == "comment"):
			#
				isComment = True
				break
			#
		#
		if (isComment): result -= 1
		else:
		#
			c = view.substr(result-1)
			if (c == ' ' or c == '\t'): result -= 1
			else: break
		#
	#
	return result
#

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
			
			if (region.begin() == indentationIndex and region.end() == commentsIndex):
			#
				newSelections.append(sublime.Region(lineRegion.begin(), lineRegion.end()))
			#
			else:
			#
				newSelections.append(sublime.Region(indentationIndex, commentsIndex))
			#
		#
		
		self.view.sel().clear()
		self.view.sel().add_all(newSelections)
	#
#