import sublime
import sublime_plugin
import os
import re
import time

def IsLower(char):
	return ord(char) >= ord('a') and ord(char) <= ord('z')

def IsUpper(char):
	return ord(char) >= ord('A') and ord(char) <= ord('Z')

def IsLetter(char):
	return IsLower() or IsUpper()

def IsNumber(char):
	return ord(char) >= ord('0') and ord(char) <= ord('9')

def GetNameParts(name):
	parts = []
	currIndex = 0
	lastIndex = 0
	lastCharWasUpper = False
	lastCharWasNumber = False
	while (currIndex < len(name)):
		char = name[currIndex]
		if (IsUpper(char) and not lastCharWasUpper):
			if (currIndex > lastIndex):
				newPart = name[lastIndex:currIndex].lower()
				# print("Part: \"" + newPart + "\"")
				parts.append(newPart)
			lastIndex = currIndex
		elif (IsNumber(char) and not lastCharWasNumber):
			if (currIndex > lastIndex):
				newPart = name[lastIndex:currIndex].lower()
				# print("Part: \"" + newPart + "\"")
				parts.append(newPart)
			lastIndex = currIndex
		elif (char == '_'):
			if (currIndex > lastIndex):
				newPart = name[lastIndex:currIndex].lower()
				# print("Part: \"" + newPart + "\"")
				parts.append(newPart)
			lastIndex = currIndex+1
		
		lastCharWasUpper = (ord(char) >= ord('A') and ord(char) <= ord('Z'))
		lastCharWasNumber = (ord(char) >= ord('0') and ord(char) <= ord('9'))
		currIndex += 1
	
	if (currIndex > lastIndex):
		newPart = name[lastIndex:currIndex].lower()
		# print("Part: \"" + newPart + "\"")
		parts.append(newPart)
	
	return parts

def LineIsEmpty(line):
	matchResult = re.search("^[\\t ]*$", line);
	if (matchResult):
		return True;
	else:
		return False;

class CreateFileHeaderCommand(sublime_plugin.TextCommand):
	def run(self, edit, headerExtensions=[".h", ".hpp"], sourceExtensions=[".c", ".cpp", ".py"], authorName="Taylor Robbins"):
		filePath = self.view.file_name()
		fileFolder, fileName = os.path.split(filePath)
		fileNameNoExt, fileExtension = os.path.splitext(fileName)
		print("fileExtension: " + fileExtension)
		
		dateString = time.strftime("%m\\%d\\%Y")
		
		fileIsEmpty = True
		lineNum = 0
		cIndex = self.view.text_point(lineNum, 0)
		while (cIndex < self.view.size()):
			lineRegion = self.view.line(cIndex)
			lineStr = self.view.substr(lineRegion)
			if (lineStr != None and LineIsEmpty(lineStr) == False):
				print("File is not empty")
				fileIsEmpty = False
				break
			else:
				lineNum += 1
				cIndex = self.view.text_point(lineNum, 0)
		
		singleCommentStr = "//"
		blockCommentStart = "/*"
		blockCommentEnd = "*/"
		
		headerString = ""
		selectRegion = False
		newRegion = None
		if (fileExtension in headerExtensions):
			headerString += blockCommentStart + "\n"
			headerString += "File:   " + fileName   + "\n"
			headerString += "Author: " + authorName + "\n"
			headerString += "Date:   " + dateString + "\n"
			headerString += blockCommentEnd + "\n"
			headerString += "\n"
			
			if (fileIsEmpty):
				nameParts = GetNameParts(fileNameNoExt)
				print("Name Parts: " + str(nameParts))
				
				defineName = ""
				for part in nameParts:
					defineName += "_" + part.upper()
				defineName += "_" + fileExtension[1:].upper()
				
				headerString += "#ifndef " + defineName + "\n"
				headerString += "#define " + defineName + "\n"
				headerString += "\n"
				selectIndex = len(headerString)
				selectRegion = True
				newRegion = sublime.Region(selectIndex, selectIndex)
				headerString += "\n\n"
				headerString += "#endif " + singleCommentStr + " " + defineName + "\n"
		
		elif (fileExtension in sourceExtensions):
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
		
		self.view.insert(edit, 0, headerString)
		
		if (selectRegion):
			self.view.sel().clear()
			self.view.sel().add(newRegion)
			self.view.run_command("show_at_center")

class CreateLocalHeaderCommand(sublime_plugin.TextCommand):
	def run(self, edit, width=32, bold=True):
		for region in self.view.sel():
			selectionStr = self.view.substr(region)
			if (len(selectionStr) == 0):
				continue
			lineRegion = self.view.line(region.begin())
			indentationStr = self.view.substr(sublime.Region(lineRegion.begin(), region.begin()))
			# print("Indentation: \"" + indentationStr + "\"")
			# print("Selection = \"" + selectionStr + "\"")
			
			# Pad the string to 32 characters
			while (len(selectionStr) < width - 2):
				selectionStr = selectionStr + " "
				if (len(selectionStr) < width):
					selectionStr = " " + selectionStr
			
			if (len(selectionStr) >= width - 2):
				selectionStr = " " + selectionStr + " "
				if (len(selectionStr) % 2 != 0):
					selectionStr = selectionStr + " "
			
			headerWidth = len(selectionStr)
			headerTopStr = ""
			while (len(headerTopStr) < headerWidth):
				if (bold):
					headerTopStr += "="
				else:
					headerTopStr += "-"
			headerTopStr = "+" + headerTopStr + "+"
			
			commentStr = "// "
			metaInfo = self.view.meta_info("shellVariables", region.begin())
			if (metaInfo != None):
				for item in metaInfo:
					if ('name' in item and 'value' in item and item['name'] == "TM_COMMENT_START"):
						commentStr = item['value']
						break
			
			headerString  = commentStr + headerTopStr + "\n" + indentationStr
			headerString += commentStr + "|" + selectionStr + "|" + "\n" + indentationStr
			headerString += commentStr + headerTopStr
			
			self.view.replace(edit, region, headerString);


