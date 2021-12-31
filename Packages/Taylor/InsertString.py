import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

# This command inserts a specified string at each cursor
class InsertStringCommand(sublime_plugin.TextCommand):
#
	def run(self, edit, string="[Unfinished Binding]"):
	#
		for region in self.view.sel():
		#
			self.view.sel().subtract(region);
			self.view.replace(edit, region, string);
			self.view.sel().add(sublime.Region(region.b + len(string), region.b + len(string)));
		#
	#
#
