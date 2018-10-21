import os, sys, sublime, sublime_plugin, random
from Taylor.Functions import *

class HillCipherCommand(sublime_plugin.TextCommand):
#
	def run(self, edit):
	#
		characters = [
			'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
			'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
		]
		# message = [
		# 	 62,  32,  45,   0,  49,  33,  44,  21,   0,  47,  49,  26,  24,  15,  38,  28,  32,  45,  51, 26,   6,  49,  24,  36,  37,   3,
		# 	165,  84, 115,   0, 124,  90, 112,  55,   0, 122, 132,  65,  67,  45, 105,  70,  90, 120, 135, 65,  17, 127,  63,  93,  97,   9
		# ]
		message = [
			 34,  54,  23,  54,  63,  57,  87,  36, 105,  63, 100,   9,  55, 117, 115,   0, 169,
			 67,  65, 124,  45,  83, 135,  25, 134,  63,  79,  99, 100,  27, 107,  43,  50, 124,
			 39,  48, 160,  27,  90, 137,   0,  72, 122,  80, 114, 158, 104,  69,  10,  99,  70,
			 54,  13,  18,   9,  21,  23,  21,  32,  13,  42,  25,  40,   3,  19,  46,  45,   0,  63,  25,
			 22,  48,  15,  29,  50,  10,  51,  21,  31,  38,  40,   9,  40,  16,  17,  46,  13,  19,  60,
			  9,  33,  52,   0,  27,  45,  32,  43,  59,  41,  26,   4,  37,  25,  18
		]
		# matrix = [
		# 	1, 0, #0, 0,
		# 	0, 1#, 0, 0,
		# 	#0, 0, 1, 0,
		# 	#0, 0, 0, 1
		# ]
		matrix = [
			2, -5,
			-1, 3
		]
		print(len(message))
		print(self.FindMultiples(len(message)))
		decoded = self.MultMatrix(matrix, message, 2)
		self.PrintMatrix(decode d, 2, True)
		if (self.IsValidMessage(decoded)): print("Valid!")
		else: print("Invalid")
		
		for i in range(0, 10000):
		#
			key = [
				random.randint(-20, 20), random.randint(-20, 20),# random.randint(-20, 20), random.randint(-20, 20),
				random.randint(-20, 20), random.randint(-20, 20)# random.randint(-20, 20), random.randint(-20, 20),
				#random.randint(-20, 20), random.randint(-20, 20), random.randint(-20, 20), random.randint(-20, 20),
				#random.randint(-20, 20), random.randint(-20, 20), random.randint(-20, 20), random.randint(-20, 20)
			]
			result = self.MultMatrix(key, message, 2)
			if (self.IsValidMessage(result)):
			#
				print("Decoded with: ")
				self.PrintMatrix(key, 2, False)
				print("=>")
				self.PrintMatrix(result, 2, True)
			#
			else:
			#
				if ((i%1000) == 0): print("Tried %u" % (i))
				# self.PrintMatrix(key, 2, False)
				# print("=>")
				# self.PrintMatrix(result, 2, True)
			#
		#
		print("Done")
	#
	
	def MultMatrix(self, matrix, message, matrixSize):
	#
		messageColumns = (int)(len(message) / matrixSize)
		results = []
		for row in range(0, matrixSize):
		#
			for column in range(0, messageColumns):
			#
				entry = 0
				for i in range(0, matrixSize):
				#
					entry += self.GetEntry(matrix, matrixSize, row, i) * self.GetEntry(message, matrixSize, i, column)
				#
				results.insert((row * messageColumns) + column, entry)
			#
		#
		return results
	#
	
	def GetEntry(self, matrix, numRows, row, column):
	#
		numColumns = (int)(len(matrix) / numRows)
		return matrix[row * numColumns + column]
	#
	
	def PrintMatrix(self, matrix, numRows, useChars):
	#
		numColumns = (int)(len(matrix) / numRows)
		for row in range(0, numRows):
		#
			sys.stdout.write("[")
			for column in range(0, numColumns):
			#
				entryValue = self.GetEntry(matrix, numRows, row, column)
				if (useChars and entryValue >= 0 and entryValue <= 26):
				#
					if (entryValue == 0): sys.stdout.write("    ")
					else: sys.stdout.write(" %3c" % (chr(ord('A') + entryValue-1)))
				#
				else:
				#
					sys.stdout.write(" %3u" % (entryValue))
				#
			#
			sys.stdout.write(" ]\n")
		#
	#
	
	def FindMultiples(self, number):
	#
		results = []
		for i in range(2, number):
		#
			if ((number%i) == 0):
				results.append(i)
		#
		return results
	#
	
	def IsValidMessage(self, matrix):
	#
		for i in range(0, len(matrix)):
		#
			if (matrix[i] > 26 or matrix[i] < 0): return False
		#
		return True
	#
#
