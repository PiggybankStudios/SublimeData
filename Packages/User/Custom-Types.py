import os, sys, sublime, sublime_plugin
sys.path.append(os.path.dirname(__file__))
from User.MyFunctions import *

import re

# TODO: Move reading and writing of project settings into their own functions

class CustomTypesEventListener(sublime_plugin.EventListener):
	def on_query_completions(self, view, prefix, locations):
		result = []
		# print("Listener!")
		
		projectSettings = view.window().project_data()
		if (projectSettings == None):
			return
		
		if ("settings" in projectSettings):
			if ("custom_types" in projectSettings["settings"]):
				for customType in projectSettings["settings"]["custom_types"]:
					# print("Type: \"" + customType + "\"")
					result.append([customType + "\t" + "Custom Type", customType])
			if ("custom_constants" in projectSettings["settings"]):
				for customConstant in projectSettings["settings"]["custom_constants"]:
					# print("Type: \"" + customConstant + "\"")
					result.append([customConstant + "\t" + "Custom Constant", customConstant])
			if ("custom_globals" in projectSettings["settings"]):
				for customGlobal in projectSettings["settings"]["custom_globals"]:
					# print("Type: \"" + customGlobal + "\"")
					result.append([customGlobal + "\t" + "Custom Global", customGlobal])
		
		return result




class UpdateCustomTypesCommand(sublime_plugin.TextCommand):
	outputPanel = None
	editToken = None
	
	def ClosePanelTimeout(self):
		self.view.window().destroy_output_panel("CustomTypes")
		# print("Windows: " + str(sublime.windows()))

	def StartOutput(self, edit):
		self.outputPanel = self.view.window().create_output_panel("CustomTypes")
		self.view.window().run_command("show_panel", {"panel": "output.CustomTypes"})
		self.editToken = edit
		self.outputPanel.settings().set("word_wrap", True)
	
	def ShowError(self, errorString):
		fullString = "ERROR in Custom-Types Plugin:\n" + errorString + "\n"
		fullStringLength = len(fullString)
		if (self.outputPanel != None):
			insertPos = self.outputPanel.size()
			self.outputPanel.insert(self.editToken, insertPos, fullString)
			errorRegions = self.outputPanel.get_regions("errorRegions")
			errorRegions.append(sublime.Region(insertPos, insertPos + fullStringLength))
			self.outputPanel.add_regions("errorRegions", errorRegions, "string")
			#TODO: Add a region to color the error red
		# sublime.set_timeout(self.ClosePanelTimeout, 2000)

	def ShowOutput(self, newString):
		if (self.outputPanel != None):
			self.outputPanel.insert(self.editToken, self.outputPanel.size(), newString + "\n")

	def CompleteOutput(self):
		# self.view.window().destroy_output_panel("CustomTypes")
		sublime.set_timeout(self.ClosePanelTimeout, 1000)
	
	def StringIsValidType(self, typeString):
		if (typeString == None):
			self.ShowOutput("Not valid type: Empty string")
			return False
		
		typeStringLength = len(typeString)
		
		searchResult = re.search("[A-Za-z0-9_]+", typeString)
		
		if (searchResult == None or
			searchResult.start() != 0 or 
			searchResult.end() != typeStringLength):
			self.ShowOutput("Not valid type: Invalid characters")
			return False
			
		return True
	
	def UpdateSyntaxTypes(self, customTypes):
		packagePath = sublime.packages_path()
		while (packagePath == None or packagePath == ""):
			packagePath = sublime.packages_path()
		
		self.ShowOutput("Packages Path: \"" + str(packagePath) + "\"")
		SyntaxFileName = packagePath + "\\User\\My C.sublime-syntax"
		
		absPath = os.path.abspath(SyntaxFileName)
		self.ShowOutput("absolute path is \"" + absPath + "\"")
		
		# Read the current fileContents
		file = open(SyntaxFileName, "r")
		if (file == None):
			self.ShowError("Couldn't open syntax file for reading")
			return False
		fileContents = file.read()
		file.close()
		
		searchResult = re.search("[\\s]+custom_types:[\\s]+'([A-Za-z0-9_\\|]*)'", fileContents)
		
		if (searchResult == None or
			len(searchResult.groups()) < 1):
			self.ShowError("Couldn't find custom_types in sublime-syntax file")
			return False
		
		typeListStart = searchResult.start(1)
		typeListEnd = searchResult.end(1)
		typeListStr = searchResult.group(1)
		
		newTypeListStr = "|".join(customTypes)
		
		if (newTypeListStr == typeListStr):
			self.ShowError("Type List in syntax already matches")
			return False
		
		# Replace the old value in the file with our new list
		fileContents = fileContents[:typeListStart] + newTypeListStr + fileContents[typeListEnd:]
		
		# Write the new fileContents
		file = open(SyntaxFileName, 'w')
		if (file == None):
			self.ShowError("Couldn't open syntax file for writing")
			return False
		file.write(fileContents)
		file.close()
		
		self.ShowOutput("Syntax type list updated successfully!")
		return True
	
	def run(self, edit, addSelected = False, removeSelected = False, printInformation = False):
		window = self.view.window()
		self.StartOutput(edit)
		
		customTypes = []
		projectSettings = window.project_data()
		if (projectSettings == None):
			self.ShowError("No project opened")
			return
		
		if (not "settings" in projectSettings):
			projectSettings["settings"] = {}
		if ("custom_types" in projectSettings["settings"]):
			customTypes = projectSettings["settings"]["custom_types"]
		
		if (addSelected and removeSelected):
			self.ShowError("Cannot add AND remove selected items")
			return
		
		if (addSelected):
			numTypesAdded = 0
			for region in self.view.sel():
				newType = self.view.substr(region)
				if (self.StringIsValidType(newType) and
					not newType in customTypes):
					self.ShowOutput("Adding type \"" + newType + "\"")
					customTypes.append(newType)
					numTypesAdded += 1
				else:
					self.ShowOutput("Ignoring selection \"" + newType + "\"")
			self.ShowOutput("Addded " + str(numTypesAdded) + " new type(s)")
		elif (removeSelected):
			numTypesRemoved = 0
			for region in self.view.sel():
				newType = self.view.substr(region)
				if (self.StringIsValidType(newType) and
					newType in customTypes):
					self.ShowOutput("Removing type \"" + newType + "\"")
					customTypes.remove(newType)
					numTypesRemoved += 1
				else:
					self.ShowOutput("Ignoring selection \"" + newType + "\"")
			self.ShowOutput("Removed " + str(numTypesRemoved) + " type(s)")
		elif (not printInformation):
			self.ShowError("No arguments specified")
			return
		
		customTypes.sort()
		
		projectSettings["settings"]["custom_types"] = customTypes
		
		if (printInformation):
			self.ShowOutput("Project Types: " + (", ".join(customTypes)))
		
		window.set_project_data(projectSettings)
		
		if (self.UpdateSyntaxTypes(customTypes) == True):
			self.CompleteOutput()




class UpdateCustomConstantsCommand(sublime_plugin.TextCommand):
	outputPanel = None
	editToken = None
	
	def ClosePanelTimeout(self):
		self.view.window().destroy_output_panel("CustomConstants")
		# print("Windows: " + str(sublime.windows()))

	def StartOutput(self, edit):
		self.outputPanel = self.view.window().create_output_panel("CustomConstants")
		self.view.window().run_command("show_panel", {"panel": "output.CustomConstants"})
		self.editToken = edit
		self.outputPanel.settings().set("word_wrap", True)
	
	def ShowError(self, errorString):
		fullString = "ERROR in Custom-Types Plugin:\n" + errorString + "\n"
		fullStringLength = len(fullString)
		if (self.outputPanel != None):
			insertPos = self.outputPanel.size()
			self.outputPanel.insert(self.editToken, insertPos, fullString)
			errorRegions = self.outputPanel.get_regions("errorRegions")
			errorRegions.append(sublime.Region(insertPos, insertPos + fullStringLength))
			self.outputPanel.add_regions("errorRegions", errorRegions, "string")
			#TODO: Add a region to color the error red
		# sublime.set_timeout(self.ClosePanelTimeout, 2000)

	def ShowOutput(self, newString):
		if (self.outputPanel != None):
			self.outputPanel.insert(self.editToken, self.outputPanel.size(), newString + "\n")

	def CompleteOutput(self):
		# self.view.window().destroy_output_panel("CustomConstants")
		sublime.set_timeout(self.ClosePanelTimeout, 1000)
	
	def StringIsValidType(self, typeString):
		if (typeString == None):
			self.ShowOutput("Not valid type: Empty string")
			return False
		
		typeStringLength = len(typeString)
		
		searchResult = re.search("[A-Za-z0-9_]+", typeString)
		
		if (searchResult == None or
			searchResult.start() != 0 or 
			searchResult.end() != typeStringLength):
			self.ShowOutput("Not valid type: Invalid characters")
			return False
			
		return True
	
	def UpdateSyntaxConstants(self, customConstants):
		packagePath = sublime.packages_path()
		while (packagePath == None or packagePath == ""):
			packagePath = sublime.packages_path()
		
		self.ShowOutput("Packages Path: \"" + str(packagePath) + "\"")
		SyntaxFileName = packagePath + "\\User\\My C.sublime-syntax"
		
		absPath = os.path.abspath(SyntaxFileName)
		self.ShowOutput("absolute path is \"" + absPath + "\"")
		
		# Read the current fileContents
		file = open(SyntaxFileName, "r")
		if (file == None):
			self.ShowError("Couldn't open syntax file for reading")
			return False
		fileContents = file.read()
		file.close()
		
		searchResult = re.search("[\\s]+custom_constants:[\\s]+'([A-Za-z0-9_\\|]*)'", fileContents)
		
		if (searchResult == None or
			len(searchResult.groups()) < 1):
			self.ShowError("Couldn't find custom_constants in sublime-syntax file")
			return False
		
		constListStart = searchResult.start(1)
		constListEnd = searchResult.end(1)
		constListStr = searchResult.group(1)
		
		newConstListStr = "|".join(customConstants)
		
		if (newConstListStr == constListStr):
			self.ShowError("Constant List in syntax already matches")
			return False
		
		# Replace the old value in the file with our new list
		fileContents = fileContents[:constListStart] + newConstListStr + fileContents[constListEnd:]
		
		# Write the new fileContents
		file = open(SyntaxFileName, 'w')
		if (file == None):
			self.ShowError("Couldn't open syntax file for writing")
			return False
		file.write(fileContents)
		file.close()
		
		self.ShowOutput("Syntax constant list updated successfully!")
		return True
	
	def run(self, edit, addSelected = False, removeSelected = False, printInformation = False):
		window = self.view.window()
		self.StartOutput(edit)
		
		customConstants = []
		projectSettings = window.project_data()
		if (projectSettings == None):
			self.ShowError("No project opened")
			return
		
		if (not "settings" in projectSettings):
			projectSettings["settings"] = {}
		if ("custom_constants" in projectSettings["settings"]):
			customConstants = projectSettings["settings"]["custom_constants"]
		
		if (addSelected and removeSelected):
			self.ShowError("Cannot add AND remove selected items")
			return
		
		if (addSelected):
			numConstantsAdded = 0
			for region in self.view.sel():
				newConst = self.view.substr(region)
				if (self.StringIsValidType(newConst) and
					not newConst in customConstants):
					self.ShowOutput("Adding constant \"" + newConst + "\"")
					customConstants.append(newConst)
					numConstantsAdded += 1
				else:
					self.ShowOutput("Ignoring selection \"" + newConst + "\"")
			self.ShowOutput("Addded " + str(numConstantsAdded) + " new constant(s)")
		elif (removeSelected):
			numConstantsRemoved = 0
			for region in self.view.sel():
				newConst = self.view.substr(region)
				if (self.StringIsValidType(newConst) and
					newConst in customConstants):
					self.ShowOutput("Removing constant \"" + newConst + "\"")
					customConstants.remove(newConst)
					numConstantsRemoved += 1
				else:
					self.ShowOutput("Ignoring selection \"" + newConst + "\"")
			self.ShowOutput("Removed " + str(numConstantsRemoved) + " constant(s)")
		elif (not printInformation):
			self.ShowError("No arguments specified")
			return
		
		customConstants.sort()
		
		projectSettings["settings"]["custom_constants"] = customConstants
		
		if (printInformation):
			self.ShowOutput("Project Constants: " + (", ".join(customConstants)))
		
		window.set_project_data(projectSettings)
		
		if (self.UpdateSyntaxConstants(customConstants) == True):
			self.CompleteOutput()




class UpdateCustomGlobalsCommand(sublime_plugin.TextCommand):
	outputPanel = None
	editToken = None
	
	def ClosePanelTimeout(self):
		self.view.window().destroy_output_panel("CustomGlobals")
		# print("Windows: " + str(sublime.windows()))

	def StartOutput(self, edit):
		self.outputPanel = self.view.window().create_output_panel("CustomGlobals")
		self.view.window().run_command("show_panel", {"panel": "output.CustomGlobals"})
		self.editToken = edit
		self.outputPanel.settings().set("word_wrap", True)
	
	def ShowError(self, errorString):
		fullString = "ERROR in Custom-Types Plugin:\n" + errorString + "\n"
		fullStringLength = len(fullString)
		if (self.outputPanel != None):
			insertPos = self.outputPanel.size()
			self.outputPanel.insert(self.editToken, insertPos, fullString)
			errorRegions = self.outputPanel.get_regions("errorRegions")
			errorRegions.append(sublime.Region(insertPos, insertPos + fullStringLength))
			self.outputPanel.add_regions("errorRegions", errorRegions, "string")
			#TODO: Add a region to color the error red
		# sublime.set_timeout(self.ClosePanelTimeout, 2000)

	def ShowOutput(self, newString):
		if (self.outputPanel != None):
			self.outputPanel.insert(self.editToken, self.outputPanel.size(), newString + "\n")

	def CompleteOutput(self):
		# self.view.window().destroy_output_panel("CustomGlobals")
		sublime.set_timeout(self.ClosePanelTimeout, 1000)
	
	def StringIsValidType(self, typeString):
		if (typeString == None):
			self.ShowOutput("Not valid type: Empty string")
			return False
		
		typeStringLength = len(typeString)
		
		searchResult = re.search("[A-Za-z0-9_]+", typeString)
		
		if (searchResult == None or
			searchResult.start() != 0 or 
			searchResult.end() != typeStringLength):
			self.ShowOutput("Not valid type: Invalid characters")
			return False
			
		return True
	
	def UpdateSyntaxGlobals(self, customGlobals):
		packagePath = sublime.packages_path()
		while (packagePath == None or packagePath == ""):
			packagePath = sublime.packages_path()
		
		self.ShowOutput("Packages Path: \"" + str(packagePath) + "\"")
		SyntaxFileName = packagePath + "\\User\\My C.sublime-syntax"
		
		absPath = os.path.abspath(SyntaxFileName)
		self.ShowOutput("absolute path is \"" + absPath + "\"")
		
		# Read the current fileContents
		file = open(SyntaxFileName, "r")
		if (file == None):
			self.ShowError("Couldn't open syntax file for reading")
			return False
		fileContents = file.read()
		file.close()
		
		searchResult = re.search("[\\s]+custom_globals:[\\s]+'([A-Za-z0-9_\\|]*)'", fileContents)
		
		if (searchResult == None or
			len(searchResult.groups()) < 1):
			self.ShowError("Couldn't find custom_globals in sublime-syntax file")
			return False
		
		globalsListStart = searchResult.start(1)
		globalsListEnd = searchResult.end(1)
		globalsListStr = searchResult.group(1)
		
		newGlobalsListStr = "|".join(customGlobals)
		
		if (newGlobalsListStr == globalsListStr):
			self.ShowError("Globals List in syntax already matches")
			return False
		
		# Replace the old value in the file with our new list
		fileContents = fileContents[:globalsListStart] + newGlobalsListStr + fileContents[globalsListEnd:]
		
		# Write the new fileContents
		file = open(SyntaxFileName, 'w')
		if (file == None):
			self.ShowError("Couldn't open syntax file for writing")
			return False
		file.write(fileContents)
		file.close()
		
		self.ShowOutput("Syntax globals list updated successfully!")
		return True
	
	def run(self, edit, addSelected = False, removeSelected = False, printInformation = False):
		window = self.view.window()
		self.StartOutput(edit)
		
		customGlobals = []
		projectSettings = window.project_data()
		if (projectSettings == None):
			self.ShowError("No project opened")
			return
		
		if (not "settings" in projectSettings):
			projectSettings["settings"] = {}
		if ("custom_globals" in projectSettings["settings"]):
			customGlobals = projectSettings["settings"]["custom_globals"]
		
		if (addSelected and removeSelected):
			self.ShowError("Cannot add AND remove selected items")
			return
		
		if (addSelected):
			numGlobalsAdded = 0
			for region in self.view.sel():
				newGlobal = self.view.substr(region)
				if (self.StringIsValidType(newGlobal) and
					not newGlobal in customGlobals):
					self.ShowOutput("Adding global \"" + newGlobal + "\"")
					customGlobals.append(newGlobal)
					numGlobalsAdded += 1
				else:
					self.ShowOutput("Ignoring selection \"" + newGlobal + "\"")
			self.ShowOutput("Addded " + str(numGlobalsAdded) + " new global(s)")
		elif (removeSelected):
			numGlobalsRemoved = 0
			for region in self.view.sel():
				newGlobal = self.view.substr(region)
				if (self.StringIsValidType(newGlobal) and
					newGlobal in customGlobals):
					self.ShowOutput("Removing global \"" + newGlobal + "\"")
					customGlobals.remove(newGlobal)
					numGlobalsRemoved += 1
				else:
					self.ShowOutput("Ignoring selection \"" + newGlobal + "\"")
			self.ShowOutput("Removed " + str(numGlobalsRemoved) + " global(s)")
		elif (not printInformation):
			self.ShowError("No arguments specified")
			return
		
		customGlobals.sort()
		
		projectSettings["settings"]["custom_globals"] = customGlobals
		
		if (printInformation):
			self.ShowOutput("Project Globals: " + (", ".join(customGlobals)))
		
		window.set_project_data(projectSettings)
		
		if (self.UpdateSyntaxGlobals(customGlobals) == True):
			self.CompleteOutput()
