import os, sys, sublime, sublime_plugin, random
from Taylor.Functions import *

class Color():
#
	def __init__(self):
	#
		self.r = 0
		self.g = 0
		self.b = 0
		self.a = 0xFF
	#
	
	def __repr__(self):
	#
		return ("(%02X, %02X, %02X, %02X)" % (self.r, self.g, self.b, self.a))
	#
	
	def FromHexStrRgba(self, hexStr):
	#
		if (hexStr == None or len(hexStr) < 6 or len(hexStr) > 8): return False
		
		hexValues = ConvertStrToHex(hexStr)
		if (len(hexValues) < 3 or len(hexValues) > 4): return False
		
		self.r = ord(hexValues[0])
		self.g = ord(hexValues[1])
		self.b = ord(hexValues[2])
		if (len(hexValues) >= 4): self.a = ord(hexValues[3])
		else: self.a = 0xFF
		return True
	#
	
	def FromHexStrArgb(self, hexStr):
	#
		if (hexStr == None or (len(hexStr) != 8 and len(hexStr) != 6)): return False
		
		hexValues = ConvertStrToHex(hexStr)
		if (len(hexValues) < 3 or len(hexValues) > 4): return False
		hasAlpha = (len(hexValues) == 4);
		
		if (hasAlpha):
		#
			self.a = ord(hexValues[0])
			self.r = ord(hexValues[1])
			self.g = ord(hexValues[2])
			self.b = ord(hexValues[3])
		#
		else:
		#
			self.a = 255
			self.r = ord(hexValues[0])
			self.g = ord(hexValues[1])
			self.b = ord(hexValues[2])
		#
		return True
	#
	
	def GetHexStrRgba(self):
	#
		return ("%02X%02X%02X%02X" % (self.r, self.g, self.b, self.a))
	#
	
	def GetHexStrArgb(self):
	#
		return ("%02X%02X%02X%02X" % (self.a, self.r, self.g, self.b))
	#
	
	def GetOpposite(self):
	#
		result = Color()
		result.r = ((self.r + 128) % 256)
		result.g = ((self.g + 128) % 256)
		result.b = ((self.b + 128) % 256)
		result.a = self.a
		return result
	#
#

# This function is simply for testing new functionality. It's bound to ctrl+;
class TaylorCommand(sublime_plugin.TextCommand):
#
	def run(self, edit):
	#
		print("Running the Taylor Command!")
		
		print(sys.version);
		
		showPos = 0
		html = ""
		for region in self.view.sel():
		#
			selectionStr = self.view.substr(region)
			# print("Selection: \"" + selectionStr + "\"")
			
			if (len(selectionStr) > 2 and selectionStr[0:2] == "0x"):
			#
				selectionStr = selectionStr[2:]
			#
			
			color = Color()
			if (color.FromHexStrArgb(selectionStr) == False):
			#
				print("Couldn't parse \"%s\" as color" % (selectionStr))
				color.a = 0
			#
			
			html += "<div style='padding:10px 50px;background-color:#" + color.GetHexStrRgba() + ";color:#" + color.GetOpposite().GetHexStrRgba() + "'>"
			html += selectionStr
			html += "</div>"
			
			showPos = region.b
			# self.view.replace(edit, region, newString)
		#
		
		if (html != ""):
		#
			self.view.show_popup(html, 0, showPos, 250, 500)
		#
		
		# addX = random.randint(-100,100);
		# addY = random.randint(-100,100);
		# for region in self.view.sel():
		# #
		# 	selectionStr = self.view.substr(region);
		# 	parts = selectionStr.split(",");
		# 	if (len(parts) != 2): continue;
		# 	xValue = int(parts[0]);
		# 	yValue = int(parts[1]);
		# 	newString = str(xValue + addX) + "," + str(yValue + addY);
		# 	self.view.replace(edit, region, newString);
		# #
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

class PrintScopesCommand(sublime_plugin.TextCommand):
#
	def run(self, edit):
	#
		rIndex = 0;
		for region in self.view.sel():
		#
			scopes = self.view.scope_name(region.end()).split(" ");
			
			print("Selection[%u]:" % rIndex);
			for scope in scopes:
			#
				print("  " + scope);
			#
			rIndex += 1;
		#
	#
#
