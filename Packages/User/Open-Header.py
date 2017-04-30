import sublime
import sublime_plugin
import os
import os.path
import platform
import fnmatch


def compare_file_names(x, y):
	if platform.system() == 'Windows' or platform.system() == 'Darwin':
		return x.lower() == y.lower()
	else:
		return x == y

class OpenHeaderCommand(sublime_plugin.TextCommand):
	def run(self, edit, extensions=[]):
		if not self.view.window().active_view():
			return
		
		filePath = self.view.window().active_view().file_name()
		if not filePath:
			return
		
		base, ext = os.path.splitext(filePath)
		baseDir, fileName = os.path.split(base)
		
		start = 0
		count = len(extensions)
		
		if ext != "":
			ext = ext[1:]
			
			for index in range(0, len(extensions)):
				if compare_file_names(extensions[index], ext):
					start = index + 1
					count -= 1
					break
		
		# Look for the file in the same folder
		for index in range(0, count):
			idx = (start + index) % len(extensions)
			
			new_path = base + '.' + extensions[idx]
			
			if os.path.exists(new_path):
				self.window.open_file(new_path, flags=sublime.FORCE_GROUP)
				return
		
		projectFolders = None
		projectData = self.view.window().project_data()
		if (projectData != None):
			projectFolders = projectData['folders']
		
		# Look for the file in the project folders
		for folder in projectFolders:
			for root, dirNames, fileNames in os.walk(folder['path']):
				for index in range(0, count):
					idx = (start + index) % len(extensions)
					lookupFileName = fileName + '.' + extensions[idx]
					
					for newMatch in fnmatch.filter(fileNames, lookupFileName):
						matchPath = os.path.join(root, newMatch)
						self.view.window().open_file(matchPath, flags=sublime.FORCE_GROUP)
						return
			
