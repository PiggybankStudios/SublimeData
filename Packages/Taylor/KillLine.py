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
		remRegions = []
		newSelections = []
		for region in self.view.sel():
		#
			# print("Region:", region)
			row, col = self.view.rowcol(region.b)
			lineRegion = self.view.full_line(region)
			endRow, endCol = self.view.rowcol(lineRegion.end())
			newLineRegion = self.view.line(self.view.text_point(endRow, 0))
			
			if (newLineRegion.size() >= col):
			#
				endPosition = self.view.text_point(endRow, col)
			#
			else:
			#
				endPosition = self.view.text_point(endRow, newLineRegion.size())
			#
			
			newSelections.append(endPosition)
			if (lineRegion not in remRegions):
			#
				print("Killing line %d" % (row+1))
				remRegions.append(lineRegion)
			#
			else: print("Already removing line %d" % (row+1))
		#
		
		self.view.window().status_message("Killed %d line(s)" % len(remRegions))
		for rIndex in range(len(remRegions)):
		#
			self.view.erase(edit, remRegions[rIndex])
			# Shift all the regions above us down by the amount deleted
			for rIndex2 in range(rIndex+1, len(remRegions)):
			#
				if (remRegions[rIndex2].a >= remRegions[rIndex].end()): remRegions[rIndex2].a -= (remRegions[rIndex].end() - remRegions[rIndex].begin())
				if (remRegions[rIndex2].b >= remRegions[rIndex].end()): remRegions[rIndex2].b -= (remRegions[rIndex].end() - remRegions[rIndex].begin())
			#
		#
		
		self.view.sel().clear()
		for selection in newSelections:
		#
			newLocation = selection
			selectionRemoved = False
			for remRegion in remRegions:
			#
				if (remRegion.begin() <= newLocation and remRegion.end() > newLocation):
				#
					# print("Selection at %d removed" % selection)
					selectionRemoved = True
					break
				#
				elif (remRegion.begin() < newLocation):
				#
					newLocation -= remRegion.end() - remRegion.begin()
					if (newLocation <= 0): print("Warning, newLocation went negative") # This shouldn't happen
				#
			#
			if (selectionRemoved):
			#
				continue
			#
			else:
			#
				# print("Selection at %d->%d added" % (selection, newLocation))
				self.view.sel().add(sublime.Region(newLocation, newLocation))
			#
		#
	#
#
