import sublime
import sublime_plugin
import re
import os
import zipfile
import tempfile

def StringIsValidType(typeString):
	if (typeString == None):
		print("Empty string")
		return False
	
	typeStringLength = len(typeString)
	
	searchResult = re.search("[A-Za-z0-9_]+", typeString)
	
	if (searchResult == None):
		print("No match")
		return False
	
	if (searchResult.start() != 0 or searchResult.end() != typeStringLength):
		print("Not full string: " + 
			"(" + str(searchResult.start()) + 
			":" + str(searchResult.end()) + ")")
		return False
		
	return True

def UpdateZipArchiveFile(zipname, filename, data):
	# generate a temp file
	tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(zipname))
	os.close(tmpfd)

	# create a temp copy of the archive without filename            
	with zipfile.ZipFile(zipname, 'r') as zin:
		with zipfile.ZipFile(tmpname, 'w') as zout:
			zout.comment = zin.comment # preserve the comment
			for item in zin.infolist():
				if item.filename != filename:
					zout.writestr(item, zin.read(item.filename))

	# replace with the temp archive
	os.remove(zipname)
	os.rename(tmpname, zipname)

	# now add filename with its new data
	with zipfile.ZipFile(zipname, mode='a', compression=zipfile.ZIP_DEFLATED) as zf:
		zf.writestr(filename, data)
		
def GetZipArchiveFile(zipname, filename):
	result = ""
	with zipfile.ZipFile(zipname, 'r') as zin:
		for item in zin.infolist():
			if (item.filename == filename):
				result = zin.read(item.filename)
	
	return result

def GetCurrentSyntaxTypes(packagePath):
	SyntaxFileName = packagePath + "\\User\\My C.sublime-syntax"
	
	# Read the current fileContents
	file = open(SyntaxFileName, "r")
	if (file == None):
		print("Couldn't open syntax file for reading")
		return None
	fileContents = file.read()
	file.close()
	
	searchResult = re.search("[\\s]+custom_types:[\\s]+'([A-Za-z0-9_\\|]*)'", fileContents)
	
	if (searchResult == None or
		len(searchResult.groups()) < 1):
		# TODO: Make this into an error window?
		print("Couldn't find custom_types in sublime-syntax file")
		return None
	
	typeListStart = searchResult.start(1)
	typeListEnd = searchResult.end(1)
	typeListStr = searchResult.group(1)
	typeList = typeListStr.split("|")
	
	return typeList
	
def UpdateSyntaxTypes(packagePath, customTypes):
	SyntaxFileName = packagePath + "\\User\\My C.sublime-syntax"
	
	# absPath = os.path.abspath(SyntaxFileName)
	# print("absolute path is \"" + absPath + "\"")
	
	# Read the current fileContents
	file = open(SyntaxFileName, "r")
	if (file == None):
		print("Couldn't open syntax file for reading")
		return
	fileContents = file.read()
	file.close()
	
	# print("File is " + str(len(fileContents)) + " bytes long")
	
	searchResult = re.search("[\\s]+custom_types:[\\s]+'([A-Za-z0-9_\\|]*)'", fileContents)
	
	if (searchResult == None or
		len(searchResult.groups()) < 1):
		# TODO: Make this into an error window?
		print("Couldn't find custom_types in sublime-syntax file")
		return
	
	typeListStart = searchResult.start(1)
	typeListEnd = searchResult.end(1)
	typeListStr = searchResult.group(1)
	
	newTypeListStr = "|".join(customTypes)
	
	if (newTypeListStr == typeListStr):
		print("Type List in syntax already matches")
		return
	
	# Replace the old value in the file with our new list
	fileContents = fileContents[:typeListStart] + newTypeListStr + fileContents[typeListEnd:]
	
	# Write the new fileContents
	file = open(SyntaxFileName, 'w')
	if (file == None):
		print("Couldn't open syntax file for writing")
		return;
	file.write(fileContents)
	file.close()
	
	print("Syntax type list updated successfully!")
	

class AddCustomTypeCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		window = self.view.window()
		
		customTypes = []
		projectSettings = window.project_data()
		if (projectSettings == None):
			print("No project opened")
			return
		# print("Current Project Settings: " + str(projectSettings))
		
		if (not "settings" in projectSettings):
			projectSettings["settings"] = {}
		if ("custom_types" in projectSettings["settings"]):
			customTypes = projectSettings["settings"]["custom_types"]
		
		for region in self.view.sel():
			newType = self.view.substr(region)
			if (StringIsValidType(newType) and
				not newType in customTypes):
				print("Adding type \"" + newType + "\"")
				customTypes.append(newType)
			else:
				print("Ignoring selection \"" + newType + "\"")
		
		projectSettings["settings"]["custom_types"] = customTypes
		# print("New Project Settings: " + str(projectSettings))
		
		window.set_project_data(projectSettings)
		
		windowSettings = window.extract_variables()
		while (windowSettings == None or
			not "packages" in windowSettings):
			# print("Could not get packages directory from window")
			windowSettings = window.extract_variables()
		# print("Window Settings: " + str(windowSettings))
		
		UpdateSyntaxTypes(windowSettings['packages'], customTypes)

class RemoveCustomTypeCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		window = self.view.window()
		
		customTypes = []
		projectSettings = window.project_data()
		if (projectSettings == None):
			print("No project opened")
			return
		# print("Current Project Settings: " + str(projectSettings))
		
		if (not "settings" in projectSettings):
			projectSettings["settings"] = {}
		if ("custom_types" in projectSettings["settings"]):
			customTypes = projectSettings["settings"]["custom_types"]
		
		for region in self.view.sel():
			newType = self.view.substr(region)
			if (StringIsValidType(newType) and
				newType in customTypes):
				print("Removing type \"" + newType + "\"")
				customTypes.remove(newType)
			else:
				print("Ignoring selection \"" + newType + "\"")
		
		projectSettings["settings"]["custom_types"] = customTypes
		# print("New Project Settings: " + str(projectSettings))
		
		window.set_project_data(projectSettings)
		
		windowSettings = window.extract_variables()
		while (windowSettings == None or
			not "packages" in windowSettings):
			# print("Could not get packages directory from window")
			windowSettings = window.extract_variables()
		# print("Window Settings: " + str(windowSettings))
		
		UpdateSyntaxTypes(windowSettings['packages'], customTypes)

class UpdateCustomTypesCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		window = self.view.window()
		
		customTypes = []
		projectSettings = window.project_data()
		if (projectSettings != None and
			"settings" in projectSettings and
			"custom_types" in projectSettings["settings"]):
			customTypes = projectSettings["settings"]["custom_types"]
		
		windowSettings = window.extract_variables()
		while (windowSettings == None or
			not "packages" in windowSettings):
			# print("Could not get packages directory from window")
			windowSettings = window.extract_variables()
		# print("Window Settings: " + str(windowSettings))
		
		UpdateSyntaxTypes(windowSettings['packages'], customTypes)

class ListCustomTypesCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		window = self.view.window()
		
		projectSettings = window.project_data()
		if (projectSettings == None):
			print("No project opened")
			return
		# print("Current Project Settings: " + str(projectSettings))
		
		if ("settings" in projectSettings and
			"custom_types" in projectSettings["settings"]):
			projectTypes = projectSettings["settings"]["custom_types"]
			print("Project Types: " + (", ".join(projectTypes)))
		else:
			print("No custom types in project settings")
		
		windowSettings = window.extract_variables()
		while (windowSettings == None or
			not "packages" in windowSettings):
			# print("Could not get packages directory from window")
			windowSettings = window.extract_variables()
		# print("Window Settings: " + str(windowSettings))
		
		syntaxTypes = GetCurrentSyntaxTypes(windowSettings['packages'])
		
		if (not syntaxTypes == None):
			print("Syntax Types: " + (", ".join(syntaxTypes)))
		else:
			print("Could not get syntax custom types")
		
		
		
		