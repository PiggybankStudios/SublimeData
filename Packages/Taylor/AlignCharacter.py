import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

# This function attempts to search through the next non-empty line following the line the cursor is
# on and find a character that matches the one immediately following the cursor and is on a column
# farther to the right than the cursor. If found it will add spaces to the current cursors location
# until the two matching characters are aligned on the same column 
class AlignCharacterCommand(sublime_plugin.TextCommand):
#
	def run(self, edit, case_sensitive=False):
	#
		regions = self.view.sel()
		
		for rIndex in reversed(range(0, len(regions))):
		#
			region = regions[rIndex]
			textPos = region.b
			row, col = self.view.rowcol(textPos)
			currentCol = TextPointColumn(self.view, textPos)
			lineRegion = self.view.line(textPos)
			lineStr = self.view.substr(lineRegion)
			currentChar = self.view.substr(sublime.Region(textPos, textPos+1))
			
			if (len(currentChar) == 0):
			#
				print("No character after the cursor on line %d" % (row+1))
				continue
			#
			
			print("Char \'%c\' at line %d currentCol %d:\n%s" % (currentChar, row+1, currentCol, lineStr))
			
			nextLineStr = " "
			nextLineRow = row
			nextLineRegion = None
			foundEndOfFile = False
			while (LineIsEmpty(nextLineStr)):
			#
				nextLineRow += 1
				nextLineRegion = self.view.line(self.view.text_point(nextLineRow, 0))
				
				if (nextLineRegion.begin() < lineRegion.end() or nextLineRegion.begin() >= self.view.size()):
				#
					foundEndOfFile = True
					break
				#
				nextLineStr = self.view.substr(nextLineRegion)
			#
			
			if (foundEndOfFile):
			#
				print("End of file without finding a non-empty line")
				continue
			#
			
			print("Checking line %d:\n%s" % (nextLineRow, nextLineStr))
			
			nextTextPos = RowColumnTextPoint(self.view, nextLineRow, currentCol)
			nextLineIndex = nextTextPos - nextLineRegion.begin()
			
			foundMatch  = False
			matchColumn = 0
			while (nextLineIndex < nextLineRegion.size()):
			#
				nextLineChar = self.view.substr(sublime.Region(nextLineRegion.begin() + nextLineIndex, nextLineRegion.begin() + nextLineIndex + 1))
				if (nextLineChar == None):
				#
					nextLineIndex += 1
					continue
				#
				
				print("Char %d: \'%c\'" % (nextLineIndex, nextLineChar))
				
				if (nextLineChar == currentChar or (not case_sensitive and nextLineChar.lower() == currentChar.lower())):
				#
					foundMatch = True
					matchColumn = TextPointColumn(self.view, nextLineRegion.begin() + nextLineIndex)
					break
				#
				
				nextLineIndex += 1
			#
			
			if (foundMatch):
			#
				print("Found match at column %d" % (matchColumn))
				print("Moving from column %d" % (currentCol))
				
				insertString = " " * (matchColumn - currentCol)
				self.view.insert(edit, textPos, insertString)
			#
			else:
			#
				print("No match found in next line")
			#
		#
	#
#
