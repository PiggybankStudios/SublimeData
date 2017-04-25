import sublime
import sublime_plugin
import re

# TODO: Clean up error outputs so the user sees if something goes wrong
# TODO: Add a window to show all types when running list_custom_types command
# TODO: Move reading and writing of project settings into their own functions

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
	
	def ShowError(self, errorString):
		fullString = "ERROR in Custom-Types Plugin:\n" + errorString + "\n"
		fullStringLength = len(fullString)
		if (self.outputPanel != None):
			insertPos = self.outputPanel.size()
			self.outputPanel.insert(self.editToken, insertPos, fullString)
			errorRegions = self.outputPanel.get_regions("errorRegions")
			errorRegions.append(sublime.Region(insertPos, insertPos + fullStringLength))
			print(self.outputPanel.)
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
					numTypesRemoved -= 1
				else:
					self.ShowOutput("Ignoring selection \"" + newType + "\"")
			self.ShowOutput("Removed " + str(numTypesRemoved) + " type(s)")
		elif (not printInformation):
			self.ShowError("No arguments specified")
			return
		
		projectSettings["settings"]["custom_types"] = customTypes
		
		if (printInformation):
			self.ShowOutput("Project Types: " + (", ".join(customTypes)))
		
		window.set_project_data(projectSettings)
		
		if (self.UpdateSyntaxTypes(customTypes) == True):
			self.CompleteOutput()
		
		
		
		