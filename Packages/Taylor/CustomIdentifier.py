import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

import re

class CustomIdentifierCommand(sublime_plugin.TextCommand):
#
	def UpdateSyntaxFile(self, mode, newList):
	#
		syntaxFilePath = self.view.settings().get("syntax")
		# print("Current syntax: \"%s\"" % (syntaxFilePath))
		
		# print("Getting packages path...")
		packagePath = sublime.packages_path()
		while (packagePath == None or packagePath == ""): packagePath = sublime.packages_path()
		packagePath = os.path.abspath(os.path.join(packagePath, os.pardir))
		# print("Package Path: \"%s\"" % (packagePath))
		syntaxFileAbsPath = os.path.abspath(packagePath + "\\" + syntaxFilePath)
		
		searchRegex = "[\\s]+custom_%ss:[\\s]+'([A-Za-z0-9_\\|]*)'" % (mode.lower())
		
		modifyResult = ModifySyntaxFileRegexList(syntaxFileAbsPath, searchRegex, newList)
		if (modifyResult == True): print("Updated syntax file successfully")
		else: print("Couldn't update syntax file")
	#
	
	def run(self, edit, action="add", mode="Type", update_syntax_file=True):
	#
		#NOTE: The lookup action is essentially a seperate command entirely.
		#      We lookup the function name in the project custom_functions list
		#      and then paste the definition in a comment on a new line above the cursor 
		if (action == "lookup" and mode == "Function"):
		#
			projectSettings = GetProjectSettings(self.view.window())
			if (projectSettings == None):
			#
				print("No project data found!")
				return
			#
			
			for region in self.view.sel():
			#
				regionStr = self.view.substr(region)
				if (StringIsValidType(regionStr)):
				#
					print("Looking up function \"%s\"" % (regionStr))
					matchStr = ""
					for functionStr in projectSettings["custom_functions"]:
					#
						parsedFunction = CppFunction(functionStr)
						if (parsedFunction.valid):
						#
							if (parsedFunction.name == regionStr):
							#
								matchStr = functionStr
								break
							#
						#
					#
					
					if (matchStr != ""):
					#
						print("Found match! Inserting: \"%s\"" % (matchStr))
						lineRegion = self.view.line(region)
						lineStr = self.view.substr(lineRegion)
						indentationStr = GetLineIndentation(lineStr)
						commentStr = GetSyntaxCommentStr(self.view, lineRegion.begin())
						
						matchStr = matchStr.replace("\n", "\n" + indentationStr + commentStr)
						insertStr = indentationStr + commentStr + matchStr + "\n"
						
						self.view.insert(edit, lineRegion.begin(), insertStr)
					#
					else:
					#
						print("No match found")
					#
				#
				else:
				#
					print("Selection \"%s\" is not a valid function name. Skipping..." % (regionStr))
				#
			#
			
			return
		#
		
		#Check to make sure the inputs are valid
		if (action != "add" and action != "remove" and action != "list" and action != "update"):
		#
			print("\"%s\" is not a valid action for AddCustomIdentifierCommand" % (action))
			return
		#
		if (action != "update"):
		#
			if (mode != "Type" and mode != "Constant" and mode != "Global" and mode != "Function"):
			#
				print("\"%s\" is not a valid mode for AddCustomIdentifierCommand" % (mode))
				return
			#
		#
		
		#Load the project settings
		targetListName  = "custom_" + mode.lower() + "s"
		projectSettings = GetProjectSettings(self.view.window())
		if (projectSettings == None):
		#
			print("No project data found!")
			return
		#
		
		# If we are adding or removing elements, do that now
		if (action == "add" or action == "remove"):
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
						if (parsedFunction.valid or (StringIsValidType(regionStr) and action == "remove")):
						#
							selectedJustName = False
							functionName = parsedFunction.name
							if (StringIsValidType(regionStr) and action == "remove"):
							#
								selectedJustName = True
								functionName = regionStr
							#
							
							foundFunctionStr = ""
							foundMatch = False
							foundIndex = 0
							for functionStr in projectSettings["custom_functions"]:
							#
								function = CppFunction(functionStr)
								if (function.valid and function.name == functionName):
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
									if (regionStr == foundFunctionStr): print("\"%s\" already in the custom_function list as \"%s\"" % (functionName, foundFunctionStr))
									else:
									#
										print("Replacing existing Custom Function \"%s\" with new definition \"%s\"" % (foundFunctionStr, regionStr))
										projectSettings["custom_functions"].pop(foundIndex)
										newIdentifiers.append(regionStr)
									#
								#
								elif (action == "remove"):
								#
									if (selectedJustName): newIdentifiers.append("void " + regionStr + "()")
									else: newIdentifiers.append(regionStr)
								#
							#
							else:
							#
								if (action == "add"):
								#
									newIdentifiers.append(regionStr)
								#
								elif (action == "remove"): print("\"%s\" is not in the custom_function list" % (functionName))
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
								if (action == "add"): print("\"%s\" is already in the %s list" % (regionStr, targetListName))
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
								elif (action == "remove"): print("\"%s\" is not in the %s list" % (regionStr, targetListName))
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
		#
		
		# List the elements in the debug output
		if (action == "list"):
		#
			print("%u Custom %ss in this project:" % (len(projectSettings[targetListName]), mode))
			for identifier in projectSettings[targetListName]: print("\t", identifier)
			# return
		#
		
		#Update the syntax file if asked to do so
		if (update_syntax_file):
		#
			if (action == "update"):
			#
				self.UpdateSyntaxFile("Type", projectSettings["custom_types"])
				self.UpdateSyntaxFile("Constant", projectSettings["custom_constants"])
				self.UpdateSyntaxFile("Global", projectSettings["custom_globals"])
			#
			elif (mode == "Function"):
			#
				print("Custom Functions cannot be added to the syntax file")
			#
			else:
			#
				self.UpdateSyntaxFile(mode, projectSettings[targetListName])
			#
		#
		
		#Save the new lists to the project settings
		# print("Saving Project Settings...")
		SaveProjectSettings(self.view.window(), projectSettings)
		# print("Done!")
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
				paramNameStr = ""
				paramNameTypeStr = ""
				paramReplaceStr = ""
				for pIndex in range(0, len(parsedFunction.parameters)):
				#
					paramName = parsedFunction.parameters[pIndex]
					paramType = parsedFunction.parameterTypes[pIndex]
					if (paramNameStr != ""):
					#
						paramNameStr += ", "
						paramNameTypeStr += ", "
						paramReplaceStr += ", "
					#
					if (paramType != ""):
						paramNameTypeStr += paramType + " "
					paramNameStr += paramName
					paramNameTypeStr += paramName
					paramReplaceStr += "${%u:%s}" % (pIndex+1, paramName)
				#
				
				maxParamStrLength = 32
				paramStr = paramNameTypeStr
				if (len(paramStr) > maxParamStrLength): paramStr = paramNameStr
				# if (len(paramStr) > maxParamStrLength): paramStr = paramNameStr[:maxParamStrLength-3] + "..."
				
				displayStr = parsedFunction.name + "\t(" + paramStr + ")"
				insertStr = parsedFunction.name + "(" + paramReplaceStr + ")"
				# print("Suggesting function \"%s\"" % (parsedFunction.name))
				result.append([displayStr, insertStr])
			#
		#
		
		return result
	#
#
