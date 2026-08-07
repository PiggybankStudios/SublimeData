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
		print("platform.system() = %s" % platform.system());
		cswitchBinaryName = "cswitch";
		if (platform.system() == "Windows"):
		#
			cswitchBinaryName = "cswitch.exe";
		#
		elif (platform.system() == "Darwin"):
		#
			# NOTE: On OSX it's quite painful to set up the PATH environment variable globall for GUI applications
			#       So for the time being we just hard-code the absolute path
			cswitchBinaryName = "/Users/robbitay/my/bin/cswitch.app/Contents/MacOS/cswitch";
		#
		subprocess.Popen([cswitchBinaryName, fileName, "-top", "-size=(220,350)"]);

	#
#