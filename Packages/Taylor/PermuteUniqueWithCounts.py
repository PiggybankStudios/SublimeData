import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

class PermuteUniqueWithCountsCommand(sublime_plugin.TextCommand):
#
	def run(self, edit, undo=False):
	#
		for region in self.view.sel():
		#
			uniqueLines = [];
			uniqueLinesCounts = {};
			regionStr = self.view.substr(region);
			if (len(regionStr) == 0): continue;
			lines = regionStr.splitlines(keepends=False);
			
			for line in lines:
			#
				if (line in uniqueLinesCounts):
				#
					uniqueLinesCounts[line] = uniqueLinesCounts[line] + 1;
				#
				else:
				#
					uniqueLines.append(line);
					uniqueLinesCounts[line] = 1;
				#
			#
			
			lineIndex = 0;
			replacementText = "";
			for uniqueLine in uniqueLines:
			#
				if (lineIndex > 0): replacementText += "\n";
				replacementText += "%s x%d" % (uniqueLine, uniqueLinesCounts[uniqueLine]);
				lineIndex += 1;
			#
			self.view.replace(edit, region, replacementText);
		#
	#
#
