import sublime
import sublime_plugin
import re

class GrabNextCommand(sublime_plugin.TextCommand):
	def run(self, edit, case_sensitive=True, forward=True, word_bounded=False):
		selections = self.view.sel()
		if (selections == None or len(selections) == 0):
			print("No selections!")
			return
		
		lastRegion = selections[-1]
		lastRegionStr = self.view.substr(lastRegion)
		
		regexFlags = 0
		regexStr = re.escape(lastRegionStr)
		if (case_sensitive == False):
			regexFlags = sublime.IGNORECASE
		if (word_bounded):
			regexStr = "\\b" + regexStr + "\\b"
		# print("Regular expression: " + str(regexStr))
		
		if (forward):
			findResult = self.view.find(regexStr, lastRegion.end(), regexFlags)
			
			if (findResult.a == -1): # No result found
				findResult = self.view.find(regexStr, 0, regexFlags)
				
				while (findResult.a != -1 and findResult in selections and findResult.begin() < lastRegion.begin()):
					findResult = self.view.find(regexStr, findResult.end(), regexFlags)
				
				if (findResult.a == -1):
					print("Selection doesn't exist anywhere else")
					return
				if (findResult.begin() >= lastRegion.begin()):
					print("All instances selected")
					return
			
		else:
			print("Backward search currently isn't supported")
			return
		
		if (findResult in selections):
			print("Next item is already selected")
			return
		
		self.view.sel().add(findResult)


