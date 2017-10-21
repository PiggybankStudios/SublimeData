import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

import functools

class RenameFileCommand(sublime_plugin.TextCommand):
#
	def run(self, edit):
	#
		filename = self.view.file_name()
		branch, leaf = os.path.split(filename)
		
		if (not os.access(filename, os.W_OK)):
		#
			sublime.error_message(leaf + " is read-only")
		#
		
		panel = self.view.window().show_input_panel("New Name:", leaf, functools.partial(self.on_done, filename, branch), None, None)
		
		name, ext = os.path.splitext(leaf)
		panel.sel().clear()
		panel.sel().add(sublime.Region(0, len(name)))
	#
	
	def on_done(self, oldFileName, branch, leaf):
	#
		newFileName = os.path.join(branch, leaf)
		
		try:
		#
			if (len(leaf) == 0):
			#
				sublime.error_message("No filename given")
				return;
			#
				
			if (os.path.exists(newFileName) and oldFileName != newFileName):
			#
				sublime.error_message(newFileName + " already exists")
				return;
			#
				
			os.rename(oldFileName, newFileName)
			
			v = self.view.window().find_open_file(oldFileName)
			if v: v.retarget(newFileName)
		#
		except Exception as e:
		#
			sublime.status_message("Unable to rename: " + str(e))
		#
	#
#