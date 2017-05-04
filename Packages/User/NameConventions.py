import sublime
import sublime_plugin
import re

#TODO: Should we handle getting rid of trailing _t on types?
#TODO: Add options to keep leading and trailing _ and trailing _t

def FullyMatchesRegex(string, regex):
	searchResult = re.search(regex, string)
	if (searchResult.start() != 0):
		# print("start: " + str(searchResult.start()))
		return False
	if (searchResult.end() != len(string)):
		# print("end: " + str(searchResult.end()))
		return False
	
	return True

def IsLower(char):
	return ord(char) >= ord('a') and ord(char) <= ord('z')

def IsUpper(char):
	return ord(char) >= ord('A') and ord(char) <= ord('Z')

def IsLetter(char):
	return IsLower() or IsUpper()

def IsNumber(char):
	return ord(char) >= ord('0') and ord(char) <= ord('9')

def ToUpper(char):
	if (not IsLower(char)):
		return char
	return chr(ord(char) - 32)

def ToLower(char):
	if (not IsUpper(char)):
		return char
	return chr(ord(char) + 32)

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

def UpperFirst(string):
	if (len(string) == 0):
		return string
	
	return ToUpper(string[0]) + string[1:]

class ChangeNamingConventionCommand(sublime_plugin.TextCommand):
	def run(self, edit, convention="upper_first", conserve_prefix=True, conserve_suffix=True):
		for region in self.view.sel():
			originalName = self.view.substr(region)
			if (len(originalName) == 0):
				print("Skipping empty selection")
				continue
			if (not FullyMatchesRegex(originalName, "[A-Za-z_][A-Za-z0-9_]*")):
				print("\"" + originalName + "\" is not a valid identifier")
				continue
			
			prefix = ""
			if (conserve_prefix):
				while(originalName[0] == "_"):
					prefix += "_"
					originalName = originalName[1:]
			suffix = ""
			if (conserve_suffix):
				searchResult = re.search("([_]+[A-Za-z0-9]?)$", originalName)
				if (searchResult):
					suffix = searchResult.group(1);
					originalName = originalName[:searchResult.start()]
			
			print("Current Text: \"" + originalName + "\"")
			print("Prefix: \"" + prefix + "\"")
			print("Suffix: \"" + suffix + "\"")
			
			nameParts = GetNameParts(originalName)
			# print("Parts: " + str(nameParts))
			
			if (len(nameParts) == 0):
				print("No name parts found")
				continue
			
			newName = originalName
			if (convention == "camel_case"):
				newName = nameParts[0]
				for pIndex in range(1, len(nameParts)):
					newName += UpperFirst(nameParts[pIndex])
			elif (convention == "upper_first"):
				newName = ""
				for newPart in nameParts:
					newName += UpperFirst(newPart)
			elif (convention == "lower_all"):
				newName = ""
				for newPart in nameParts:
					newName += newPart
			elif (convention == "lower_underscores"):
				newName = nameParts[0]
				for pIndex in range(1, len(nameParts)):
					newName += "_" + nameParts[pIndex]
			elif (convention == "upper_underscores"):
				newName = nameParts[0].upper()
				for pIndex in range(1, len(nameParts)):
					newName += "_" + nameParts[pIndex].upper()
			else:
				print("Unknown convention type: \"" + convention + "\"")
			
			newName = prefix + newName + suffix
			
			print("New Name: \"" + newName + "\"")
			
			self.view.replace(edit, region, newName)
			
			
			
