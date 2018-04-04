import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

import hashlib

# Replaces all selected regions with the MD5 hash of the text in HEX
class Md5HashCommand(sublime_plugin.TextCommand):
	def run(self, edit):
	#
		for region in self.view.sel():
		#
			regionStr = self.view.substr(region)
			md5Hash = hashlib.md5(regionStr.encode("utf-8")).hexdigest()
			self.view.replace(edit, region, md5Hash)
		#
	#
#