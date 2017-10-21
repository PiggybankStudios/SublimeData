import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

class DeleteFileCommand(sublime_plugin.TextCommand):
#
	def run(self, edit):
	#
		filename = self.view.file_name()
		branch, leaf = os.path.split(filename)
		
		if (sublime.ok_cancel_dialog("Are you sure you want to delete %s" % (leaf), "Delete")):
		#
			print("Deleting \"%s\" in folder \"%s\"!" % (leaf, branch))
			
			if (not os.access(filename, os.W_OK)):
			#
				sublime.error_message(leaf + " is read-only")
				return
			#
			
			deletedSuccessfully = False
			try:
			#
				removeResult = os.remove(filename)
				deletedSuccessfully = True
			#
			except Exception as e:
			#
				sublime.status_message("Unable to delete file: " + str(e))
			#
			
			if (deletedSuccessfully):
			#
				sublime.status_message("Deleted \"%s\"" % (leaf))
				self.view.close()
			#
		#
		else:
		#
			print("User decided not to delete file")
		#
	#
#