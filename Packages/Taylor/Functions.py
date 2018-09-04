# This file contains all of the common functions that my commands might use.
# Any general purpose functions can be placed in here

import os, sys, sublime, sublime_plugin, re

def FullyMatchesRegex(string, regex):
#
	searchResult = re.search(regex, string)
	if (searchResult.start() != 0):
	#
		# print("start: " + str(searchResult.start()))
		return False
	#
	if (searchResult.end() != len(string)):
	#
		# print("end: " + str(searchResult.end()))
		return False
	#
	
	return True
#

def IsWhitespace(char):
#
	if (char == '\t' or char == ' ' or char == '\n' or char == '\r'):
	#
		return True
	#
	else:
	#
		return False
	#
#

def IsLower(char):
#
	return ord(char) >= ord('a') and ord(char) <= ord('z')
#

def IsUpper(char):
#
	return ord(char) >= ord('A') and ord(char) <= ord('Z')
#

def IsLetter(char):
#
	return IsLower() or IsUpper()
#

def IsNumber(char):
#
	return ord(char) >= ord('0') and ord(char) <= ord('9')
#

def ToUpper(char):
#
	if (not IsLower(char)): return char
	return chr(ord(char) - 32)
#

def ToLower(char):
#
	if (not IsUpper(char)): return char
	return chr(ord(char) + 32)
#

def IsIdentChar(char):
#
	if (IsUpper(char) or IsLower(char) or IsNumber(char) or char == '_'):
	#
		return True
	#
	else: return False
#

def GetNameParts(name):
#
	parts = []
	currIndex = 0
	lastIndex = 0
	lastCharWasUpper = False
	lastCharWasNumber = False
	while (currIndex < len(name)):
	#
		char = name[currIndex]
		if (IsUpper(char) and not lastCharWasUpper):
		#
			if (currIndex > lastIndex):
			#
				newPart = name[lastIndex:currIndex].lower()
				# print("Part: \"" + newPart + "\"")
				parts.append(newPart)
			#
			lastIndex = currIndex
		#
		elif (IsNumber(char) and not lastCharWasNumber):
		#
			if (currIndex > lastIndex):
			#
				newPart = name[lastIndex:currIndex].lower()
				# print("Part: \"" + newPart + "\"")
				parts.append(newPart)
			#
			lastIndex = currIndex
		#
		elif (char == '_' or char == ' '):
		#
			if (currIndex > lastIndex):
			#
				newPart = name[lastIndex:currIndex].lower()
				# print("Part: \"" + newPart + "\"")
				parts.append(newPart)
			#
			lastIndex = currIndex+1
		#
		
		lastCharWasUpper = (ord(char) >= ord('A') and ord(char) <= ord('Z'))
		lastCharWasNumber = (ord(char) >= ord('0') and ord(char) <= ord('9'))
		currIndex += 1
	#
	
	if (currIndex > lastIndex):
	#
		newPart = name[lastIndex:currIndex].lower()
		# print("Part: \"" + newPart + "\"")
		parts.append(newPart)
	#
	
	return parts
#

def UpperFirst(string):
#
	if (len(string) == 0): return string
	return ToUpper(string[0]) + string[1:]
#

def LineIsEmpty(line):
#
	matchResult = re.search("^[\\t ]*$", line);
	if (matchResult): return True;
	else: return False;
#

def GetCString(view, region):
#
	startIndex = region.begin()
	endIndex = region.end()
	viewSize = view.size()
	
	if (startIndex == 0): return "";
	
	# Step back till we find the (non-escaped) quotation mark or the beginning of line/file
	currentChar = view.substr(startIndex-1)
	while (startIndex > 0):
	#
		if (currentChar == '\"' and (startIndex <= 0 or view.substr(startIndex-2) != "\\")):
		#
			break
		#
		if (currentChar == '\n' or currentChar == '\r'):
		#
			# startIndex = startIndex + 1
			return ""
		#
		if (currentChar == '<'):
		#
			break
		#
		if (endIndex - startIndex > 256):
		#
			break
		#
		# print("<" + currentChar)
		startIndex = startIndex - 1
		currentChar = view.substr(startIndex-1)
	#
	
	if (startIndex == 0): return "";
	
	# Step forward till we find the (non-escaped) quotation mark or the end of line/file
	currentChar = view.substr(endIndex)
	while (endIndex < viewSize):
	#
		if (currentChar == '\"' and (endIndex <= 0 or view.substr(endIndex-1) != "\\")):
		#
			break
		#
		if (currentChar == '\n' or currentChar == '\r'):
		#
			return ""
		#
		if (currentChar == '>'):
		#
			break;
		#
		if (endIndex - startIndex > 256):
		#
			break
		#
		# print(">" + currentChar)
		endIndex = endIndex + 1
		currentChar = view.substr(endIndex)
	#
	
	if (endIndex >= viewSize): return ""
	
	fileNameRegion = sublime.Region(startIndex, endIndex)
	fileNameLength = endIndex - startIndex
	fileName = view.substr(fileNameRegion)
	# Enable this to escaped quotes into regular quotes in the result
	# fileName = fileName.replace("\\\"", "\"")
	
	return fileName
#

def LineIsInclude(view, region):
#
	matchRegex = "#include"
	matchLength = len(matchRegex)
	lineRegion = view.line(region)
	line = view.substr(lineRegion)
	
	if (len(line) < len(matchRegex) or 
		line[0:matchLength] != matchRegex):
	#
		return False
	#
	
	fileName = GetCString(view, region)
	fileNameLength = len(fileName)
	
	return len(fileName) > 0
#

def ActualLineLength(tabSize, lineStr):
#
	result = 0
	
	column = 0;
	for cIndex in range(0, len(lineStr)):
	#
		if (lineStr[cIndex] == '\t'):
		#
			actualTabSize = tabSize - (column%tabSize)
			# print("Tab %s" % actualTabSize)
			result += actualTabSize
			column += actualTabSize
		#
		else:
		#
			result += 1
			column += 1
		#
	#
	
	return result
#

def IsHexChar(character):
#
	if (character.lower() >= 'a' and character.lower() <= 'f'):
	#
		return True
	#
	elif (character >= '0' and character <= '9'):
	#
		return True
	#
	else: return False
#

def GetHexCharValue(character):
#
	if (ord(character) >= ord('A') and ord(character) <= ord('F')):
	#
		return 10 + (ord(character) - ord('A'))
	#
	elif (ord(character) >= ord('a') and ord(character) <= ord('f')):
	#
		return 10 + (ord(character) - ord('a'))
	#
	elif (ord(character) >= ord('0') and ord(character) <= ord('9')):
	#
		return ord(character) - ord('0')
	#
	else:
	#
		return 0
	#
#

def GetHexCharsValue(upperChar, lowerChar):
#
	return (GetHexCharValue(upperChar) << 4) + GetHexCharValue(lowerChar)
#

def ConvertStrToHex(inputStr):
#
	result = ""
	for cIndex in range(0, len(inputStr), 2):
	#
		if (cIndex+1 >= len(inputStr)): break
		if (IsHexChar(inputStr[cIndex + 0]) and IsHexChar(inputStr[cIndex + 1])):
		#
			newByte = GetHexCharsValue(inputStr[cIndex + 0], inputStr[cIndex + 1])
			result += chr(newByte)
		#
	#
	return result
#

def SplitScopesString(scopeString):
#
	scopes = []
	
	parts = scopeString.split(" ")
	for part in parts:
	#
		scopeName = part.strip()
		if (len(scopeName) == 0): continue
		# print("Scope: \"" + scopeName + "\"")
		scopes.append(scopeName)
	#
	
	return scopes
#

def TextPointColumn(view, textPoint):
#
	tabSize = view.settings().get("tab_size")
	lineRegion = view.line(textPoint)
	
	if (lineRegion.size() == 0 or textPoint < lineRegion.begin() or textPoint >= lineRegion.end()):
	#
		return 0
	#
	
	result = 0
	for cIndex in range(0, textPoint-lineRegion.begin()):
	#
		c = view.substr(sublime.Region(lineRegion.begin() + cIndex, lineRegion.begin() + cIndex + 1))
		if (c == "\t"):
		#
			actualTabSize = tabSize - (result%tabSize)
			result += actualTabSize
		#
		else:
		#
			result += 1
		#
	#
	
	return result
#

def RowColumnTextPoint(view, row, column):
#
	tabSize = view.settings().get("tab_size")
	lineRegion = view.line(view.text_point(row, 0))
	
	if (column == 0 or lineRegion.size() == 0):
	#
		return lineRegion.begin()
	#
	
	currentCol = 0
	result = lineRegion.begin();
	for cIndex in range(0, lineRegion.size()):
	#
		c = view.substr(sublime.Region(lineRegion.begin() + cIndex, lineRegion.begin() + cIndex + 1))
		if (c == "\t"):
		#
			actualTabSize = tabSize - (currentCol%tabSize)
			currentCol += actualTabSize
		#
		else:
		#
			currentCol += 1
		#
		result += 1
		
		if (currentCol >= column): break
	#
	
	return result
#

def GetLineIndentation(lineStr):
#
	result = ""
	
	for cIndex in range(len(lineStr)):
	#
		if (lineStr[cIndex] =='\t' or lineStr[cIndex] == ' '):
		#
			result += lineStr[cIndex]
		#
		else: break
	#
	
	return result
#

class LexicalPiece():
#
	def __init__(self):
	#
		self.type = "Empty"
		self.value = ""
	#
	
	def __str__(self):
	#
		return "LexicalPiece(%s \"%s\")" % (self.type, self.value)
	#
	
	def __repr__(self):
	#
		if   (self.type == "Syntax"):     return "%s" % self.value
		elif (self.type == "Identifier"): return "\"%s\"" % self.value
		else: return "[%s]" % self.value
	#
#

def LexicalParse(inputStr):
#
	results = []
	lastSyntaxChar = 0
	
	for cIndex in range(0, len(inputStr)+1):
	#
		c = " "
		if (cIndex < len(inputStr)):
		#
			c = inputStr[cIndex]
		#
		
		if (IsIdentChar(c)):
		#
			pass # print("I:", c)
		#
		else:
		#
			newPartStr = inputStr[lastSyntaxChar:cIndex]
			
			if (len(newPartStr) > 0):
			#
				newPiece = LexicalPiece()
				newPiece.type = "Identifier"
				newPiece.value = newPartStr
				results.append(newPiece)
				# print("Piece:", newPiece)
			#
			
			if (IsWhitespace(c) == False):
			#
				syntaxPiece = LexicalPiece()
				syntaxPiece.type = "Syntax"
				syntaxPiece.value = c
				results.append(syntaxPiece)
				# print("S: \'%c\'" % c)
			#
			
			lastSyntaxChar = cIndex+1
		#
	#
	
	return results
#

def StringifyLexicalPieces(pieces):
#
	result = ""
	
	wasSyntax = True
	for piece in pieces:
	#
		if (piece.type == "Syntax"):
		#
			result += piece.value
			wasSyntax = True
		#
		elif (piece.type == "Identifier"):
		#
			if (wasSyntax == False): result += " "
			result += piece.value
			wasSyntax = False
		#
		else:
		#
			print("Unknown piece type: %s" % (piece.type))
		#
	#
	
	return result
#

class CppFunction():
#
	def __init__(self):
	#
		self.valid = False
		self.fullStr = ""
		self.name = ""
		self.returnType = ""
		self.parameterTypes = []
		self.parametersOptional = []
		self.parameters = []
		self.lexicalPieces = []
	#
	
	def __init__(self, functionStr):
	#
		self.valid = False
		self.fullStr = functionStr
		self.name = ""
		self.returnType = ""
		self.parameterTypes = []
		self.parametersOptional = []
		self.parameters = []
		self.lexicalPieces = []
		
		self.NewTryParse(functionStr)
	#
	
	def __repr__(self):
	#
		if (self.valid):
		#
			result = "%s %s(" % (self.returnType, self.name)
			paramStr = ""
			for pIndex in range(0, len(self.parameters)):
			#
				paramName = self.parameters[pIndex]
				paramType = self.parameters[pIndex]
				if (paramStr != ""): paramStr += ", "
				if (paramType != ""): paramStr += paramType
				paramStr += paramName
			#
			result += paramStr + ")"
			return result
		#
		else: return "Invalid CppFunction"
	#
	
	def NewTryParse(self, functionStr):
	#
		self.valid = True
		self.name = ""
		self.returnType = ""
		self.parameterTypes = []
		self.parametersOptional = []
		self.parameters = []
		functionStr = functionStr.replace("...", "args")
		self.lexicalPieces = LexicalParse(functionStr)
		# print("Lexical Pieces:", self.lexicalPieces)
		
		if (len(self.lexicalPieces) == 0):
		#
			print("No lexical pieces found")
			self.valid = False
			return False
		#
		
		beforeParenPieces = []
		parameterPieceLists = []
		
		foundOpenParens = False
		foundCloseParens = False
		newParamPieces = []
		for piece in self.lexicalPieces:
		#
			if (piece.type == "Syntax" and piece.value == "("):
			#
				if (foundOpenParens):
				#
					print("Found more than one open parenthesis!")
					self.valid = False
					return False
				#
				elif (foundCloseParens):
				#
					print("Found open parenthesis after close parenthesis!")
					self.valid = False
					return False
				#
				else:
				#
					foundOpenParens = True
				#
			#
			elif (piece.type == "Syntax" and piece.value == ")"):
			#
				if (foundCloseParens):
				#
					print("Found more than one close parenthesis!")
					self.valid = False
					return False
				#
				elif (foundOpenParens == False):
				#
					print("Found close parenthesis before open parenthesis!")
					self.valid = False
					return False
				#
				else:
				#
					foundCloseParens = True
					if (len(newParamPieces) > 0):
					#
						parameterPieceLists.append(newParamPieces)
						newParamPieces = []
					#
				#
			#
			elif (piece.type == "Syntax" and piece.value == ","):
			#
				if (foundOpenParens == False):
				#
					print("Found comma before open parenthesis")
					self.valid = False
					return False
				#
				elif (foundCloseParens):
				#
					print("Found comma after close parenthesis")
					self.valid = False
					return False
				#
				else:
				#
					if (len(newParamPieces) > 0):
					#
						parameterPieceLists.append(newParamPieces)
						newParamPieces = []
					#
				#
			#
			else:
			#
				if (foundOpenParens == False):
				#
					beforeParenPieces.append(piece)
				#
				elif (foundCloseParens == False):
				#
					newParamPieces.append(piece)
				#
				else:
				#
					pass # print("Ignoring part after close parnthesis: %s" % (piece))
				#
			#
		#
		
		if (foundOpenParens == False):
		#
			print("No open parenthesis found")
			self.valid = False
			return False
		#
		elif (foundCloseParens == False):
		#
			print("Found open parenthesis with no close parenthesis")
			self.valid = False
			return False
		#
		
		# print("Found %u pieces before parenthesis:" % (len(beforeParenPieces)))
		# for piece in beforeParenPieces: print("\t", piece)
		# print("Found %u parameters:" % (len(parameterPieceLists)))
		# for parameterPieces in parameterPieceLists:
		# #
		# 	print("\t%u Parts:" % (len(parameterPieces)))
		# 	for piece in parameterPieces: print("\t\t", piece)
		# #
		
		# We need to parse the function name and return type
		if (len(beforeParenPieces) == 0):
		#
			print("No lexical pieces before open parenthesis")
			self.valid = False
			return False
		#
		elif (beforeParenPieces[-1].type == "Syntax"):
		#
			print("Found syntax, not function name, before parenthesis: %s" % (beforeParenPieces[-1]))
			self.valid = False
			return False
		#
		elif (len(beforeParenPieces) == 1):
		#
			print("Warning: No function return type found")
			self.name = beforeParenPieces[0].value
			self.returnType = ""
		#
		else:
		#
			self.returnType = StringifyLexicalPieces(beforeParenPieces[0:-1])
			self.name = beforeParenPieces[-1].value
		#
		
		# Now we need to parse each parameter piece list
		
		for pIndex in range(0, len(parameterPieceLists)):
		#
			pieceList = parameterPieceLists[pIndex]
			if (len(pieceList) == 0):
			#
				print("Parameter[%u] has no pieces" % (pIndex))
				self.valid = False
				return False
			#
			elif (len(pieceList) == 1 and pieceList[0].type == "Syntax"):
			#
				print("Parameter[%u] ended in Syntax piece, not Identifier" % (pIndex))
				self.valid = False
				return False
			#
			elif (len(pieceList) == 1):
			#
				# print("Warning: No type for parameter[%u]" % (pIndex))
				self.parameterTypes.append("")
				self.parametersOptional.append(False)
				self.parameters.append(pieceList[0].value)
			#
			else:
			#
				beforeEquals = []
				afterEquals = []
				containsEquals = False
				for piece in pieceList:
				#
					if (piece.type == "Syntax" and piece.value == "="):
					#
						if (containsEquals == False):
						#
							containsEquals = True
						#
						else:
						#
							print("Found more than one equals in parameter[%u]" % (pIndex))
							self.valid = False
							return False
						#
					#
					else:
					#
						if (containsEquals): afterEquals.append(piece)
						else:               beforeEquals.append(piece)
					#
				#
				
				if (len(beforeEquals) == 0):
				#
					print("No items found before = in parameter[%u]" % (pIndex))
					self.valid = False
					return False
				#
				elif (beforeEquals[-1].type == "Syntax"):
				#
					print("Expected parameter name, not Syntax, before = in parameter[%u]" % (pIndex))
					self.valid = False
					return False
				#
				elif (containsEquals and len(afterEquals) == 0):
				#
					print("Expected assignment after = in parameter[%u]" % (pIndex))
					self.valid = False
					return False
				#
				elif (len(beforeEquals) == 1):
				#
					print("Warning: No type for parameter[%u]" % (pIndex))
					self.parameterTypes.append("")
					self.parametersOptional.append(containsEquals)
					self.parameters.append(beforeEquals[0].value)
				#
				else:
				#
					self.parameterTypes.append(StringifyLexicalPieces(beforeEquals[0:-1]))
					self.parametersOptional.append(containsEquals)
					self.parameters.append(beforeEquals[-1].value)
				#
			#
		#
	#
#end of CppFunction class

class TestCppParseCommand(sublime_plugin.TextCommand):
#
	def run(self, edit):
	#
		for region in self.view.sel():
		#
			regionStr =  self.view.substr(region)
			print("Attempting to parse \"%s\"" % (regionStr))
			
			parsedFunction = CppFunction(regionStr)
			
			if (parsedFunction.valid):
			#
				print("Function:")
				print("\tName: %s" % (parsedFunction.name))
				print("\tReturn Type: %s" % (parsedFunction.returnType))
				print("\tParameters: %u" % (len(parsedFunction.parameters)))
				for pIndex in range(0, len(parsedFunction.parameters)):
				#
					optionalStr = ""
					if (parsedFunction.parametersOptional[pIndex]): optionalStr = " (Optional)"
					print("\t\t[%u] %s - %s%s" % (pIndex, parsedFunction.parameterTypes[pIndex], parsedFunction.parameters[pIndex], optionalStr))
				#
			#
			else:
			#
				print("Could not parse as function")
			#
		#
	#
#

def StringIsValidType(typeString):
#
	if (typeString == None):
	#
		return False
	#
	
	typeStringLength = len(typeString)
	
	searchResult = re.search("[A-Za-z0-9_]+", typeString)
	
	if (searchResult == None or
		searchResult.start() != 0 or 
		searchResult.end() != typeStringLength):
	#
		return False
	#
	
	return True
#

def GetProjectSettings(window):
#
	projectData = window.project_data()
	if (projectData == None): return None
	
	if ("settings" not in projectData): projectData["settings"] = {}
	if ("build_options"    not in projectData["settings"]): projectData["settings"]["build_options"]    = []
	if ("custom_types"     not in projectData["settings"]): projectData["settings"]["custom_types"]     = []
	if ("custom_constants" not in projectData["settings"]): projectData["settings"]["custom_constants"] = []
	if ("custom_globals"   not in projectData["settings"]): projectData["settings"]["custom_globals"]   = []
	if ("custom_functions" not in projectData["settings"]): projectData["settings"]["custom_functions"] = []
	
	return projectData["settings"]
#

def SaveProjectSettings(window, newSettings):
#
	projectData = window.project_data()
	projectData["settings"] = newSettings
	window.set_project_data(projectData)
#

def RemoveItemsFromList(target, itemsToRemove):
#
	result = target
	for item in itemsToRemove:
	#
		if (item in result): result.remove(item)
	#
	return result

def RemoveFunctionsFromList(target, functionsToRemove):
#
	result = target
	for removeFunction in functionsToRemove:
	#
		removeParsedFunction = CppFunction(removeFunction)
		if (removeParsedFunction.valid):
		#
			foundMatch = False
			matchFunctionStr = ""
			for functionStr in result:
			#
				parsedFunction = CppFunction(functionStr)
				if (parsedFunction.valid and parsedFunction.name == removeParsedFunction.name):
				#
					foundMatch = True
					matchFunctionStr = functionStr
					break
				#
			#
			
			if (foundMatch):
			#
				result.remove(matchFunctionStr)
			#
		#
	#
	return result
#

def ModifySyntaxFileRegexList(filename, searchRegex, newList):
#
	# Read the current fileContents
	file = open(filename, "r")
	if (file == None):
	#
		print("Couldn't open syntax file for reading")
		return False
	#
	fileContents = file.read()
	file.close()
	
	searchResult = re.search(searchRegex, fileContents)
	
	if (searchResult == None or len(searchResult.groups()) < 1):
	#
		print("Couldn't find custom_types in sublime-syntax file")
		return False
	#
	
	newTypeListStr = "|".join(newList)
	
	if (newTypeListStr == searchResult.group(1)):
	#
		print("Syntax regex list is already up to date")
		return True
	#
	
	# Replace the old value in the file with our new list
	fileContents = fileContents[:searchResult.start(1)] + newTypeListStr + fileContents[searchResult.end(1):]
	
	# Write the new fileContents
	file = open(filename, 'w')
	if (file == None):
	#
		print("Couldn't open syntax file for writing")
		return False
	#
	file.write(fileContents)
	file.close()
	
	return True
#

def GetSingleCommentStr(view, viewPos):
#
	result = "// "
	metaInfo = view.meta_info("shellVariables", viewPos)
	if (metaInfo != None):
	#
		for item in metaInfo:
		#
			if ('name' in item and 'value' in item and item['name'] == "TM_COMMENT_START"):
			#
				result = item['value']
				break
			#
		#
	#
	
	return result
#

def GetBlockCommentStrs(view, viewPos):
#
	startStr = ""
	endStr = ""
	metaInfo = view.meta_info("shellVariables", viewPos)
	if (metaInfo != None):
	#
		for item in metaInfo:
		#
			if ('name' in item and 'value' in item and item['name'] == "TM_COMMENT_START_2"):
			#
				startStr = item['value']
			#
			if ('name' in item and 'value' in item and item['name'] == "TM_COMMENT_END_2"):
			#
				endStr = item['value']
			#
		#
	#
	
	return startStr, endStr
#

def PositionIsFolded(view, viewPos):
#
	if (viewPos >= view.size()): return False
	region = sublime.Region(viewPos, viewPos+1)
	foldResult = view.fold(region)
	if (foldResult): view.unfold(region)
	return (foldResult == False); 
#

def FillDollarVariables(varString, valueDictionary):
#
	result = ""
	
	cIndex = 0
	while (cIndex < len(varString)):
	#
		if (varString[cIndex] == "$"):
		#
			foundMatch = False
			matchName = ""
			matchValue = ""
			for vName, value in valueDictionary.items():
			#
				if (cIndex + len(vName) <= len(varString) and
					varString[cIndex+1:cIndex+1+len(vName)] == vName):
				#
					if (len(vName) > len(matchName)):
					#
						foundMatch = True
						matchName = vName
						matchValue = value
					#
				#
			#
			
			if (foundMatch):
			#
				# print("Replaced $%s with \"%s\"" % (matchName, matchValue))
				result += matchValue
				cIndex += 1 + len(matchName)
			#
			else:
			#
				result += varString[cIndex]
				cIndex += 1
			#
		#
		else:
		#
			result += varString[cIndex]
			cIndex += 1
		#
	#
	
	return result
#

#Returns fullPath, directory, fileName, baseName, and extension
def SafeSplitPath(pathStr):
#
	if (pathStr == None or len(pathStr) == 0):
	#
		return "", "", "", "", ""
	#
	
	directory, fileName = os.path.split(pathStr)
	baseName, extension = os.path.splitext(fileName)
	
	if (extension != None and len(extension) > 0 and extension[0] == "."):
	#
		extension = extension[1:]
	#
	
	return pathStr, directory, fileName, baseName, extension
#

def FormattedDictionaryStr(dictionary):
#
	orderedKeys = []
	for key, value in dictionary.items(): orderedKeys.append(key)
	orderedKeys.sort()
	
	result = "{\n"
	for key in orderedKeys:
	#
		result += "\t" + str(key) + ": " + str(dictionary[key]) + "\n"
	#
	result += "}"
	return result
#

def FindBeginOfLineAfterIndents(view, region):
#
	result = region.begin()
	while (result < view.size() and result < region.end()):
	#
		c = view.substr(result)
		if (c == '\t' or c == ' '): result += 1
		else: break
	#
	return result
#

def FindEndOfLineBeforeComments(view, region):
#
	result = region.end()
	while (result > 0 and result > region.begin()):
	#
		scopeNames = view.scope_name(result-1).split(" ")
		isComment = False
		for scope in scopeNames:
		#
			scopeParts = scope.split(".")
			if (len(scopeParts) > 0 and scopeParts[0] == "comment"):
			#
				isComment = True
				break
			#
		#
		if (isComment): result -= 1
		else:
		#
			c = view.substr(result-1)
			if (c == ' ' or c == '\t'): result -= 1
			else: break
		#
	#
	return result
#

