import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

# This command is helpful when writing multi-line macros in C. It allows you to easily
# add and remove \ characters to the end of each line from the cursor up to the line that
# contains #define. If you are removing the \ characters then the function also removes
# all \ on consecutive lines below and trailing whitespace that results.
class ToggleDefineEndingsCommand(sublime_plugin.TextCommand):
#
	def run(self, edit):
	#
		tabSize = self.view.settings().get("tab_size")
		for region in self.view.sel():
		#
			lineNum, columnNum = self.view.rowcol(region.a)
			
			firstLineRegion = self.view.line(region.a)
			firstLineStr = self.view.substr(firstLineRegion)
			addingCharacters = True
			if (len(firstLineStr) > 0 and firstLineStr[-1] == '\\'):
			#
				addingCharacters = False
			#
			
			if (addingCharacters):
			#
				# Count how many lines we need to go and find
				# the max line length
				numLines = 0
				maxLineLength = 0
				currentLine = lineNum
				while (currentLine >= 0):
				#
					textPoint = self.view.text_point(currentLine, 0)
					lineRegion = self.view.line(textPoint)
					lineStr = self.view.substr(lineRegion)
					lineLength = ActualLineLength(tabSize, lineStr)
					
					print("Line %d: %u bytes \"%s\"" % (currentLine, lineLength, lineStr))
					numLines += 1
					
					if (lineLength > maxLineLength): maxLineLength = lineLength
					
					match = re.match("^\\s*\#define", lineStr)
					print("Match: " + str(match))
					
					if (match != None): break
					
					currentLine -= 1
				#
				
				print("%u lines. Max Length: %u bytes" % (numLines, maxLineLength))
				
				currentLine = lineNum
				for lIndex in range(0, numLines):
				#
					textPoint = self.view.text_point(currentLine, 0)
					lineRegion = self.view.line(textPoint)
					lineStr = self.view.substr(lineRegion)
					lineLength = ActualLineLength(tabSize, lineStr)
					
					while(lineLength <= maxLineLength):
					#
						lineStr += ' '
						lineLength += 1
					#
					lineStr += '\\'
					
					self.view.replace(edit, lineRegion, lineStr)
					currentLine -= 1
				#
			#
			else: # Removing character
			#
				# Remove going up
				currentLine = lineNum
				while (currentLine >= 0):
				#
					textPoint = self.view.text_point(currentLine, 0)
					lineRegion = self.view.line(textPoint)
					lineStr = self.view.substr(lineRegion)
					
					if (len(lineStr) == 0 or lineStr[-1] != '\\'): break;
					
					while (lineStr[-1] == '\\' or lineStr[-1] == ' '):
					#
						lineStr = lineStr[0:-1]
					#
					
					self.view.replace(edit, lineRegion, lineStr)
					currentLine -= 1
				#
				
				# Remove going down
				currentLine = lineNum+1
				while (True):
				#
					textPoint = self.view.text_point(currentLine, 0)
					lineRegion = self.view.line(textPoint)
					lineStr = self.view.substr(lineRegion)
					
					if (len(lineStr) == 0 or lineStr[-1] != '\\'): break;
					
					while (lineStr[-1] == '\\' or lineStr[-1] == ' '):
					#
						lineStr = lineStr[0:-1]
					#
					
					self.view.replace(edit, lineRegion, lineStr)
					currentLine += 1
				#
			#
		#
	#
#
