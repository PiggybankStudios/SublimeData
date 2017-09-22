import os, sys, sublime, sublime_plugin
sys.path.append(os.path.dirname(__file__))
from User.MyFunctions import *

import re

#TODO: Should we handle getting rid of trailing _t on types?
#TODO: Add options to keep leading and trailing _ and trailing _t

class ChangeNamingConventionCommand(sublime_plugin.TextCommand):
	def run(self, edit, convention="upper_first", conserve_prefix=True, conserve_suffix=True):
		for region in self.view.sel():
			originalName = self.view.substr(region)
			if (len(originalName) == 0):
				print("Skipping empty selection")
				continue
			if (not FullyMatchesRegex(originalName, "[A-Za-z_][A-Za-z0-9_ ]*")):
				print("\"" + originalName + "\" is not a valid identifier")
				continue
			
			prefix = ""
			if (conserve_prefix):
				while(originalName[0] == "_"):
					prefix += "_"
					originalName = originalName[1:]
			suffix = ""
			if (conserve_suffix):
				searchResult = re.search("([_]+[A-Za-z0-9 ]?)$", originalName)
				if (searchResult):
					suffix = searchResult.group(1);
					originalName = originalName[:searchResult.start()]
			
			print("Current Text: \"" + originalName + "\"")
			print("Prefix: \"" + prefix + "\"")
			print("Suffix: \"" + suffix + "\"")
			
			nameParts = GetNameParts(originalName)
			# print("Parts: " + str(nameParts))
			
			if (len(nameParts) == 0):
				print("No name parts found")
				continue
			
			newName = originalName
			if (convention == "camel_case"):
				newName = nameParts[0]
				for pIndex in range(1, len(nameParts)):
					newName += UpperFirst(nameParts[pIndex])
			elif (convention == "upper_first"):
				newName = ""
				for newPart in nameParts:
					newName += UpperFirst(newPart)
			elif (convention == "lower_all"):
				newName = ""
				for newPart in nameParts:
					newName += newPart
			elif (convention == "lower_underscores"):
				newName = nameParts[0]
				for pIndex in range(1, len(nameParts)):
					newName += "_" + nameParts[pIndex]
			elif (convention == "upper_underscores"):
				newName = nameParts[0].upper()
				for pIndex in range(1, len(nameParts)):
					newName += "_" + nameParts[pIndex].upper()
			elif (convention == "lower_words"):
				newName = ""
				for newPart in nameParts:
					if (newName != ""):
						newName += " "
					newName += newPart.lower()
			elif (convention == "upper_first_words"):
				newName = ""
				for newPart in nameParts:
					if (newName != ""):
						newName += " "
					newName += UpperFirst(newPart)
			elif (convention == "sentence"):
				newName = ""
				for newPart in nameParts:
					if (newName != ""):
						newName += " "
						newName += newPart.lower()
					else:
						newName += UpperFirst(newPart)
			else:
				print("Unknown convention type: \"" + convention + "\"")
			
			newName = prefix + newName + suffix
			
			print("New Name: \"" + newName + "\"")
			
			self.view.replace(edit, region, newName)
			
			
			
