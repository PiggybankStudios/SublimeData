import os, sys, sublime, sublime_plugin
from Taylor.Functions import *
import subprocess

# This function is simply for testing new functionality. It's bound to ctrl+;
class StartGitBashCommand(sublime_plugin.TextCommand):
#
	def run(self, edit):
	#
		projectPath = self.view.window().project_file_name()
		if (projectPath == ""):
		#
			print("No project open")
			return
		#

		print("Running on " + os.name)
		
		projectDir, projectFile = os.path.split(projectPath)
		print(projectDir)
		print("Starting Git Bash in \"%s\"!" % (projectDir))

		if (os.name == "posix"):
		#
			subprocess.Popen("x-terminal-emulator", cwd=projectDir)
		#
		else:
		#
			subprocess.Popen("C:\\Program Files\\Git\\git-bash.exe", cwd=projectDir)
		#

	#
#