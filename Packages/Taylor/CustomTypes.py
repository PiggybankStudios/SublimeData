import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

import re

# TODO: Move reading and writing of project settings into their own functions

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
	

class CustomIdentifierCommand(sublime_plugin.TextCommand):
#
	def run(self, edit, action="add", mode="Type", update_syntax_file=True):
	#
		if (action != "add" and action != "remove" and action != "list"):
		#
			print("\"%s\" is not a valid action for AddCustomIdentifierCommand" % (action))
		#
		if (mode != "Type" and mode != "Constant" and mode != "Global" and mode != "Function"):
		#
			print("\"%s\" is not a valid mode for AddCustomIdentifierCommand" % (mode))
			return
		#
		
		targetListName  = "custom_" + mode.lower() + "s"
		projectSettings = GetProjectSettings(self.view.window())
		if (projectSettings == None):
		#
			print("No project data found!")
			return
		#
		
		newIdentifiers = []
		for region in self.view.sel():
		#
			regionStr = self.view.substr(region)
			if (len(regionStr) > 0):
			#
				if (mode == "Function"):
				#
					parsedFunction = CppFunction(regionStr)
					if (parsedFunction.valid):
					#
						foundFunctionStr = ""
						foundMatch = False
						foundIndex = 0
						for functionStr in projectSettings["custom_functions"]:
						#
							function = CppFunction(functionStr)
							if (function.valid and function.name == parsedFunction.name):
							#
								foundFunctionStr = functionStr
								foundMatch = True
								break
							#
							foundIndex += 1
						#
						
						if (foundMatch):
						#
							if (action == "add"):
							#
								if (regionStr == foundFunctionStr): print("\"%s\" already in the function list as \"%s\"" % (parsedFunction.name, foundFunctionStr))
								else:
								#
									print("Replacing existing Custom Function \"%s\" with new definition \"%s\"" % (foundFunctionStr, regionStr))
									projectSettings["custom_functions"].pop(foundIndex)
									newIdentifiers.append(regionStr)
								#
							#
							elif (action == "remove"):
							#
								newIdentifiers.append(regionStr)
							#
						#
						else:
						#
							if (action == "add"):
							#
								newIdentifiers.append(regionStr)
							#
							elif (action == "remove"): print("\"%s\" is not a Custom Function" % (parsedFunction.name))
						#
					#
					else:
					#
						print("\"%s\" is not a parseable function" % (regionStr))
					#
				#
				else:
				#
					if (StringIsValidType(regionStr)):
					#
						if (regionStr in projectSettings[targetListName]):
						#
							if (action == "add"): print("\"%s\" is already a Custom %s" % (regionStr, mode))
							elif (action == "remove"):
							#
								newIdentifiers.append(regionStr)
							#
						#
						else:
						#
							if (action == "add"):
							#
								newIdentifiers.append(regionStr)
							#
							elif (action == "remove"): print("\"%s\" is not a Custom %s" % (regionStr, mode))
						#
					#
					else:
					#
						print("\"%s\" is not a valid identifier!" % (regionStr))
					#
				#
			#
			else:
			#
				print("Ignoring blank selection")
			#
		#
		
		if (len(newIdentifiers) == 0):
			print("No new %ss found" % (mode))
			return
		
		print("Going to %s %u Custom %s(s):" % (action, len(newIdentifiers), mode))
		for identifier in newIdentifiers: print("\t", identifier)
		
		if (action == "add"):
		#
			projectSettings[targetListName].extend(newIdentifiers)
			
		#
		elif (action == "remove"):
		#
			if (mode == "Function"):
			#
				projectSettings[targetListName] = RemoveFunctionsFromList(projectSettings[targetListName], newIdentifiers)
			#
			else:
			#
				projectSettings[targetListName] = RemoveItemsFromList(projectSettings[targetListName], newIdentifiers)
			#
		#
		projectSettings[targetListName].sort()
		
		if (action == "list"):
		#
			print("%u Custom %ss in this project:" % (len(projectSettings[targetListName]), mode))
			for identifier in projectSettings[targetListName]: print("\t", identifier)
			# return
		#
		
		if (update_syntax_file):
		#
			if (mode != "Function"):
			#
				syntaxFilePath = self.view.settings().get("syntax")
				# syntaxFileDirectory, syntaxFileName = os.path.split(syntaxFilePath)
				# syntaxFileNameNoExt, syntaxFileExt = os.path.splitext(syntaxFileName)
				print("Current syntax: \"%s\"" % (syntaxFilePath))
				
				print("Getting packages path...")
				packagePath = sublime.packages_path()
				while (packagePath == None or packagePath == ""): packagePath = sublime.packages_path()
				packagePath = os.path.abspath(os.path.join(packagePath, os.pardir))
				print("Package Path: \"%s\"" % (packagePath))
				syntaxFileAbsPath = os.path.abspath(packagePath + "\\" + syntaxFilePath)
				
				searchRegex = "[\\s]+custom_%ss:[\\s]+'([A-Za-z0-9_\\|]*)'" % (mode.lower())
				
				modifyResult = ModifySyntaxFileRegexList(syntaxFileAbsPath, searchRegex, projectSettings[targetListName])
				if (modifyResult == True): print("Updated syntax file successfully")
				else: print("Couldn't update syntax file")
			#
			else:
			#
				print("Custom Functions cannot be added to the syntax file")
			#
		#
		
		print("Saving Project Settings...")
		SaveProjectSettings(self.view.window(), projectSettings)
		print("Done!")
	#
#

class CustomIdentifierEventListener(sublime_plugin.EventListener):
#
	def on_query_completions(self, view, prefix, locations):
	#
		result = []
		# print("Listener!", prefix, locations)
		
		projectSettings = GetProjectSettings(view.window())
		if (projectSettings == None): return
		
		for customType in projectSettings["custom_types"]:
		#
			result.append([customType + "\t" + "Custom Type", customType])
		#
		for customConstant in projectSettings["custom_constants"]:
		#
			result.append([customConstant + "\t" + "Custom Constant", customConstant])
		#
		for customGlobal in projectSettings["custom_globals"]:
		#
			result.append([customGlobal + "\t" + "Custom Global", customGlobal])
		#
		
		for functionStr in projectSettings["custom_functions"]:
		#
			parsedFunction = CppFunction(functionStr)
			if (parsedFunction.valid):
			#
				pIndex = 1
				paramNameStr = ""
				paramReplaceStr = ""
				for parameter in parsedFunction.parameters:
				#
					if (paramNameStr != ""):
					#
						paramReplaceStr += ", "
						paramNameStr += ", "
					#
					paramNameStr += parameter
					paramReplaceStr += "${%u:%s}" % (pIndex, parameter)
					pIndex += 1
				#
				displayStr = parsedFunction.name + "(" + paramNameStr + ")"
				insertStr = parsedFunction.name + "(" + paramReplaceStr + ")"
				# print("Suggesting function \"%s\"" % (parsedFunction.name))
				result.append([displayStr+"\t"+"Custom Function", insertStr])
			#
		#
		
		return result
	#
#
