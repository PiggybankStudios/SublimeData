import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

# This command attempts to jump to the next scope match from the cursor
# It can be used to jump between Function/Class definitions or any other syntax scope
# If select_whole is true it will also set the selection to the extent of the matching scope text (e.g. the whole function name)
# If show_centered is true it will bring the match into the center of the screen
# If loop_around is true then the function will loop around the end of the file to the beginning (or vice versa)
class GotoNextScopeCommand(sublime_plugin.TextCommand):
#
	def run(self, edit, forward=True, loop_around=False, scope_match="entity.", show_only=False, select_whole=True, show_centered=True):
	#
		scopeMatchLen = len(scope_match)
		
		selections = self.view.sel()
		if (len(selections) != 1):
		#
			print("More than one selection. Cannot goto next")
			return
		#
		
		startIndex = selections[0].b
		cIndex = startIndex
		
		success = False
		foundNonMatch = False
		foundFirst = False
		firstIndex = 0
		lastIndex = 0
		while (True):
		#
			scopes = SplitScopesString(self.view.scope_name(cIndex))
			# print("Scopes: " + str(scopes))
			
			isMatch = False
			for scope in scopes:
			#
				if (len(scope) >= scopeMatchLen and scope[0:scopeMatchLen] == scope_match):
				#
					isMatch = True
					break
				#
			#
			
			if (isMatch):
			#
				if (foundNonMatch and foundFirst == False):
				#
					foundFirst = True
					firstIndex = cIndex
					if (forward == False):
					#
						firstIndex += 1
						if (loop_around and firstIndex >= self.view.size()): firstIndex = 0
					#
					print("Start Find: %u" % firstIndex)
				#
			#
			else:
			#
				foundNonMatch = True
				if (foundFirst):
				#
					lastIndex = cIndex
					if (forward == False):
					#
						lastIndex += 1
						if (loop_around and lastIndex >= self.view.size()): lastIndex = 0
					#
					print("End find: %u" % lastIndex)
					success = True
					break
				#
			#
			
			if (forward):
			#
				cIndex += 1
				if (cIndex >= self.view.size()):
				#
					if (loop_around): cIndex = 0
					else: break
				#
			#
			else:
			#
				cIndex -= 1
				if (cIndex < 0):
				#
					if (loop_around): cIndex = self.view.size()-1
					else: break
				#
			#
			
			if (cIndex == startIndex): break
		#
		
		# NOTE: If the match extends all the way to the end of the file
		#		then we need to handle that case here
		if (foundFirst and success == False):
		#
			if (cIndex < 0):
			#
				lastIndex = 0
				success = True
			#
			elif (cIndex >= self.view.size()):
			#
				lastIndex = self.view.size()
				success = True
			#
			else:
			#
				print("Not sure exactly how we got here...")
			#
		#
		
		newRegion = sublime.Region(min(firstIndex, lastIndex), min(firstIndex, lastIndex))
		if (select_whole):
		#
			newRegion = sublime.Region(max(firstIndex, lastIndex), min(firstIndex, lastIndex))
		#
		regionStr = self.view.substr(newRegion)
		self.view.window().status_message("Found %s" % regionStr)
		if (success):
		#
			if (show_centered):
			#
				self.view.show_at_center(newRegion.b)
			#
			else:
			#
				self.view.show(newRegion.b)
			#
			
			if (show_only == False):
			#
				self.view.sel().clear()
				self.view.sel().add(newRegion)
			#
		#
		else:
		#
			self.view.window().status_message("No Matching Scopes Found")
		#
	#
#
