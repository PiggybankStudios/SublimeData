import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

class InsertLangStrCommand(sublime_plugin.TextCommand):
#
	def run(self, edit, name=""):
	#
		if (len(self.view.sel()) == 0):
		#
			sublime.status_message("No regions selected")
			return
		#
		elif (len(self.view.sel()) > 1):
		#
			sublime.status_message("Too many regions selected")
			return
		#
		selectionRegon = self.view.sel()[0]
		originalText = self.view.substr(selectionRegon)
		if (name == ""):
		#
			nameParts = GetNameParts(originalText)
			upperFirstsName = ""
			for namePart in nameParts: upperFirstsName += UpperFirst(namePart)
			self.view.window().show_input_panel(
				"LangStr_",
				upperFirstsName, # Initial Text
				self.on_done,
				None, #on_preview
				None #on_cancel
			)
		#
		else:
		#
			print("Would insert with name \"" + name + "\"")
			
			numSpaces = 25 - len(name)
			if (numSpaces < 0): numSpaces = 0
			paddingStr = " " * numSpaces
			
			projectPath = self.view.window().project_file_name()
			projectBaseDir, projectFileName = os.path.split(projectPath)
			
			listHeaderFilePath = projectBaseDir + "/code/app/app_lang_strs_list.h"
			if (not os.path.exists(listHeaderFilePath)):
			#
				print("Couldn't file the app_lang_strs_list.h header file at \"%s\"" % listHeaderFilePath)
				return
			#
			
			listHeaderFile = open(listHeaderFilePath, "r")
			listFileContents = listHeaderFile.readlines()
			listHeaderFile.close()
			
			insertLineIndex = len(listFileContents)
			lIndex = 0
			for line in listFileContents:
			#
				if ("LANG_STR_ENTRY(" in line): insertLineIndex = lIndex+1
				lIndex += 1
			#
			if (insertLineIndex > 0 and not listFileContents[insertLineIndex-1].endswith("\n")):
			#
				listFileContents[insertLineIndex-1] += "\n"
			#
			listFileContents.insert(insertLineIndex, "LANG_STR_ENTRY(" + name + ")\n")
			
			listHeaderFile = open(listHeaderFilePath, "w")
			listHeaderFile.write("".join(listFileContents))
			listHeaderFile.close()
			
			langFolder = projectBaseDir + "/data/Resources/Languages/"
			# print("langFolder: \"%s\"" % langFolder)
			langFiles = os.listdir(langFolder)
			
			for fileName in langFiles:
			#
				filePath = langFolder + fileName
				if (not os.path.isdir(filePath)):
				#
					if (fileName.startswith("lang_")):
					#
						# print("Lang File: \"%s\"" % fileName)
						with open(filePath, "a") as langFile:
						#
							if ("_en" in fileName):
							#
								langFile.write("\n" + name + ":" + paddingStr + originalText)
							#
							else:
							#
								langFile.write("\n" + name + ":" + paddingStr + "?")
							#
						#
					#
				#
			#
			
			# Remove trailing quote
			if (selectionRegon.end() < self.view.size()):
			#
				charAfterRegion = sublime.Region(selectionRegon.end(), selectionRegon.end() + 1)
				if (self.view.substr(charAfterRegion) == "\""): self.view.erase(edit, charAfterRegion)
			#
			# Remove leading quote
			if (selectionRegon.begin() > 0):
			#
				charBeforeRegion = sublime.Region(selectionRegon.begin() - 1, selectionRegon.begin())
				if (self.view.substr(charBeforeRegion) == "\""): self.view.erase(edit, charBeforeRegion)
			#
			selectionRegon = self.view.sel()[0]
			self.view.replace(edit, selectionRegon, "LangStr(" + name + ")")
		#
	#
	
	def on_done(self, name):
	#
		self.view.run_command("insert_lang_str", {"name": name})
	#
#