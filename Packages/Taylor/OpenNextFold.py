import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

class OpenNextFoldCommand(sublime_plugin.TextCommand):
#
	def run(self, edit, reverse=False):
	#
		for region in self.view.sel():
		#
			currentPos = region.b
			if (reverse and currentPos > 0): currentPos -= 1
			while (True):
			#
				if (reverse == False and currentPos >= self.view.size()):
				#
					print("Found end of file")
					break
				#
				if (reverse == True and currentPos <= 0):
				#
					print("Found beginning of file")
					break
				#
				
				unfoldResult = self.view.unfold(sublime.Region(currentPos, currentPos+1))
				# print("[%u]: %s" % (currentPos, unfoldResult))
				if (len(unfoldResult) > 0):
				#
					print("Unfolded region starting at %u" % (currentPos))
					break
				#
				
				if (reverse): currentPos -= 1
				else: currentPos += 1
			#
		#
	#
#