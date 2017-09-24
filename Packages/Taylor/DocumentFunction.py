import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

import re

class DocumentFunctionCommand(sublime_plugin.TextCommand):
#
	def run(self, edit, single_line_comments=False):
	#	
		singleCommentStr = GetSingleCommentStr(self.view, 0)
		blockCommentStartStr, blockCommentEndStr = GetBlockCommentStrs(self.view, 0)
		if (blockCommentStartStr == "" or blockCommentEndStr == ""):
		#
			single_line_comments = True
		#
		
		newSelections = []
		for region in self.view.sel():
		#
			regionStr = self.view.substr(region)
			
			function = CppFunction(regionStr)
			if (function.valid):
			#
				selectionBegin = 0
				selectionEnd = 0
				documentStr = ""
				if (single_line_comments == False): documentStr += blockCommentStartStr + "\n"
				
				if (single_line_comments): documentStr += singleCommentStr
				paramStr = ""
				for paramName in function.parameters:
				#
					if (paramStr != ""): paramStr += ", "
					paramStr += paramName
				#
				documentStr += "Function: " + function.name + "(" + paramStr + ")\n"
				
				if (single_line_comments): documentStr += singleCommentStr
				documentStr += "Description:\n"
				
				if (single_line_comments): documentStr += singleCommentStr
				documentStr += "\t** "
				selectionBegin = len(documentStr)
				documentStr += "No description"
				selectionEnd = len(documentStr)
				documentStr += "\n"
				
				if (len(function.parameters) > 0):
				#
					if (single_line_comments): documentStr += singleCommentStr
					documentStr += "Parameters:\n"
					
					longestName = 0
					for paramName in function.parameters:
					#
						if (len(paramName) > longestName): longestName = len(paramName)
					#
					
					longestType = 0
					for paramType in function.parameterTypes:
					#
						if (len(paramType) > longestType): longestType = len(paramType)
					#
					
					for pIndex in range(0, len(function.parameters)):
					#
						paramName = function.parameters[pIndex]
						paramType = function.parameterTypes[pIndex]
						if (paramType == ""): paramType = "void"
						
						if (single_line_comments): documentStr += singleCommentStr
						documentStr += "\t-" + paramType + ":"
						if (len(paramType) < longestType): documentStr += " " * (longestType - len(paramType))
						documentStr += " " + paramName
						if (len(paramName) < longestName): documentStr += " " * (longestName - len(paramName))
						documentStr += " ** Description\n"
					#
				#
				
				if (function.returnType != "" and function.returnType != "void"):
				#
					if (single_line_comments): documentStr += singleCommentStr
					documentStr += "Returns:\n"
					
					if (single_line_comments): documentStr += singleCommentStr
					documentStr += "\t-" + function.returnType + ": ** Description\n"
				#
				
				if (single_line_comments == False): documentStr += blockCommentEndStr + "\n"
				
				# print("Documentation:\n", documentStr)
				
				insertPos = self.view.line(region).begin()
				self.view.insert(edit, insertPos, documentStr)
				newSelections.append(sublime.Region(insertPos + selectionBegin, insertPos + selectionEnd))
			#
		#
		
		self.view.sel().clear()
		self.view.sel().add_all(newSelections)
	#
#