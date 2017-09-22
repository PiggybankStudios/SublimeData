import os, sys, sublime, sublime_plugin
from Taylor.Functions import *


def Encrypt(string):
	encryptedStr = ""
	stringLength = len(string)
	for cIndex in range(0, stringLength):
		currentChar = string[cIndex]
		charNum = ord(currentChar)
		newNum = charNum
		if (charNum >= ord('A') and charNum <= ord('Z')):
			newNum += 5
			if (newNum > ord('Z')):
				newNum -= 26
		if (charNum >= ord('a') and charNum <= ord('z')):
			newNum += 5
			if (newNum > ord('z')):
				newNum -= 26
		if (charNum >= ord('0') and charNum <= ord('9')):
			newNum += 5
			if(newNum > ord('9')):
				newNum -= 10
		newChar = chr(newNum)
		encryptedStr += newChar
	
	return encryptedStr

def Decrypt(encryptedStr):
	string = ""
	stringLength = len(encryptedStr)
	for cIndex in range(0, stringLength):
		currentChar = encryptedStr[cIndex]
		charNum = ord(currentChar)
		newNum = charNum
		if (charNum >= ord('A') and charNum <= ord('Z')):
			newNum -= 5
			if (newNum < ord('A')):
				newNum += 26
		if (charNum >= ord('a') and charNum <= ord('z')):
			newNum -= 5
			if (newNum < ord('a')):
				newNum += 26
		if (charNum >= ord('0') and charNum <= ord('9')):
			newNum -= 5
			if(newNum < ord('0')):
				newNum += 10
		newChar = chr(newNum)
		string += newChar
	
	return string

class LetsEncryptCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		for region in self.view.sel():
			encryptedStr = Encrypt(self.view.substr(region))
			self.view.replace(edit, region, encryptedStr)

class LetsDecryptCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		for region in self.view.sel():
			decryptedStr = Decrypt(self.view.substr(region))
			self.view.replace(edit, region, decryptedStr)

# class DecryptHoverListener(sublime_plugin.ViewEventListener):
# 	def on_hover(self, point, hover_zone):
# 		# print("Hovering")
# 		if (hover_zone != sublime.HOVER_TEXT):
# 			return
# 		lineRegion = self.view.line(point)
# 		lineStr = self.view.substr(lineRegion)
# 		# print("\"" + lineStr + "\"")
		
# 		decryptedStr = Decrypt(lineStr)
# 		self.view.show_popup(decryptedStr, 
# 			sublime.HIDE_ON_MOUSE_MOVE_AWAY, 
# 			point, 10000, 10000)
