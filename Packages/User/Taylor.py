import os, sys, sublime, sublime_plugin
sys.path.append(os.path.dirname(__file__))
from User.MyFunctions import *

class TaylorCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		print("Running the Taylor Command!")
		
		for region in self.view.sel():
			selectionStr = self.view.substr(region)
			# print("Selection: \"" + selectionStr + "\"")
			
			function = CppFunction(selectionStr)
			if (function.valid):
				print("Parsed Function:", function)
			else:
				print("Could not parse function: \"%s\"" % (selectionStr))
	#end of Def
#End of TaylorCommand