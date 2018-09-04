import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

import re
import time

class CreateFileHeaderCommand(sublime_plugin.TextCommand):
#
	def run(self, edit, headerExtensions=[".h", ".hpp"], sourceExtensions=[".c", ".cpp", ".py"], authorName="Taylor Robbins"):
	#
		filePath = self.view.file_name()
		fileFolder, fileName = os.path.split(filePath)
		fileNameNoExt, fileExtension = os.path.splitext(fileName)
		print("fileExtension: " + fileExtension)
		
		dateString = time.strftime("%m\\%d\\%Y")
		
		existingDateRegion = self.view.find("Date\\:\\s*\\d{1,2}\\\\\\d{1,2}\\\\\\d{1,4}", 0)
		if (existingDateRegion != None and existingDateRegion != sublime.Region(-1, -1) and self.view.match_selector(existingDateRegion.begin(), "comment")):
		#
			print("File header already exists. Replacing date");
			self.view.replace(edit, existingDateRegion, "Date:   " + dateString)
			return
		#
		
		fileIsEmpty = True
		lineNum = 0
		cIndex = self.view.text_point(lineNum, 0)
		while (cIndex < self.view.size()):
		#
			lineRegion = self.view.line(cIndex)
			lineStr = self.view.substr(lineRegion)
			if (lineStr != None and LineIsEmpty(lineStr) == False):
			#
				print("File is not empty")
				fileIsEmpty = False
				break
			#
			else:
			#
				lineNum += 1
				cIndex = self.view.text_point(lineNum, 0)
			#
		#
		
		singleCommentStr = GetSingleCommentStr(self.view, 0)
		blockCommentStart, blockCommentEnd = GetBlockCommentStrs(self.view, 0)
		
		headerString = ""
		selectRegion = False
		newRegion = None
		if (fileExtension in headerExtensions):
		#
			headerString += blockCommentStart + "\n"
			headerString += "File:   " + fileName   + "\n"
			headerString += "Author: " + authorName + "\n"
			headerString += "Date:   " + dateString + "\n"
			headerString += blockCommentEnd + "\n"
			headerString += "\n"
			
			if (fileIsEmpty):
			#
				nameParts = GetNameParts(fileNameNoExt)
				print("Name Parts: " + str(nameParts))
				
				defineName = ""
				for part in nameParts:
				#
					defineName += "_" + part.upper()
				#
				defineName += "_" + fileExtension[1:].upper()
				
				headerString += "#ifndef " + defineName + "\n"
				headerString += "#define " + defineName + "\n"
				headerString += "\n"
				selectIndex = len(headerString)
				selectRegion = True
				newRegion = sublime.Region(selectIndex, selectIndex)
				headerString += "\n\n"
				headerString += "#endif " + singleCommentStr + " " + defineName + "\n"
			#
		#
		elif (fileExtension in sourceExtensions):
		#
			headerString += blockCommentStart + "\n"
			headerString += "File:   " + fileName   + "\n"
			headerString += "Author: " + authorName + "\n"
			headerString += "Date:   " + dateString + "\n"
			headerString += "Description: \n"
			headerString += "\t** None \n"
			headerString += blockCommentEnd + "\n\n"
			searchResult = re.search("\t\*\* (None)", headerString)
			newRegion = sublime.Region(searchResult.start(1),searchResult.end(1))
			selectRegion = True
		#
		
		self.view.insert(edit, 0, headerString)
		
		if (selectRegion):
		#
			self.view.sel().clear()
			self.view.sel().add(newRegion)
			self.view.run_command("show_at_center")
		#
	#
#

class CreateLocalHeaderCommand(sublime_plugin.TextCommand):
#
	def run(self, edit, width=32, bold=True):
	#
		for region in self.view.sel():
		#
			selectionStr = self.view.substr(region)
			lineRegion = self.view.line(region.begin())
			indentationStr = self.view.substr(sublime.Region(lineRegion.begin(), region.begin()))
			lineStr = self.view.substr(lineRegion)
			# print("Indentation: \"" + indentationStr + "\"")
			# print("Selection = \"" + selectionStr + "\"")
			
			# NOTE: All the code written here for stripping a header is kinda garbage looking.
			#       It probably needs to be rewritten to make it nicer looking. It seems to work though
			isHeader, contentStr = self.IsHeaderLine(lineStr)
			if (isHeader):
			#
				print("Current line is a header containing \"%s\"" % (contentStr))
				
				targetLine = self.view.rowcol(region.begin())[0]
				# print("targetLine: %d" % (targetLine))
				
				# Check the last line for content if the current one has none
				if (len(contentStr) == 0 and targetLine > 0):
				#
					lastLineRegion = self.view.line(self.view.text_point(targetLine-1, 0))
					lastLineStr = self.view.substr(lastLineRegion)
					# print("lastLineStr = \"%s\"" % (lastLineStr))
					lastLineIsHeader, lastLineContent = self.IsHeaderLine(lastLineStr)
					if (lastLineIsHeader and len(lastLineContent) > 0):
					#
						print("last line is header containing \"%s\"" % (lastLineContent))
						targetLine = targetLine-1
						contentStr = lastLineContent
					#
				#
				
				# Check the next line for content if the current one has none
				if (len(contentStr) == 0 and lineRegion.end() < self.view.size()):
				#
					nextLineRegion = self.view.line(self.view.text_point(targetLine+1, 0))
					nextLineStr = self.view.substr(nextLineRegion)
					# print("nextLineStr = \"%s\"" % (nextLineStr))
					nextLineIsHeader, nextLineContent = self.IsHeaderLine(nextLineStr)
					if (nextLineIsHeader and len(nextLineContent) > 0):
					#
						print("next line is header containing \"%s\"" % (nextLineContent))
						targetLine = targetLine+1
						contentStr = nextLineContent
					#
				#
				
				if (len(contentStr) == 0):
				#
					print("Could not find title line with content")
					continue
				#
				
				print("Target Line: %d containing \"%s\"" % (targetLine, contentStr))
				
				stripResult = self.StripHeader(edit, targetLine)
				
				if (stripResult == True): print("Stripped header successfully")
				else: print("Couldn't strip header")
				
				continue
			#
			else:
			#
				print("\"%s\" is not a header string" % (lineStr))
			#
			
			if (len(selectionStr) == 0): continue
			
			# Pad the string to 32 characters
			
			if (len(selectionStr) >= width - 2):
			#
				selectionStr = " " + selectionStr + " "
				if (len(selectionStr) % 2 != 0):
				#
					selectionStr = selectionStr + " "
				#
			#
			else:
			#
				while (len(selectionStr) < width-2):
				#
					selectionStr = selectionStr + " "
					if (len(selectionStr) < width-2):
					#
						selectionStr = " " + selectionStr
					#
				#
			#
			
			if (selectionStr[0] != " "): selectionStr = " " + selectionStr
			print("SelectionStr = \"%s\"" % (selectionStr))
			
			headerWidth = len(selectionStr)
			headerTopStr = ""
			while (len(headerTopStr) < headerWidth):
			#
				if (bold): headerTopStr += "="
				else: headerTopStr += "-"
			#
			headerTopStr = "+" + headerTopStr + "+"
			
			commentStr = GetSingleCommentStr(self.view, region.begin())
			
			headerString  = commentStr + headerTopStr + "\n" + indentationStr
			headerString += commentStr + "|" + selectionStr + "|" + "\n" + indentationStr
			headerString += commentStr + headerTopStr
			
			self.view.replace(edit, region, headerString);
		#
	#
	
	def IsHeaderLine(self, line):
	#
		headerChars = [ '|', '+', '=', '-' ]
		commentChars = [ '/', '#', '*' ]
		
		headerStr = line
		preceedingStr = ""
		while (len(headerStr) > 0):
		#
			if (IsWhitespace(headerStr[0]) or headerStr[0] in commentChars):
			#
				preceedingStr += headerStr[0]
				headerStr = headerStr[1:]
			#
			elif (headerStr[0] in headerChars):
			#
				break
			#
			else:
			#
				print("Invalid comment char: \'%c\'" % (headerStr[0]))
				return (False, "")
			#
		#
		
		# print("headerStr = \"%s\"" % (headerStr))
		
		if (len(headerStr) < 4):
		#
			print("Too short: \"%s\"" % (headerStr))
			return (False, "")
		#
		if (headerStr[0] not in headerChars): return (False, "")
		if (headerStr[-1] not in headerChars): return (False, "")
		
		allHeaderChars = True
		for cIndex in range(0, len(headerStr)):
		#
			if (headerStr[cIndex] not in headerChars):
			#
				allHeaderChars = False
				break
			#
		#
		
		if (allHeaderChars):
		#
			print("All header chars")
			return (True, "")
		#
		
		if (IsWhitespace(headerStr[1]) == False or IsWhitespace(headerStr[-2]) == False):
		#
			print("No surrounding whitespace")
			return (False, "")
		#
		headerStr = headerStr[1:-1]
		
		while (IsWhitespace(headerStr[0])): headerStr = headerStr[1:]
		while (IsWhitespace(headerStr[-1])): headerStr = headerStr[:-1]
		
		return (True, headerStr)
	#
	
	def StripHeader(self, edit, lineIndex):
	#
		lastLineRegion = self.view.line(self.view.text_point(lineIndex-1, 0))
		currLineRegion = self.view.line(self.view.text_point(lineIndex, 0))
		nextLineRegion = self.view.line(self.view.text_point(lineIndex+1, 0))
		
		lastLineIsHeader, lastLineContent = self.IsHeaderLine(self.view.substr(lastLineRegion))
		currLineIsHeader, currLineContent = self.IsHeaderLine(self.view.substr(currLineRegion))
		nextLineIsHeader, nextLineContent = self.IsHeaderLine(self.view.substr(nextLineRegion))
		
		if (lastLineIsHeader == False or currLineIsHeader == False or nextLineIsHeader == False): return False
		if (len(lastLineContent) > 0 or len(currLineContent) == 0 or len(nextLineContent) > 0): return False
		
		indentationStr = GetLineIndentation(self.view.substr(lastLineRegion))
		
		replaceRegion = sublime.Region(lastLineRegion.begin(), nextLineRegion.end())
		
		self.view.replace(edit, replaceRegion, indentationStr + currLineContent)
		
		selectionStart = replaceRegion.begin() + len(indentationStr)
		self.view.sel().add(sublime.Region(selectionStart, selectionStart + len(currLineContent)))
		
		return True
	#
#


