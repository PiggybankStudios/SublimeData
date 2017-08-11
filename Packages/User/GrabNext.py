import sublime
import sublime_plugin
import re

def RegionInSelections(region, selections):
	for sel in selections:
		if (sel.begin() <= region.begin() and sel.end() >= region.end()):
			return True
		elif (region.begin() <= sel.begin() and region.end() >= sel.end()):
			return True
	
	return False

class GrabNextCommand(sublime_plugin.TextCommand):
	def run(self, edit, case_sensitive=True, forward=True, word_bounded=False, do_selection=True, show_at_center=True, print_success_info=True):
		selections = self.view.sel()
		if (selections == None or len(selections) == 0):
			self.view.window().status_message("No selections!")
			return
		
		lastRegion = selections[-1]
		lastRegionStr = self.view.substr(lastRegion)
		
		if (len(lastRegionStr) == 0):
			self.view.window().status_message("Last selection is empty")
			return
		
		regexFlags = 0
		regexStr = re.escape(lastRegionStr)
		if (case_sensitive == False):
			regexFlags = sublime.IGNORECASE
		if (word_bounded):
			regexStr = "\\b" + regexStr + "\\b"
		# print("Regular expression: " + str(regexStr))
		
		findResults = self.view.find_all(regexStr, regexFlags)
		isSelected = []
		
		numSelected = 0
		firstSelectionIndex = 0
		lastSelectionIndex = 0
		numUnselectedAbove = 0
		numUnselectedMiddle = 0
		numUnselectedBelow = 0
		sIndex = 0
		allSelected = True
		foundFirstSelected = False
		for region in findResults:
			if (RegionInSelections(region, selections)):
				# print("Selected: " + str(region))
				isSelected.append(True)
				numSelected += 1
				if (not foundFirstSelected):
					foundFirstSelected = True
					firstSelectionIndex = sIndex
				lastSelectionIndex = sIndex
				numUnselectedMiddle += numUnselectedBelow
				numUnselectedBelow = 0
				
			else:
				# print("Not Selected: " + str(region))
				isSelected.append(False)
				allSelected = False
				if (foundFirstSelected == False):
					numUnselectedAbove += 1
				else:
					numUnselectedBelow += 1
			
			sIndex += 1
		
		
		if (allSelected):
			self.view.window().status_message("All regions already selected")
			return
		
		foundSelected = False
		if (forward):
			sIndex = 0
		else:
			sIndex = len(findResults)-1
		newSelectionIndex = None
		while (True):
			if (isSelected[sIndex]):
				foundSelected = True
			elif (foundSelected):
				newSelectionIndex = sIndex
				break
			
			if (forward):
				sIndex += 1
				if (sIndex >= len(findResults)):
					sIndex = 0
			else:
				sIndex -= 1
				if (sIndex < 0):
					sIndex = len(findResults)-1
		
		if (newSelectionIndex == None):
			print("ERROR: I don't know how we got here")
			return
		
		if (do_selection):
			self.view.sel().add(findResults[newSelectionIndex])
			numSelected += 1
			if (newSelectionIndex < firstSelectionIndex):
				if (numUnselectedAbove > 1):
					numUnselectedMiddle += numUnselectedAbove-1
				numUnselectedAbove = 0
			elif(newSelectionIndex < lastSelectionIndex):
				numUnselectedMiddle -= 1
			else:
				numUnselectedBelow -= 1
		else:
			print("New Selection: " + str(findResults[newSelectionIndex]))
		
		if (print_success_info):
			self.view.window().status_message("%u/%u Selected: %u above, %u middle, %u below" % (numSelected, len(findResults), numUnselectedAbove, numUnselectedMiddle, numUnselectedBelow))
		
		if (show_at_center):
			self.view.run_command("show_at_center")
		
		# if (forward):
		# 	findResult = self.view.find(regexStr, lastRegion.end(), regexFlags)
			
		# 	if (findResult.a == -1): # No result found
		# 		findResult = self.view.find(regexStr, 0, regexFlags)
				
		# 		while (findResult.a != -1 and findResult in selections and findResult.begin() < lastRegion.begin()):
		# 			findResult = self.view.find(regexStr, findResult.end(), regexFlags)
				
		# 		if (findResult.a == -1):
		# 			print("Selection doesn't exist anywhere else")
		# 			return
		# 		if (findResult.begin() >= lastRegion.begin()):
		# 			print("All instances selected")
		# 			return
			
		# else:
		# 	print("Backward search currently isn't supported")
		# 	return
		
		# if (findResult in selections):
		# 	print("Next item is already selected")
		# 	return
		
		# self.view.sel().add(findResult)


