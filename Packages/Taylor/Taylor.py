import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

# This function is simply for testing new functionality. It's bound to ctrl+;
class TaylorCommand(sublime_plugin.TextCommand):
#
	def run(self, edit):
	#
		print("Running the Taylor Command!")
		
		settings = self.view.settings()
		print("\"syntax\" = \"%s\"" % settings.get("syntax"))
		
		for region in self.view.sel():
		#
			selectionStr = self.view.substr(region)
			# print("Selection: \"" + selectionStr + "\"")
			
			function = CppFunction(selectionStr)
			if (function.valid):
			#
				print("Parsed Function:", function)
			#
			else:
			#
				print("Could not parse function: \"%s\"" % (selectionStr))
			#
		#
	#
#

class GotoSubstringCommand(sublime_plugin.TextCommand):
#
	def run(self, edit, substring=","):
	#
		print("Going to substring \"%s\"" % (substring))
		
		substrLength = len(substring)
		
		for region in self.view.sel():
		#
			currentPos = region.b
			currentLineRegion = self.view.line(currentPos)
			currentLineStr = self.view.substr(currentLineRegion)
			
			while (currentPos < currentLineRegion.end()):
			#
				cPos = currentPos - currentLineRegion.begin()
				if (currentLineStr[cPos:cPos+substrLength] == substring):
				#
					print("Found substr at index %u/%u" % (cPos, currentLineRegion.end()))
					break;
				#
				else:
				#
					currentPos += 1
				#
			#
			
			self.view.sel().subtract(region)
			self.view.sel().add(sublime.Region(currentPos, currentPos))
		#
		
	#
#

class SelectAllLinesCommand(sublime_plugin.TextCommand):
#
	def run(self, edit):
	#
		# print("Selecting all lines")
		
		selections = []
		lIndex = 0
		while (True):
		#
			lineRegion = self.view.line(self.view.text_point(lIndex, 0))
			lineStr = self.view.substr(lineRegion)
			# print("Line[%u]: \"%s\"" % (lIndex, lineStr))
			
			selections.append(sublime.Region(lineRegion.begin(), lineRegion.begin()))
			
			if (lineRegion.end() >= self.view.size()): break
			else: lIndex += 1
			# if (lIndex >= 1000): break
		#
		
		print("Selecting %u lines" % (len(selections)))
		
		self.view.sel().clear()
		self.view.sel().add_all(selections)
	#
#


# This command is simply a placeholder that's useful for holding the place for an unbound hotkey
class DoNothingCommand(sublime_plugin.TextCommand):
#
	def run(self, edit):
	#
		print("Doing nothing!")
		sublime.status_message("Key is unbound");
	#
#

# This command searches the whole file and tries to fill empty lines with tabs/spaces until it matches
# the indentation of the previous line.
class IndentBlankLinesCommand(sublime_plugin.TextCommand):
#
	def run(self, edit, use_tabs=True):
	#
		tabSize = self.view.settings().get("tab_size")
		
		rowIndex = 0
		textPoint = 0
		while (textPoint < self.view.size()):
		#
			textPoint = self.view.text_point(rowIndex, 0)
			lineRegion = self.view.line(textPoint)
			lineStr = self.view.substr(lineRegion)
			
			if (rowIndex > 0 and LineIsEmpty(lineStr) and len(lineStr) == 0):
			#
				lastLineRegion = self.view.line(self.view.text_point(rowIndex-1, 0))
				lastLineStr = self.view.substr(lastLineRegion)
				lastLineIndentation = GetLineIndentation(lastLineStr)
				
				if (ActualLineLength(tabSize, lineStr) < ActualLineLength(tabSize, lastLineIndentation)):
				#
					newLineStr = lineStr
					while (ActualLineLength(tabSize, newLineStr) < ActualLineLength(tabSize, lastLineIndentation)):
					#
						if (use_tabs): newLineStr += '\t'
						else:          newLineStr += ' '
					#
					self.view.replace(edit, lineRegion, newLineStr)
				#
			#
			rowIndex += 1
			textPoint = lineRegion.end()
		#
	#
#

# Expands each selection to word bounderies and then removes the characters in the selection
class KillWordCommand(sublime_plugin.TextCommand):
#
	def run(self, edit):
	#
		for region in reversed(self.view.sel()):
		#
			word = self.view.word(region)
			self.view.erase(edit, word)
		#
	#
#
