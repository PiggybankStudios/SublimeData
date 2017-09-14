import sublime
import sublime_plugin
import re

import webbrowser

def GetCString(view, region):
	startIndex = region.begin()
	endIndex = region.end()
	viewSize = view.size()
	
	if (startIndex == 0):
		return "";
	
	# Step back till we find the (non-escaped) quotation mark or the beginning of line/file
	currentChar = view.substr(startIndex-1)
	while (startIndex > 0):
		if (currentChar == '\"' and (startIndex <= 0 or view.substr(startIndex-2) != "\\")):
			break
		if (currentChar == '\n' or currentChar == '\r'):
			# startIndex = startIndex + 1
			return ""
		if (currentChar == '<'):
			break
		if (endIndex - startIndex > 256):
			break
		# print("<" + currentChar)
		startIndex = startIndex - 1
		currentChar = view.substr(startIndex-1)
	
	if (startIndex == 0):
		return "";
	
	# Step forward till we find the (non-escaped) quotation mark or the end of line/file
	currentChar = view.substr(endIndex)
	while (endIndex < viewSize):
		if (currentChar == '\"' and (endIndex <= 0 or view.substr(endIndex-1) != "\\")):
			break
		if (currentChar == '\n' or currentChar == '\r'):
			return ""
		if (currentChar == '>'):
			break;
		if (endIndex - startIndex > 256):
			break
		# print(">" + currentChar)
		endIndex = endIndex + 1
		currentChar = view.substr(endIndex)
	
	if (endIndex >= viewSize):
		return ""
	
	fileNameRegion = sublime.Region(startIndex, endIndex)
	fileNameLength = endIndex - startIndex
	fileName = view.substr(fileNameRegion)
	# Enable this to escaped quotes into regular quotes in the result
	# fileName = fileName.replace("\\\"", "\"")
	
	return fileName

class PopupTestCommand(sublime_plugin.TextCommand):
	popupItems = [
	"Open String File", 
	"Kill Word", 
	"Pound Replace",
	"Taylor Command",
	"View Info",
	"My Google Search",
	"Update Custom Types",
	"Custom Types Info",
	"Let's Encrypt",
	"Let's Decrypt",
	"Open Header",
	"Create File Header",
	"Kill Line"]
	
	commandItems = [
	"open_string_file", 
	"kill_word", 
	"pound_replace",
	"taylor",
	"view_info",
	"my_google_search",
	"update_custom_types",
	"list_custom_types",
	"lets_encrypt",
	"lets_decrypt",
	"open_header",
	"create_file_header",
	"kill_line"]
	
	def popupDone(self, selectedIndex):
		# print("Selected " + self.popupItems[selectedIndex] + "!")
		if (selectedIndex != -1):
			print("Running command \"" + self.commandItems[selectedIndex] + "\"")
			self.view.run_command(self.commandItems[selectedIndex])
	
	def run(self, edit):
		self.view.show_popup_menu(self.popupItems, self.popupDone)
	
class TaylorCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		# resources = self.view.window().lookup_symbol_in_index("function")
		# print(str(resources))
		shell_vars = self.view.meta_info("shellVariables", self.view.sel()[0].begin())
		if not shell_vars:
			return ([], [])
		
		# transform the list of dicts into a single dict
		all_vars = {}
		for v in shell_vars:
			if 'name' in v and 'value' in v:
				all_vars[v['name']] = v['value']
		
		print("Shel Vars: " + str(all_vars))

class ViewInfoCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		view = self.view
		
		visibleRegion = view.visible_region()
		print("Visible region: [{}, {}]".format(visibleRegion.begin(), visibleRegion.end()))

class ViewPoundReplaceCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		visibleRegion = self.view.visible_region()
		
		for cIndex in range(visibleRegion.begin(), visibleRegion.end()):
			charRegion = sublime.Region(cIndex, cIndex+1)
			currentChar = self.view.substr(charRegion)
			
			if (currentChar != '\n' and currentChar != '\r' and
				currentChar != '\t' and currentChar != ' '):
				self.view.replace(edit, charRegion, '#')

class PoundReplaceCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		
		for region in self.view.sel():
			
			for cIndex in range(region.begin(), region.end()):
				charRegion = sublime.Region(cIndex, cIndex+1)
				currentChar = self.view.substr(charRegion)
				
				if (currentChar != '\n' and currentChar != '\r' and
					currentChar != '\t' and currentChar != ' '):
					self.view.replace(edit, charRegion, '#')

# This is a simple command that deletes the word(s) your cursor is inside
class KillWordCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		for region in self.view.sel():
			word = self.view.word(region)
			self.view.erase(edit, word)
			
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

def LineIsInclude(view, region):
	matchRegex = "#include"
	matchLength = len(matchRegex)
	lineRegion = view.line(region)
	line = view.substr(lineRegion)
	
	if (len(line) < len(matchRegex) or 
		line[0:matchLength] != matchRegex):
		return False
	
	fileName = GetCString(view, region)
	fileNameLength = len(fileName)
	
	return len(fileName) > 0
	

# This is a simple function that opens the goto window
# with the name of the #include header file that your
# cursor is on already entered into the text box
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

class LetsEncryptCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		for region in self.view.sel():
			for cIndex in range(region.begin(), region.end()):
				currentChar = self.view.substr(cIndex)
				charNum = ord(currentChar)
				charNum += 5
				newChar = chr(charNum)
				replaceRegion = sublime.Region(cIndex, cIndex+1)
				self.view.replace(edit, replaceRegion, newChar)

class LetsDecryptCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		for region in self.view.sel():
			for cIndex in range(region.begin(), region.end()):
				currentChar = self.view.substr(cIndex)
				charNum = ord(currentChar)
				charNum -= 5
				newChar = chr(charNum)
				replaceRegion = sublime.Region(cIndex, cIndex+1)
				self.view.replace(edit, replaceRegion, newChar)

def LineIsEmpty(line):
	matchResult = re.search("^[\\t ]*$", line);
	if (matchResult):
		return True;
	else:
		return False;

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

class InsertNumsHexCommand(sublime_plugin.TextCommand):
	def run(self, edit, start_num=0, padding=2):
		iterator = start_num
		for region in self.view.sel():
			replaceStr = "%X" % iterator
			while (len(replaceStr) < padding):
				replaceStr = "0" + replaceStr
			self.view.replace(edit, region, replaceStr)
			iterator += 1

def ActualLineLength(tabSize, lineStr):
	result = 0
	
	column = 0;
	for cIndex in range(0, len(lineStr)):
		if (lineStr[cIndex] == '\t'):
			actualTabSize = tabSize - (column%tabSize)
			# print("Tab %s" % actualTabSize)
			result += actualTabSize
			column += actualTabSize
		else:
			result += 1
			column += 1
	
	return result

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
				
def IsHexChar(character):
	if (character.lower() >= 'a' and character.lower() <= 'f'):
		return True
	elif (character >= '0' and character <= '9'):
		return True
	else:
		return False

class AsciiToHexCommand(sublime_plugin.TextCommand):
	def run(self, edit, undo=False, add_prefix=False, add_spaces=True):
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
						if (cIndex != 0 and wasNewLine == False and add_spaces):
							replaceStr += " "
						if (add_prefix):
							replaceStr += "0x"
						
						charNum = ord(regionStr[cIndex])
						replaceStr += ("%02X" % charNum)
						
						wasNewLine = False
				
				self.view.replace(edit, region, replaceStr)

def SplitScopesString(scopeString):
	scopes = []
	
	parts = scopeString.split(" ")
	for part in parts:
		scopeName = part.strip()
		if (len(scopeName) == 0):
			continue
		# print("Scope: \"" + scopeName + "\"")
		scopes.append(scopeName)
	
	return scopes

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

class DoNothingCommand(sublime_plugin.TextCommand):
	def run(self):
		print("Doing nothing!")

def TextPointColumn(view, textPoint):
	tabSize = view.settings().get("tab_size")
	lineRegion = view.line(textPoint)
	
	if (lineRegion.size() == 0 or textPoint < lineRegion.begin() or textPoint >= lineRegion.end()):
		return 0
	
	result = 0
	for cIndex in range(0, textPoint-lineRegion.begin()):
		c = view.substr(sublime.Region(lineRegion.begin() + cIndex, lineRegion.begin() + cIndex + 1))
		if (c == "\t"):
			actualTabSize = tabSize - (result%tabSize)
			result += actualTabSize
		else:
			result += 1
	
	return result

def RowColumnTextPoint(view, row, column):
	tabSize = view.settings().get("tab_size")
	lineRegion = view.line(view.text_point(row, 0))
	
	if (column == 0 or lineRegion.size() == 0):
		return lineRegion.begin()
	
	currentCol = 0
	result = lineRegion.begin();
	for cIndex in range(0, lineRegion.size()):
		c = view.substr(sublime.Region(lineRegion.begin() + cIndex, lineRegion.begin() + cIndex + 1))
		if (c == "\t"):
			actualTabSize = tabSize - (currentCol%tabSize)
			currentCol += actualTabSize
		else:
			currentCol += 1
		result += 1
		
		if (currentCol >= column):
			break
	
	return result

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


# class ShowPositionCommand(sublime_plugin.TextCommand):
# 	def run(self, edit, position, buffer_size=5):
# 		row, col = self.view.rowcol(position)
# 		

# H
#          h  Hello