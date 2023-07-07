import subprocess, os, platform, sys, sublime, sublime_plugin
from Taylor.Functions import *

class OpenFileWithDefaultProgramCommand(sublime_plugin.WindowCommand):
#
	def run(self, extensions=[]):
	#
		filePath = self.window.active_view().file_name()
		if not filePath:
			return
		
		print("Opening file %s" % (filePath));
		if platform.system() == 'Darwin':       # macOS
		#
			subprocess.call(('open', filePath))
		#
		elif platform.system() == 'Windows':    # Windows
		#
			os.startfile(filePath)
		#
		else:                                   # linux variants
		#
			subprocess.call(('xdg-open', filePath))
		#
	#
#
