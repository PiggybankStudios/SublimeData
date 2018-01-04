import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

class CheckOffTodoItemCommand(sublime_plugin.TextCommand):
#
	def run(self, edit, move_line=False, check_str="X"):
	#
		selectionRegion = self.view.sel()[0]
		lineRegion = self.view.line(selectionRegion)
		lineStr = self.view.substr(lineRegion)
		
		checkboxRegion = lineRegion
		while (checkboxRegion.a < checkboxRegion.b):
		#
			scope = self.view.scope_name(checkboxRegion.a)
			# print("scope = \"%s\"" % scope)
			if (scope.find("checkbox.punctuation.todo") != -1): break
			else: checkboxRegion.a += 1
		#
		if (checkboxRegion.a >= checkboxRegion.b):
		#
			print("No checkbox found")
			return
		#
		
		checkboxStr = self.view.substr(checkboxRegion)
		# print("checkboxStr = \"%s\"" % checkboxStr)
		if (len(checkboxStr) < 3):
		#
			print("checkboxStr is too short")
			return
		#
		
		checkboxStr = checkboxStr[0] + check_str + checkboxStr[2:]
		print("Checked checkboxStr = \"%s\"" % checkboxStr)
		
		deleteRegion = checkboxRegion
		insertPos = deleteRegion.end()
		insertString = checkboxStr
		selectionRegion = sublime.Region(checkboxRegion.end())
		if (move_line):
		#
			foundCheckedItem = False
			newLineIndex = self.view.rowcol(insertPos)[0] + 1
			while (not foundCheckedItem):
			#
				newLineRegion = self.view.line(self.view.text_point(newLineIndex, 0))
				if (newLineRegion.begin() >= self.view.size()):
				#
					print("Found end of file")
					break
				#
				newLineStr = self.view.substr(newLineRegion)
				while (newLineRegion.a < newLineRegion.b and (self.view.substr(newLineRegion.a) == ' ' or self.view.substr(newLineRegion.a) == '\t')):
				#
					newLineRegion.a += 1
				#
				
				if (self.view.match_selector(newLineRegion.a, "comment.checkbox")):
				#
					foundCheckedItem = True
					insertPos = self.view.line(newLineRegion.a).begin()
					insertString = GetLineIndentation(newLineStr) + insertString + "\n"
					
					# Put the cursor at the end of the line that followed the original cursor line
					nextLineNum = self.view.rowcol(selectionRegion.b)[0] + 1
					nextLineRegion = self.view.line(self.view.text_point(nextLineNum, 0))
					nextLineStr = self.view.substr(nextLineRegion)
					# print("Next line is \"%s\"" % nextLineStr)
					selectionRegion = self.view.line(deleteRegion.begin()).begin() + len(nextLineRegion)
					
					# Expand the deletion region to the whole line if it's by itself on the line
					while (self.view.substr(deleteRegion.a-1) == ' ' or self.view.substr(deleteRegion.a-1) == '\t'):
					#
						deleteRegion.a -= 1
					#
					# if (self.view.substr(deleteRegion.a-1) == "\n"):
					# #
					# 	deleteRegion.a -= 1
					# #
					if (self.view.substr(deleteRegion.b) == "\n"):
					#
						deleteRegion.b += 1
					#
					break
				#
				else:
				#
					newLineIndex += 1
				#
			#
		#
		
		self.view.insert(edit, insertPos, insertString)
		tempStr = self.view.substr(deleteRegion)
		# print("Replacing \"%s\"" % (tempStr))
		self.view.replace(edit, deleteRegion, "")
		self.view.sel().clear()
		self.view.sel().add(selectionRegion)
	#
#
