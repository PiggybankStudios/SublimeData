# This file contains all of the common functions that my commands might use.
# Any general purpose functions can be placed in here

def FullyMatchesRegex(string, regex):
	searchResult = re.search(regex, string)
	if (searchResult.start() != 0):
		# print("start: " + str(searchResult.start()))
		return False
	if (searchResult.end() != len(string)):
		# print("end: " + str(searchResult.end()))
		return False
	
	return True
#End

def IsLower(char):
	return ord(char) >= ord('a') and ord(char) <= ord('z')
#End

def IsUpper(char):
	return ord(char) >= ord('A') and ord(char) <= ord('Z')
#End

def IsLetter(char):
	return IsLower() or IsUpper()
#End

def IsNumber(char):
	return ord(char) >= ord('0') and ord(char) <= ord('9')
#End

def ToUpper(char):
	if (not IsLower(char)):
		return char
	return chr(ord(char) - 32)
#End

def ToLower(char):
	if (not IsUpper(char)):
		return char
	return chr(ord(char) + 32)
#End

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
		elif (char == '_' or char == ' '):
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
#End

def UpperFirst(string):
	if (len(string) == 0):
		return string
	
	return ToUpper(string[0]) + string[1:]
#End

def LineIsEmpty(line):
	matchResult = re.search("^[\\t ]*$", line);
	if (matchResult):
		return True;
	else:
		return False;
#End

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
#End

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
#End

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
#End
			
def IsHexChar(character):
	if (character.lower() >= 'a' and character.lower() <= 'f'):
		return True
	elif (character >= '0' and character <= '9'):
		return True
	else:
		return False
#End

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
#End

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
#End

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
#End

def GetLineIndentation(lineStr):
	result = ""
	
	for cIndex in range(len(lineStr)):
		if (lineStr[cIndex] =='\t' or lineStr[cIndex] == ' '):
			result += lineStr[cIndex]
		else:
			break
	
	return result
#End
