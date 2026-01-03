import os, platform, sys, sublime, sublime_plugin
from Taylor.Functions import *
import subprocess

class StartCswitchCommand(sublime_plugin.TextCommand):
#
	def run(self, edit):
	#
		fileName = self.view.file_name();
		if (fileName == ""):
		#
			print("Current tab doesn't represent a file on disk!");
			return;
		#
		
		# print("Running on " + os.name)
		print("Starting CSwitch on \"%s\"!" % (fileName));
		print("PATH = %s!" % (os.environ.get("PATH")));
		cswitchBinaryName = "cswitch";
		if (platform.system() == "Windows"):
		#
			cswitchBinaryName = "cswitch.exe";
		#
		subprocess.Popen([cswitchBinaryName, fileName, "-top", "-size=(220,350)"]);

	#
#