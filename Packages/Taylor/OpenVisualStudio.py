import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

import re
import subprocess

class OpenVisualStudioCommand(sublime_plugin.TextCommand):
#
	def run(self, edit):
	#
		possibleVsExePaths = [
			"C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\Common7\\IDE\\devenv.exe",
			"C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Professional\\Common7\\IDE\\devenv.exe",
			"C:\\Program Files (x86)\\Microsoft Visual Studio\\2017\\Professional\\Common7\\IDE\\devenv.exe",
		];
		vsExePath = "";
		for possibleVsExePath in possibleVsExePaths:
		#
			if (os.path.isfile(possibleVsExePath)):
			#
				vsExePath = possibleVsExePath;
				break;
			#
		#
		if (vsExePath == ""):
		#
			print("Couldn't find visual studio executable in any of the expected places.");
			return;
		#
		
		command = "\"" + vsExePath + "\" /edit \"" + self.view.file_name() + "\"";
		print("Running: " + command);
		subprocess.Popen(command)
	#
#