import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

class FoldAtSameIndentationCommand(sublime_plugin.TextCommand):
#
	def run(self, edit, single_fold=False):
	#
		if (len(self.view.sel()) != 1):
		#
			print("This command only works with 1 selection")
			return
		#
		
		tabSize = self.view.settings().get("tab_size")
		firstSelRegion = self.view.sel()[0]
		firstLineRegion = self.view.line(firstSelRegion.b)
		firstLineStr = self.view.substr(firstLineRegion)
		firstIndentStr = GetLineIndentation(firstLineStr)
		firstIndentAmount = ActualLineLength(tabSize, firstIndentStr)
		
		print("Indentation is %u characters: \"%s\"" % (firstIndentAmount, firstIndentStr))
		
		lastLineRegion = None
		lineRegion = sublime.Region(0, 0)
		lineStr = ""
		lIndex = 0
		foldStarted = False
		foldStartPos = 0
		while (True):
		#
			lineRegion = self.view.line(self.view.text_point(lIndex, 0))
			lineStr = self.view.substr(lineRegion)
			lineIndentStr = GetLineIndentation(lineStr)
			lineIndentAmount = ActualLineLength(tabSize, lineIndentStr)
			
			# print("Line[%u] %u indent: \"%s\"" % (lIndex+1, lineIndentAmount, lineStr))
			
			if (lineIndentAmount > firstIndentAmount or len(lineStr) == 0):
			#
				if (foldStarted == False and lastLineRegion != None and len(lineStr) > 0):
				#
					foldStarted = True
					foldStartPos = lastLineRegion.end()
				#
			#
			else:
			#
				if (foldStarted):
				#
					foldRegion = sublime.Region(foldStartPos, lastLineRegion.end())
					print("Folding region [%u, %u]" % (foldRegion.a, foldRegion.b))
					foldStarted = False
					
					if (single_fold == False or foldStartPos >= firstSelRegion.b):
					#
						self.view.fold(foldRegion)
						
						if (single_fold): break
					#
				#
			#
			
			lastLineRegion = lineRegion
			lIndex += 1
			nextLineRegion = self.view.line(self.view.text_point(lIndex, 0))
			if (nextLineRegion == lineRegion): break
		#
	#
#