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
		
		if (len(searchString) > 0):
		#
			print("My Google Search: Searching for \"" + searchString + "\"")
			searchString = searchString.replace(" ", "+")
			webbrowser.open("https://www.google.com/search?q=" + searchString)
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
