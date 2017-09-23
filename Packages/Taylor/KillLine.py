import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

# This command simply removes the line that each cursor currently resides on.
# If it resides on multiple it will kill all the lines it touches.
# We also attempt to place the cursor on the next line following the one killed
# at the same column that it was before you killed the line.
class KillLineCommand(sublime_plugin.TextCommand):
#
	def run(self, edit, next_line=True):
	#
		newRegions = [];
		for region in self.view.sel():
		#
			row, col = self.view.rowcol(region.b);
			lineRegion = self.view.full_line(region);
			endRow, endCol = self.view.rowcol(lineRegion.end());
			newLineRegion = self.view.line(self.view.text_point(endRow, 0));
			
			if (newLineRegion.size() >= col):
			#
				endPosition = self.view.text_point(endRow, col);
			#
			else:
			#
				endPosition = self.view.text_point(endRow, newLineRegion.size());
			#
			
			print("Row " + str(row) + ", Col " + str(col));
			print("End: Row " + str(endRow) + ", Col " + str(endCol));
			print("End Pos: " + str(endPosition));
			
			newRegion = sublime.Region(endPosition, endPosition);
			# newRegions.append(newRegion);
			self.view.sel().add(newRegion);
			self.view.sel().subtract(region);
			
			self.view.erase(edit, lineRegion);
			# self.view.sel().add(lineRegion);
		#
		
		# self.view.sel().clear();
		# self.view.sel().add_all(newRegions);
	#
#
