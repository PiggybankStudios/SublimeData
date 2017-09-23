import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

import re

# This command moves each cursor to the next empty line from where it's currently at
# It's designed to be a general purpose command with lots of options that can be set
class MoveToEmptyLineCommand(sublime_plugin.TextCommand):
#
	def run(self, edit, forward=True, expand_selection=False, show_at_center=True):
	#
		newSelections = []
		for region in self.view.sel():
		#
			originPos = region.b
			originRow, originColumn = self.view.rowcol(originPos)
			currentLine = "somethingNotEmpty";
			currentRow = originRow;
			foundBeginning = False;
			foundEnd = False;
			while (not LineIsEmpty(currentLine)):
			#
				if (forward): currentRow += 1;
				else: currentRow -= 1;
				
				if (currentRow < 0):
				#
					currentRow = 0;
					foundBeginning = True;
					print("Found beginning of file");
					break;
				#
				
				pos = self.view.text_point(currentRow, 0);
				currentLine = self.view.substr(self.view.line(pos));
				
				if (pos == self.view.size()):
				#
					print("Found end of file");
					foundEnd = True;
					break;
				#
			#			
			print("Found line " + str(currentRow+1));
			
			if (foundBeginning): newPos = 0;
			elif (foundEnd): newPos = self.view.size();
			else:
			#
				lineLength = len(currentLine)
				newPos = self.view.text_point(currentRow, lineLength);
			#
			
			if (expand_selection):
			#
				newRegion = sublime.Region(region.a, newPos);
			#
			else:
			#
				newRegion = sublime.Region(newPos, newPos);
			#
			newSelections.append(newRegion);
		#
		
		self.view.sel().clear();
		self.view.sel().add_all(newSelections);
		
		if (show_at_center and len(newSelections) == 1):
		#
			self.view.show(newSelections[0].b);
		#
	#
#
