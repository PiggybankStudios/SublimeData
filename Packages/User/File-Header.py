import sublime
import sublime_plugin
import os
import re
import time

class CreateFileHeaderCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		filePath = self.view.file_name()
		fileFolder, fileName = os.path.split(filePath)
		fileNameNoExt, fileNameExt = os.path.splitext(fileName)
		print("fileNameExt: " + fileNameExt)
		
		authorName = "Taylor Robbins"
		dateString = time.strftime("%m\\%d\\%Y")
		
		headerString = ""
		selectRegion = False
		newRegion = None
		if (fileNameExt in [".h", ".hpp"]):
			headerString += "/*\n"
			headerString += "File:   " + fileName   + "\n"
			headerString += "Author: " + authorName + "\n"
			headerString += "Date:   " + dateString + "\n"
			headerString += "*/\n"
			headerString += "\n"
		elif (fileNameExt in [".c", ".cpp", ".py"]):
			headerString += "/*\n"
			headerString += "File:   " + fileName   + "\n"
			headerString += "Author: " + authorName + "\n"
			headerString += "Date:   " + dateString + "\n"
			headerString += "Description: \n"
			headerString += "\t** None \n"
			headerString += "*/\n\n"
			searchResult = re.search("\t\*\* (None)", headerString)
			newRegion = sublime.Region(searchResult.start(1),searchResult.end(1))
			selectRegion = True
		
		self.view.insert(edit, 0, headerString)
		
		if (selectRegion):
			self.view.sel().clear()
			self.view.sel().add(newRegion)
			self.view.run_command("show_at_center")

class CreateLocalHeaderCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		for region in self.view.sel():
			selectionStr = self.view.substr(region)
			if (len(selectionStr) == 0):
				continue
			lineRegion = self.view.line(region.begin())
			indentationStr = self.view.substr(sublime.Region(lineRegion.begin(), region.begin()))
			print("Indentation: \"" + indentationStr + "\"")
			print("Selection = \"" + selectionStr + "\"")
			
			# Pad the string to 32 characters
			while (len(selectionStr) < 32 - 2):
				selectionStr = selectionStr + " "
				if (len(selectionStr) < 32):
					selectionStr = " " + selectionStr
			
			if (len(selectionStr) >= 32 - 2):
				selectionStr = " " + selectionStr + " "
				if (len(selectionStr) % 2 != 0):
					selectionStr = selectionStr + " "
			
			headerWidth = len(selectionStr)
			headerTopStr = ""
			while (len(headerTopStr) < headerWidth):
				headerTopStr += "="
			headerTopStr = "+" + headerTopStr + "+"
			
			headerString  = "//" + headerTopStr + "\n" + indentationStr
			headerString += "//|" + selectionStr + "|" + "\n" + indentationStr
			headerString += "//" + headerTopStr
			
			self.view.replace(edit, region, headerString);
			