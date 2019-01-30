import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

#TODO: Make the cursors end up inside the collapsed/expanded braces after the edit
class CollapseBracesCommand(sublime_plugin.TextCommand):
#
	def run(self, edit):
	#
		fileSize = self.view.size()
		for region in self.view.sel():
		#
			# +==============================+
			# |       Find Start Brace       |
			# +==============================+
			startIndex = -1
			cIndex = region.b
			if (cIndex >= fileSize): cIndex = fileSize-1
			while (cIndex >= 0):
			#
				if (not IsStringOrComment(self.view, cIndex)):
				#
					c = self.view.substr(cIndex)
					if (c == '{'):
					#
						startIndex = cIndex+1
						break
					#
				#
				cIndex -= 1
			#
			if (startIndex <= 0):
			#
				print("Couldn't find starting curly brace")
				return
			#
			
			# +==============================+
			# |        Find End Brace        |
			# +==============================+
			endIndex = -1
			cIndex = startIndex+1
			braceCount = 1
			while (cIndex < fileSize):
			#
				if (not IsStringOrComment(self.view, cIndex)):
				#
					c = self.view.substr(cIndex)
					if (c == '}'):
					#
						braceCount -= 1
						if (braceCount <= 0):
						#
							endIndex = cIndex
							break
						#
					#
					elif (self.view.substr(cIndex) == '{'):
					#
						braceCount += 1
					#
				#
				cIndex += 1
			#
			if (endIndex <= 0):
			#
				print("Couldn't find ending curly brace")
				return
			#
			
			curlyStartLine, curlyStartColumn = self.view.rowcol(startIndex-1)
			curlyRegion = sublime.Region(startIndex-1, endIndex+1)
			contentRegion = sublime.Region(startIndex, endIndex)
			contentStr = self.view.substr(contentRegion)
			splitLines = SplitLines(contentStr)
			# print("Found " + str(len(splitLines)) + " lines:\n" + str(splitLines))
			
			# +==============================+
			# |      Expand Single Line      |
			# +==============================+
			if (len(splitLines) <= 1):
			#
				lines = SplitBySemicolons(contentStr)
				print("Expanding " + str(len(lines)) + " statements") #:\n" + str(lines))
				
				insertLine = curlyStartLine
				insertLineIndex = self.view.text_point(insertLine, 0)
				insertLineRegion = self.view.line(insertLineIndex)
				insertLineStr = self.view.substr(insertLineRegion)
				indentation = GetLineIndentation(insertLineStr)
				insertStr = "\n" + indentation + "{\n" + indentation + "\t" + ("\n" + indentation + "\t").join(lines) + "\n" + indentation + "}"
				# print("Expanded:\n" + insertStr)
				
				removeRegion = curlyRegion
				while (removeRegion.a > 0 and IsSpaceOrTab(self.view.substr(removeRegion.a-1))): removeRegion.a -= 1
				while (removeRegion.b < fileSize and IsSpaceOrTab(self.view.substr(removeRegion.b))): removeRegion.b += 1
				
				self.view.insert(edit, insertLineRegion.end(), insertStr)
				self.view.erase(edit, removeRegion)
			#
			# +==============================+
			# |     Collapse Multi-line      |
			# +==============================+
			elif (len(splitLines) > 1):
			#
				lines = []
				for line in splitLines:
				#
					actualLine = StripOuterWhitespace(line)
					if (len(actualLine) > 0):
					#
						lines.append(actualLine)
					#
				#
				print("Collapsing " + str(len(lines)) + " lines:\n" + str(lines))
				
				insertLine = curlyStartLine-1
				if (insertLine < 0): insertLine = 0
				insertLineIndex = self.view.text_point(insertLine, 0)
				insertLineRegion = self.view.line(insertLineIndex)
				insertLineStr = self.view.substr(insertLineRegion)
				insertPos = FindEndOfLineBeforeComments(self.view, insertLineRegion)
				
				#TODO: Maybe this region expansion should also take into account comments and other things?
				removeRegion = self.view.line(curlyRegion)
				if (removeRegion.a > 0 and self.view.substr(removeRegion.a-1) == '\n'): removeRegion.a -= 1
				# if (removeRegion.b < fileSize and self.view.substr(removeRegion.b) == '\n'): removeRegion.b += 1
				
				newContent = " " + (" ").join(lines) + " "
				if (len(newContent) == 2): newContent = " " #NOTE: Empty content becomes a single space, not two
				insertStr = " {" + newContent + "}"
				
				self.view.erase(edit, removeRegion)
				self.view.insert(edit, insertPos, insertStr)
			#
		#
	#
#