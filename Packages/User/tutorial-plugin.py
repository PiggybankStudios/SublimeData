import os, sys, sublime, sublime_plugin
sys.path.append(os.path.dirname(__file__))
from User.MyFunctions import *

import re
import webbrowser

# Replaces the selected characters in the file with a specified character
# This function skips replaces new line characters and tabs
class CharacterReplaceCommand(sublime_plugin.TextCommand):
	def run(self, edit, character="#"):
		for region in self.view.sel():
			for cIndex in range(region.begin(), region.end()):
				charRegion = sublime.Region(cIndex, cIndex+1)
				currentChar = self.view.substr(charRegion)
				if (currentChar != '\n' and currentChar != '\r' and currentChar != '\t'):
					self.view.replace(edit, charRegion, character)

# Expands each selection to word bounderies and then removes the characters in the selection
class KillWordCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		for region in self.view.sel():
			word = self.view.word(region)
			self.view.erase(edit, word)

# Opens	up a web browser and searches the selected text on google
# Multiple selections will be concatenated together with spaces into a single search
# If remove_text is true then the selected text will be deleted at the same time
class MyGoogleSearchCommand(sublime_plugin.TextCommand):
	def run(self, edit, remove_text=False):
		# print("Running")
		searchString = ""
		for region in self.view.sel(): 
			if (searchString != ""):
				searchString = searchString + " "
			searchString = searchString + self.view.substr(region)
		
		if (len(searchString) > 0):
			print("My Google Search: Searching for \"" + searchString + "\"")
			searchString = searchString.replace(" ", "+")
			
			webbrowser.open("https://www.google.com/search?q=" + searchString)
		else:
			print("Nothing selected to search for")
		
		if (remove_text):
			for region in self.view.sel():
				self.view.erase(edit, region)
			# self.view.sel().clear()

# If the cursor is within the quotation marks or angle brackets of a C #include line
# then this command will attempt to extract the file name and open up the goto window
# with the file name pre-entered
class OpenStringFileCommand(sublime_plugin.TextCommand):
	
	def want_event(self):
		return True
	
	def run(self, edit, event = None, forcePos = None):
		region = self.view.sel()[0]
		# If we were passed an event we want to look at the point
		# that was clicked on by the mouse instead of selected points
		if (event != None):
			textPos = self.view.window_to_text([event['x'], event['y']])
			region = sublime.Region(textPos, textPos)
		if (forcePos != None):
			region = sublime.Region(forcePos, forcePos)
		
		fileName = GetCString(self.view, region)
		
		if (len(fileName) > 0):
			print("Opening file overlay for filename \"" + fileName + "\"")
			targetGroup = (self.view.window().active_group() + 1) % self.view.window().num_groups()
			self.view.window().focus_group(targetGroup)
			self.view.window().run_command("show_overlay", 
				{"overlay": "goto", "show_files": True, "text": fileName})
	
	# This function determines whether this command shows up in the context menu
	def is_visible(self, event = None):
		region = self.view.sel()[0]
		# If we were passed an event we want to look at the point
		# that was clicked on by the mouse instead of selected points
		if (event != None):
			textPos = self.view.window_to_text([event['x'], event['y']])
			region = sublime.Region(textPos, textPos)
		
		return LineIsInclude(self.view, region)

# This listener works in tandem with the OpenStringFileCommand to provide a little
# helpful window that shows up when hovering over a C #include line
class IncludeHoverEventListener(sublime_plugin.ViewEventListener):
	
	def OnPopupLinkClicked(self, link):
		self.view.window().run_command("show_overlay", 
			{"overlay": "goto", "show_files": True, "text": link})

	def on_hover(self, point, hover_zone):
		region = sublime.Region(point, point);
		if (hover_zone == sublime.HOVER_TEXT and
			LineIsInclude(self.view, region)):
			# print("Line is #include!")
			fileName = GetCString(self.view, region)
			if (len(fileName) > 0):
				htmlCode = ("<p style=\"padding:0px;margin:0px\">#included file:</p>" + 
					"<a href=\"" + fileName +"\">" + 
					fileName + "</a>?")
				self.view.show_popup(htmlCode, 
					sublime.HIDE_ON_MOUSE_MOVE_AWAY, point, 
					100000, 10000, self.OnPopupLinkClicked)

# This command moves each cursor to the next empty line from where it's currently at
# It's designed to be a general purpose command with lots of options that can be set
class MoveToEmptyLineCommand(sublime_plugin.TextCommand):
	def run(self, edit, forward=True, expand_selection=False, show_at_center=True):
		newSelections = []
		for region in self.view.sel():
			originPos = region.begin()
			if (forward):
				originPos = region.end()
			originRow, originColumn = self.view.rowcol(originPos)
			currentLine = "somethingNotEmpty";
			currentRow = originRow;
			foundBeginning = False;
			foundEnd = False;
			while (not LineIsEmpty(currentLine)):
				if (forward): currentRow += 1;
				else: currentRow -= 1;
				
				if (currentRow < 0):
					currentRow = 0;
					foundBeginning = True;
					print("Found beginning of file");
					break;
				
				pos = self.view.text_point(currentRow, 0);
				currentLine = self.view.substr(self.view.line(pos));
				
				if (pos == self.view.size()):
					print("Found end of file");
					foundEnd = True;
					break;
			
			print("Found line " + str(currentRow+1));
			
			if (foundBeginning):
				newPos = 0;
			elif (foundEnd):
				newPos = self.view.size();
			else:
				lineLength = len(currentLine)
				newPos = self.view.text_point(currentRow, lineLength);
			
			if (expand_selection):
				if (forward):
					newRegion = sublime.Region(region.begin(), newPos);
				else:
					newRegion = sublime.Region(region.end(), newPos);
			else:
				newRegion = sublime.Region(newPos, newPos);
			newSelections.append(newRegion);
		
		self.view.sel().clear();
		self.view.sel().add_all(newSelections);
		
		if (show_at_center and len(newSelections) == 1):
			self.view.show(newSelections[0].b);

# This command simply removes the line that each cursor currently resides on.
# If it resides on multiple it will kill all the lines it touches.
# We also attempt to place the cursor on the next line following the one killed
# at the same column that it was before you killed the line.
class KillLineCommand(sublime_plugin.TextCommand):
	def run(self, edit, next_line=True):
		newRegions = [];
		for region in self.view.sel():
			row, col = self.view.rowcol(region.b);
			lineRegion = self.view.full_line(region);
			endRow, endCol = self.view.rowcol(lineRegion.end());
			newLineRegion = self.view.line(self.view.text_point(endRow, 0));
			
			if (newLineRegion.size() >= col):
				endPosition = self.view.text_point(endRow, col);
			else:
				endPosition = self.view.text_point(endRow, newLineRegion.size());
			
			print("Row " + str(row) + ", Col " + str(col));
			print("End: Row " + str(endRow) + ", Col " + str(endCol));
			print("End Pos: " + str(endPosition));
			
			newRegion = sublime.Region(endPosition, endPosition);
			# newRegions.append(newRegion);
			self.view.sel().add(newRegion);
			self.view.sel().subtract(region);
			
			self.view.erase(edit, lineRegion);
			# self.view.sel().add(lineRegion);
		
		# self.view.sel().clear();
		# self.view.sel().add_all(newRegions);

# This command convertes to and from Decimal to Hexidecimal.
# It works entirely on ASCII representations of numbers
class ConvertToHexCommand(sublime_plugin.TextCommand):
	def run(self, edit, undo=False):
		for region in self.view.sel():
			regionStr = self.view.substr(region)
			if (len(regionStr) == 0):
				continue
			
			if (undo):
				try:
					integerValue = int(regionStr, 16)
				except ValueError:
					print("Could not parse \"" + regionStr + "\" as Base 16 integer")
					continue
				
				replaceStr = "%d" % (integerValue)
				self.view.replace(edit, region, replaceStr)
			else:
				try:
					integerValue = int(regionStr)
				except ValueError:
					print("Could not parse \"" + regionStr + "\" as Base 10 integer")
					continue
				
				replaceStr = "%X" % (integerValue)
				self.view.replace(edit, region, replaceStr)

# This command is helpful when writing multi-line macros in C. It allows you to easily
# add and remove \ characters to the end of each line from the cursor up to the line that
# contains #define. If you are removing the \ characters then the function also removes
# all \ on consecutive lines below and trailing whitespace that results.
class ToggleDefineEndingsCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		tabSize = self.view.settings().get("tab_size")
		for region in self.view.sel():
			lineNum, columnNum = self.view.rowcol(region.a)
			
			firstLineRegion = self.view.line(region.a)
			firstLineStr = self.view.substr(firstLineRegion)
			addingCharacters = True
			if (len(firstLineStr) > 0 and firstLineStr[-1] == '\\'):
				addingCharacters = False
			
			if (addingCharacters):
				# Count how many lines we need to go and find
				# the max line length
				numLines = 0
				maxLineLength = 0
				currentLine = lineNum
				while (currentLine >= 0):
					textPoint = self.view.text_point(currentLine, 0)
					lineRegion = self.view.line(textPoint)
					lineStr = self.view.substr(lineRegion)
					lineLength = ActualLineLength(tabSize, lineStr)
					
					print("Line %d: %u bytes \"%s\"" % (currentLine, lineLength, lineStr))
					numLines += 1
					
					if (lineLength > maxLineLength):
						maxLineLength = lineLength
					
					match = re.match("^\\s*\#define", lineStr)
					print("Match: " + str(match))
					
					if (match != None):
						break
					
					currentLine -= 1
				
				print("%u lines. Max Length: %u bytes" % (numLines, maxLineLength))
				
				currentLine = lineNum
				for lIndex in range(0, numLines):
					textPoint = self.view.text_point(currentLine, 0)
					lineRegion = self.view.line(textPoint)
					lineStr = self.view.substr(lineRegion)
					lineLength = ActualLineLength(tabSize, lineStr)
					
					while(lineLength <= maxLineLength):
						lineStr += ' '
						lineLength += 1
					lineStr += '\\'
					
					self.view.replace(edit, lineRegion, lineStr)
					
					currentLine -= 1
			else: # Removing characters
				
				# Remove going up
				currentLine = lineNum
				while (currentLine >= 0):
					textPoint = self.view.text_point(currentLine, 0)
					lineRegion = self.view.line(textPoint)
					lineStr = self.view.substr(lineRegion)
					
					if (len(lineStr) == 0 or lineStr[-1] != '\\'):
						break;
					
					while (lineStr[-1] == '\\' or lineStr[-1] == ' '):
						lineStr = lineStr[0:-1]
					
					self.view.replace(edit, lineRegion, lineStr)
					currentLine -= 1
				
				# Remove going down
				currentLine = lineNum+1
				while (True):
					textPoint = self.view.text_point(currentLine, 0)
					lineRegion = self.view.line(textPoint)
					lineStr = self.view.substr(lineRegion)
					
					if (len(lineStr) == 0 or lineStr[-1] != '\\'):
						break;
					
					while (lineStr[-1] == '\\' or lineStr[-1] == ' '):
						lineStr = lineStr[0:-1]
					
					self.view.replace(edit, lineRegion, lineStr)
					currentLine += 1

# This command takes any selection and turns it into a string of Hexadecimal numbers
# For example, "Hello" becomes "0x48 0x65 0x6C 0x6C 0x6F"
# The prefix and seperator string can be defined as whatever string you want
# If undo is true then we will attempt to take the selected string of hex numbers
# and convert them back into ASCII characters. This process can produce invalid ASCII
# characters so be careful with it. It will also only work with spaces and "0x" prefixes 
class AsciiToHexCommand(sublime_plugin.TextCommand):
	def run(self, edit, undo=False, prefix="0x", seperator=" "):
		for region in self.view.sel():
			regionStr = self.view.substr(region)
			
			if (undo):
				replaceStr = ""
				cIndex = 0
				while (cIndex < len(regionStr)):
					currentChar = regionStr[cIndex]
					nextChar = 0
					if (cIndex < len(regionStr)-1):
						nextChar = regionStr[cIndex+1]
					
					if (currentChar == ' '):
						cIndex += 1
						continue
					elif (currentChar == '0' and nextChar == 'x'):
						cIndex += 2
						continue
					elif (cIndex >= len(regionStr)-1 or
						not IsHexChar(currentChar) or not IsHexChar(nextChar)):
						replaceStr += '?'
						cIndex += 1
						continue
					else:
						hexStr = currentChar + nextChar
						hexValue = int(hexStr, 16)
						newChar = chr(hexValue)
						replaceStr += newChar
						
						cIndex += 2 
				
				self.view.replace(edit, region, replaceStr)
			else:
				replaceStr = ""
				wasNewLine = False
				for cIndex in range(0, len(regionStr)):
					if (regionStr[cIndex] =='\n' or regionStr[cIndex] == '\r'):
						replaceStr += regionStr[cIndex]
						
						wasNewLine = True
					else:
						if (cIndex != 0 and wasNewLine == False):
							replaceStr += seperator
						replaceStr += prefix
						
						charNum = ord(regionStr[cIndex])
						replaceStr += ("%02X" % charNum)
						
						wasNewLine = False
				
				self.view.replace(edit, region, replaceStr)

# This command attempts to jump to the next scope match from the cursor
# It can be used to jump between Function/Class definitions or any other syntax scope
# If select_whole is true it will also set the selection to the extent of the matching scope text (e.g. the whole function name)
# If show_centered is true it will bring the match into the center of the screen
# If loop_around is true then the function will loop around the end of the file to the beginning (or vice versa)
class GotoNextScopeCommand(sublime_plugin.TextCommand):
	def run(self, edit, forward=True, loop_around=False, scope_match="entity.", show_only=False, select_whole=True, show_centered=True):
		scopeMatchLen = len(scope_match)
		
		selections = self.view.sel()
		if (len(selections) != 1):
			print("More than one selection. Cannot goto next")
		
		startIndex = selections[0].b
		cIndex = startIndex
		
		success = False
		foundNonMatch = False
		foundFirst = False
		firstIndex = 0
		lastIndex = 0
		while (True):
			scopes = SplitScopesString(self.view.scope_name(cIndex))
			# print("Scopes: " + str(scopes))
			
			isMatch = False
			for scope in scopes:
				if (len(scope) >= scopeMatchLen and scope[0:scopeMatchLen] == scope_match):
					isMatch = True
					break
			
			if (isMatch):
				if (foundNonMatch and foundFirst == False):
					foundFirst = True
					firstIndex = cIndex
					if (forward == False):
						firstIndex += 1
						if (loop_around and firstIndex >= self.view.size()): firstIndex = 0
					print("Start Find: %u" % firstIndex)
			else:
				foundNonMatch = True
				if (foundFirst):
					lastIndex = cIndex
					if (forward == False):
						lastIndex += 1
						if (loop_around and lastIndex >= self.view.size()): lastIndex = 0
					print("End find: %u" % lastIndex)
					success = True
					break
			
			if (forward):
				cIndex += 1
				if (cIndex >= self.view.size()):
					if (loop_around): cIndex = 0
					else: break
			else:
				cIndex -= 1
				if (cIndex < 0):
					if (loop_around): cIndex = self.view.size()-1
					else: break
			
			if (cIndex == startIndex):
				break
		
		# NOTE: If the match extends all the way to the end of the file
		#		then we need to handle that case here
		if (foundFirst and success == False):
			if (cIndex < 0):
				lastIndex = 0
				success = True
			elif (cIndex >= self.view.size()):
				lastIndex = self.view.size()
				success = True
			else:
				print("Not sure exactly how we got here...")
		
		newRegion = sublime.Region(min(firstIndex, lastIndex), min(firstIndex, lastIndex))
		if (select_whole):
			newRegion = sublime.Region(max(firstIndex, lastIndex), min(firstIndex, lastIndex))
		regionStr = self.view.substr(newRegion)
		self.view.window().status_message("Found %s" % regionStr)
		if (success):
			if (show_centered):
				self.view.show_at_center(newRegion.b)
			else:
				self.view.show(newRegion.b)
			if (show_only == False):
				self.view.sel().clear()
				self.view.sel().add(newRegion)
		else:
			self.view.window().status_message("No Matching Scopes Found")

# This command is simply a placeholder that's useful for holding the place for an unbound hotkey
class DoNothingCommand(sublime_plugin.TextCommand):
	def run(self):
		print("Doing nothing!")

# This function attempts to search through the next non-empty line following the line the cursor is
# on and find a character that matches the one immediately following the cursor and is on a column
# farther to the right than the cursor. If found it will add spaces to the current cursors location
# until the two matching characters are aligned on the same column 
class AlignCharacterCommand(sublime_plugin.TextCommand):
	def run(self, edit, case_sensitive=False):
		
		regions = self.view.sel()
		
		for rIndex in reversed(range(0, len(regions))):
			region = regions[rIndex]
			textPos = region.b
			row, col = self.view.rowcol(textPos)
			currentCol = TextPointColumn(self.view, textPos)
			lineRegion = self.view.line(textPos)
			lineStr = self.view.substr(lineRegion)
			currentChar = self.view.substr(sublime.Region(textPos, textPos+1))
			
			if (len(currentChar) == 0):
				print("No character after the cursor on line %d" % (row+1))
				continue
			
			print("Char \'%c\' at line %d currentCol %d:\n%s" % (currentChar, row+1, currentCol, lineStr))
			
			nextLineStr = " "
			nextLineRow = row
			nextLineRegion = None
			foundEndOfFile = False
			while (LineIsEmpty(nextLineStr)):
				nextLineRow += 1
				nextLineRegion = self.view.line(self.view.text_point(nextLineRow, 0))
				
				if (nextLineRegion.begin() < lineRegion.end() or nextLineRegion.begin() >= self.view.size()):
					foundEndOfFile = True
					break
				
				nextLineStr = self.view.substr(nextLineRegion)
			
			if (foundEndOfFile):
				print("End of file without finding a non-empty line")
				continue
			
			print("Checking line %d:\n%s" % (nextLineRow, nextLineStr))
			
			nextTextPos = RowColumnTextPoint(self.view, nextLineRow, currentCol)
			nextLineIndex = nextTextPos - nextLineRegion.begin()
			
			foundMatch  = False
			matchColumn = 0
			while (nextLineIndex < nextLineRegion.size()):
				nextLineChar = self.view.substr(sublime.Region(nextLineRegion.begin() + nextLineIndex, nextLineRegion.begin() + nextLineIndex + 1))
				if (nextLineChar == None):
					nextLineIndex += 1
					continue
				
				print("Char %d: \'%c\'" % (nextLineIndex, nextLineChar))
				
				if (nextLineChar == currentChar or (not case_sensitive and nextLineChar.lower() == currentChar.lower())):
					foundMatch = True
					matchColumn = TextPointColumn(self.view, nextLineRegion.begin() + nextLineIndex)
					break
				
				nextLineIndex += 1
			
			if (foundMatch):
				print("Found match at column %d" % (matchColumn))
				print("Moving from column %d" % (currentCol))
				
				insertString = " " * (matchColumn - currentCol)
				self.view.insert(edit, textPos, insertString)
			else:
				print("No match found in next line")

# This command searches the whole file and tries to fill empty lines with tabs/spaces until it matches
# the indentation of the previous line.
class IndentBlankLinesCommand(sublime_plugin.TextCommand):
	def run(self, edit, use_tabs=True):
		tabSize = self.view.settings().get("tab_size")
		
		rowIndex = 0
		textPoint = 0
		while (textPoint < self.view.size()):
			textPoint = self.view.text_point(rowIndex, 0)
			lineRegion = self.view.line(textPoint)
			lineStr = self.view.substr(lineRegion)
			
			if (rowIndex > 0 and LineIsEmpty(lineStr) and len(lineStr) == 0):
				lastLineRegion = self.view.line(self.view.text_point(rowIndex-1, 0))
				lastLineStr = self.view.substr(lastLineRegion)
				lastLineIndentation = GetLineIndentation(lastLineStr)
				
				if (ActualLineLength(tabSize, lineStr) < ActualLineLength(tabSize, lastLineIndentation)):
					newLineStr = lineStr
					while (ActualLineLength(tabSize, newLineStr) < ActualLineLength(tabSize, lastLineIndentation)):
						if (use_tabs):
							newLineStr += '\t'
						else:
							newLineStr += ' '
					self.view.replace(edit, lineRegion, newLineStr)
			
			rowIndex += 1
			textPoint = lineRegion.end()

