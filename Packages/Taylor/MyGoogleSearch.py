import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

import webbrowser

# Opens	up a web browser and searches the selected text on google
# Multiple selections will be concatenated together with spaces into a single search
# If remove_text is true then the selected text will be deleted at the same time
class MyGoogleSearchCommand(sublime_plugin.TextCommand):
#
	def run(self, edit, remove_text=False):
	#
		# print("Running")
		searchString = ""
		for region in self.view.sel(): 
		#
			if (searchString != ""):
			#
				searchString = searchString + " "
			#
			searchString = searchString + self.view.substr(region)
		#
		
		searchUrl = "https://www.google.com/search?q=";
		
		_, fileName = os.path.split(self.view.file_name());
		if (fileName.lower() == "cargo.toml"):
		#
			searchUrl = "https://crates.io/search?q=";
		#
		
		if (len(searchString) > 0):
		#
			print("My Google Search: Searching for \"" + searchString + "\"")
			searchString = searchString.replace(" ", "+")
			webbrowser.open(searchUrl + searchString)
		#
		else:
		#
			print("Nothing selected to search for")
		#
		
		if (remove_text):
		#
			for region in self.view.sel():
			#
				self.view.erase(edit, region)
			#
			# self.view.sel().clear()
		#
	#
#
