import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

# This command expects the cursor to be selecting the name of an enumeration in the form
# enum |EnumerationName_t| // The | | characters represent the selection
# {
# 	EnumerationName_Value0 = 0,
# 	EnumerationName_Value1,
# 	...
# }
# It will then generate a function like:
# const char* GetEnumerationNameStr(EnumerationName_t enumerationName)
# {
# 	switch (enumerationName)
# 	{
# 		case EnumerationName_Value0: return "Value0";
# 		case EnumerationName_Value1: return "Value1";
# 		...
# 		default: return "Unknown";
# 	}
# }
class GenereateEnumStrFuncCommand(sublime_plugin.TextCommand):
#
	def run(self, edit):
	#
		selections = self.view.sel();
		if (len(selections) != 1):
		#
			print("More than one selection. Cannot GenereateEnumStrFunc");
			return;
		#
		if (selections[0].a == selections[0].b):
		#
			print("Nothing is selected. Cannot GenereateEnumStrFunc");
			return;
		#
		selectionRowA, selectionColA = self.view.rowcol(selections[0].a);
		selectionRowB, selectionColB = self.view.rowcol(selections[0].b);
		if (selectionRowA != selectionRowB):
		#
			print("The selection spans across multiple lines. This isn't supported. Cannot GenereateEnumStrFunc");
			return;
		#
		
		enumTypeStr = self.view.substr(selections[0]);
		enumBaseStr = enumTypeStr;
		if (enumBaseStr.endswith("_t")): enumBaseStr = enumBaseStr[0:-2];
		# print("Enumeration %s (%s)" % (enumBaseStr, enumTypeStr));
		
		openCurlyRow = selectionRowA+1;
		openCurlyLineStr = GetLineStr(self.view, openCurlyRow, True);
		if (openCurlyLineStr != "{"):
		#
			print("Expected to find open curly bracket on next line after selection. Instead we found \"%s\". Cannot GenereateEnumStrFunc" % (openCurlyLineStr));
			return;
		#
		# print("Open curly bracket is on line %d (selection on line %d)" % (openCurlyRow+1, selectionRowA+1));
		
		enumSuffixes = [];
		maxSuffixLength = 0;
		closeCurlyRow = openCurlyRow+1;
		while (True):
		#
			if (self.view.text_point(closeCurlyRow, 0) == self.view.size()):
			#
				print("Found end of file before finding closing curly bracket line for enum. Cannot GenereateEnumStrFunc");
				return;
			#
			closeCurlyLineStr = GetLineStr(self.view, closeCurlyRow, True);
			# print("Line %d: \"%s\"" % (closeCurlyRow, closeCurlyLineStr));
			if (closeCurlyLineStr == "};"):
			#
				# print("Closing curly bracket is on line %d" % (closeCurlyRow+1));
				break;
			#
			else:
			#
				enumStr = StripCppComment(closeCurlyLineStr);
				if (len(enumStr) > 0):
				#
					if (enumStr.endswith(",")): enumStr = enumStr[0:-1];
					if (enumStr.startswith(enumBaseStr)):
					#
						enumStr = StripEverythingAfterFirstSpace(enumStr);
						enumSuffixStr = enumStr[len(enumBaseStr):];
						enumSuffixes.append(enumSuffixStr);
						if (not enumSuffixStr.startswith("_Num") and maxSuffixLength < len(enumSuffixStr)):
						#
							maxSuffixLength = len(enumSuffixStr);
						#
					#
				#
			#
			closeCurlyRow += 1;
		#
		
		if (len(enumSuffixes) == 0):
		#
			print("No valid enum value lines found between open and close curly brackets (line %d to %d)" % (openCurlyRow+1, closeCurlyRow+1));
		#
		
		# print("Found %d enum values:\n%s" % (len(enumSuffixes), enumSuffixes));
		
		enumVarName = "enumValue"; #TODO: Make this better?
		funcCode = "const char* Get%sStr(%s %s)\n" % (enumBaseStr, enumTypeStr, enumVarName);
		funcCode += "{\n";
		funcCode += "\tswitch (%s)\n" % (enumVarName);
		funcCode += "\t{\n";
		for enumSuffix in enumSuffixes:
		#
			if (enumSuffix.startswith("_Num")): continue;
			numSpacesNeeded = maxSuffixLength - len(enumSuffix);
			enumSuffixNoUnderscore = enumSuffix;
			if (enumSuffixNoUnderscore.startswith("_")): enumSuffixNoUnderscore = enumSuffixNoUnderscore[1:];
			funcCode += "\t\tcase %s: %sreturn \"%s\";\n" % (enumBaseStr + enumSuffix, " " * numSpacesNeeded, enumSuffixNoUnderscore);
		#
		funcCode += "\t\tdefault: return \"Unknown\";\n";
		funcCode += "\t}\n";
		funcCode += "}";
		# print("Function:\n%s" % (funcCode));
		
		closeCurlyLineRegion = self.view.line(self.view.text_point(closeCurlyRow, 0))
		insertPoint = closeCurlyLineRegion.end();
		self.view.insert(edit, insertPoint, "\n" + funcCode);
	#
#