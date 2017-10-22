import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

import collections
import functools
import html
import subprocess
import threading
import time

windowsDefaultBuildSettings = {
	"cmd": "build.bat",
	"working_dir": "$project_path",
	"error_relative_dir": "",
	"syntax": "Packages/TaylorAddons/MSVC Build.sublime-syntax",
	
	"error_regex": '''([^\\n\(]*)\((\d+)\)\:\s?(?:fatal\s)?(?:error)\s?\w\d+\:\s*(.+)''',
	"error_match_groups": ["file_name", "line_number", "message"],
	"error_phantom_color": "#9E0038",
	"default_error_message": "An error occurred here!",
	
	"warning_regex": '''([^\\n\(]*)\((\d+)\)\:\s?(?:fatal\s)?(?:warning)\s?\w\d+\:\s*(.+)''',
	"warning_match_groups": ["file_name", "line_number", "message"],
	"warning_phantom_color": "#95880B",
	"default_warning_message": "Warning!",
	
	"show_output_panel": True,
	"output_word_wrap": False,
	"output_line_numbers": True,
	"show_error_phantoms": True,
}

class ProcessListener(object):
#
	def HandleData(self, process, data): pass
	def ProcessFinished(self, process): pass
#

class AsyncProcess(object):
#
	def __init__(self, listener, buildSettings, envVars, outputPanel):
	#
		self.listener = listener
		self.killed = False
		self.startTime = time.time()
		
		startupInfo = None
		if os.name == "nt":
		#
			startupInfo = subprocess.STARTUPINFO()
			startupInfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
		#
		
		processEnv = os.environ.copy()
		for key, value in processEnv.items(): processEnv[key] = os.path.expandvars(value)
		
		if (sys.platform == "win32"):
		#
			self.process = subprocess.Popen(buildSettings["cmd"],
				stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
				startupinfo=startupInfo, env=processEnv, shell=True)
		#
		elif (sys.platform == "darwin"):
		#
			self.process = subprocess.Popen(buildSettings["cmd"],
				stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
				startupinfo=startupInfo, env=processEnv, shell=False)
		#
		elif (sys.platform == "linux"):
		#
			self.process = subprocess.Popen(["/bin/bash", "-c", buildSettings["cmd"]],
				stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
				startupinfo=startupInfo, env=processEnv, shell=False)
		#
		else:
		#
			self.process = subprocess.Popen(buildSettings["cmd"],
				stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
				startupinfo=startupInfo, env=processEnv, shell=False)
		#
		
		if (self.process.stdout): threading.Thread(target=self.HandleStdOut).start()
		if (self.process.stderr): threading.Thread(target=self.HandleStdErr).start()
	#
	
	def Kill(self):
	#
		if (self.killed == False):
		#
			self.killed = True
			
			if (sys.platform == "win32"):
			#
				#NOTE: Terminate would not kill the process opened by the shell cmd.exe,
				#      It would only kill cmd.exe leaving the child running
				startupInfo = subprocess.STARTUPINFO()
				startupInfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
				subprocess.Popen("taskkill /PID " + str(self.process.pid), startupinfo=startupInfo)
			#
			else:
			#
				self.process.terminate()
			#
			self.listener = None
		#
	#
	
	def HandleStdOut(self):
	#
		while (True):
		#
			data = os.read(self.process.stdout.fileno(), 2**15)
			
			if (len(data) > 0):
			#
				if (self.listener): self.listener.HandleData(self, data)
			#
			else:
			#
				self.process.stdout.close()
				if (self.listener): self.listener.ProcessFinished(self)
				break
			#
		#
	#
	
	def HandleStdErr(self):
	#
		while (True):
		#
			data = os.read(self.process.stderr.fileno(), 2**15)
			
			if (len(data) > 0):
			#
				if (self.listener): self.listener.HandleData(self, data)
			#
			else:
			#
				self.process.stderr.close()
				break
			#
		#
	#
	
	def Poll(self): return (self.process.poll() is None)
	def ExitCode(self): return self.process.poll()
#

class TaylorBuildCommand(sublime_plugin.WindowCommand, ProcessListener):
#
	BLOCK_SIZE = 2**14
	textQueue = collections.deque()
	textQueueProcess = None
	textQueueLock = threading.Lock()
	
	process = None
	
	errorsByFile = {}
	phantomSetsByBuffer = {}
	showErrorsInline = True
	
	def run(self, kill=False, update_phantoms_only=False, hide_phantoms_only=False):
	#
		if (update_phantoms_only):
		#
			if (self.showErrorsInline): self.UpdatePhantoms()
			return
		#
		if (hide_phantoms_only):
		#
			self.HidePhantoms()
			return
		#
		
		# +==============================+
		# |     Clear the Text Queue     |
		# +==============================+
		self.textQueueLock.acquire()
		try:
		#
			self.textQueue.clear()
			self.textQueueProcess = None
		#
		finally: self.textQueueLock.release()
		
		# +==============================+
		# |         Kill Request         |
		# +==============================+
		if (kill):
		#
			if (self.process):
			#
				self.process.Kill()
				self.process = None
				self.PushOnQueue(None, "[Cancelled]")
			#
			return
		#
		
		# +==============================+
		# |      Aquire Information      |
		# +==============================+
		window = self.window
		activeView = window.active_view()
		projectFilePath, projectDirectory, projectFileName, projectBaseName, projectExtension = SafeSplitPath(window.project_file_name())
		fileFilePath, fileDirectory, fileFileName, fileBaseName, fileExtension = SafeSplitPath(activeView.file_name())
		
		# +==============================+
		# |    Environment variables     |
		# +==============================+
		self.envVars = {
			"packages": sublime.packages_path(),
			"file_path": fileDirectory,
			"file_name": fileFileName,
			"file_base_name": fileBaseName,
			"file_extension": fileExtension,
			"file": fileFilePath,
			"project_path": projectDirectory,
			"project_name": projectFileName,
			"project_base_name": projectBaseName,
			"project_extension": projectExtension,
			"project": projectFilePath,
		}
		# print("Environment Variables: ", FormattedDictionaryStr(self.envVars))
		# print ("Current Working Directory: ", os.getcwd()) # Returned "C:\Users\robbitay\AppData\Roaming\Sublime Text 3\Packages"
		
		# +==============================+
		# |        Build Settings        |
		# +==============================+
		global windowsDefaultBuildSettings
		global osxDefaultBuildSettings
		global linuxDefaultBuildSettings
		
		if (sys.platform == "win32"): # Windows
		#
			self.buildSettings = windowsDefaultBuildSettings.copy()
		#
		elif (sys.platform == "darwin"): # OSX
		#
			self.buildSettings = osxDefaultBuildSettings.copy()
		#
		elif (sys.platform == "linux"): # Linux
		#
			self.buildSettings = linuxDefaultBuildSettings.copy()
		#
		else:
		#
			print("Unknown platform!")
			return
		#
		
		#Grab the project build_option overrides
		projectSettings = GetProjectSettings(window)
		if (projectSettings != None and projectSettings["build_options"] != None):
		#
			self.buildSettings.update(projectSettings["build_options"])
		#
		
		# Process working_dir option
		self.buildSettings["working_dir"] = FillDollarVariables(self.buildSettings["working_dir"], self.envVars)
		if (self.buildSettings["working_dir"] == ""): self.buildSettings["working_dir"] = fileDirectory
		if (self.buildSettings["working_dir"] == ""): self.buildSettings["working_dir"] = projectDirectory
		
		# Process error_relative_dir option
		# if (self.buildSettings["error_relative_dir"] == ""):
		
		print("Build Settings: " + FormattedDictionaryStr(self.buildSettings))
		
		# +==============================+
		# |         Output Panel         |
		# +==============================+
		if (not hasattr(self, "outputPanel")):
			self.outputPanel = window.create_output_panel("taylor_build")
		
		#NOTE: The result_file_regex and related settings are what determine how the F4 and Shift+F4 shortcuts
		#      work. Eventually we'll want to replace this functionality with our own
		self.outputPanel.settings().set("result_file_regex", self.buildSettings["error_regex"])
		self.outputPanel.settings().set("result_line_regex", "")
		self.outputPanel.settings().set("result_base_dir", self.buildSettings["working_dir"])
		self.outputPanel.settings().set("word_wrap", self.buildSettings["output_word_wrap"])
		self.outputPanel.settings().set("line_numbers", self.buildSettings["output_line_numbers"])
		self.outputPanel.settings().set("gutter", self.buildSettings["output_line_numbers"])
		self.outputPanel.settings().set("scroll_past_end", False)
		self.outputPanel.assign_syntax(self.buildSettings["syntax"])
		
		# Call create_output_panel a second time after assigning the above
		# settings, so that it'll be picked up as a result buffer
		window.create_output_panel("taylor_build")
		
		if (self.buildSettings["show_output_panel"]):
		#
			window.run_command("show_panel", {"panel": "output.taylor_build"})
		#
		
		self.HidePhantoms()
		self.showErrorsInline = self.buildSettings["show_error_phantoms"]
		
		# +==============================+
		# |            Build             |
		# +==============================+
		sublime.status_message("Building...")
		
		if (self.buildSettings["working_dir"] != ""): os.chdir(self.buildSettings["working_dir"])
		
		try:
		#
			self.process = AsyncProcess(self, self.buildSettings, self.envVars, self.outputPanel)
			
			self.textQueueLock.acquire()
			try: self.textQueueProcess = self.process
			finally: self.textQueueLock.release()
		#
		except Exception as e:
		#
			self.PushOnQueue(None, "Exception while trying to launch async build script!")
			self.PushOnQueue(None, "Cmd: \"%s\"" % (self.buildSettings["cmd"]))
			self.PushOnQueue(None, str(e))
		#
	#
	
	# +--------------------------------------------------------------+
	# |                  Process Listener Callbacks                  |
	# +--------------------------------------------------------------+
	# Called from the asynchronous process when data is received from the build process
	def HandleData(self, process, data):
	#
		try: characters = data.decode("utf-8")
		except:
		#
			characters = "[Decode error - output not utf-8]\n"
			process = None
		#
		
		# Normalize line endings
		characters = characters.replace("\r\n", "\n").replace("\r", "\n")
		
		self.PushOnQueue(process, characters)
	#
	
	def ProcessFinished(self, process):
	#
		# Start the Finish function on another thread
		sublime.set_timeout(functools.partial(self.Finish, process), 0)
	#
	
	# +--------------------------------------------------------------+
	# |                       Class Functions                        |
	# +--------------------------------------------------------------+
	# Pushes a string onto the Queue and then activates ServiceQueue if needs be
	def PushOnQueue(self, process, string):
	#
		wasEmpty = False
		
		self.textQueueLock.acquire()
		try:
		#
			if (process != self.textQueueProcess):
			#
				#NOTE: A second call to TaylorBuild has been made before the first one finished
				#      Ignore it instead of intermingling the output
				if (process): process.kill()
				return
			#
			
			if (len(self.textQueue) == 0):
			#
				wasEmpty = True
				self.textQueue.append("")
			#
			
			numBytesAvail = self.BLOCK_SIZE - len(self.textQueue[-1])
			
			if (len(string) < numBytesAvail):
			#
				cur = self.textQueue.pop()
				self.textQueue.append(cur + string)
			#
			else:
			#
				self.textQueue.append(string)
			#
		#
		finally: self.textQueueLock.release()
		
		#If the queue was empty then we need to startup the ServiceQueue thread again
		if (wasEmpty): sublime.set_timeout(self.ServiceQueue, 0)
	#
	
	# Takes data from the queue and processes it, showing it on the outputPanel and finding errors
	def ServiceQueue(self):
	#
		isEmpty = False
		
		self.textQueueLock.acquire()
		try:
		#
			# This will happen if a new build was started, which will clear the textQueue
			if (len(self.textQueue) == 0): return
			
			characters = self.textQueue.popleft()
			isEmpty = (len(self.textQueue) == 0)
		#
		finally: self.textQueueLock.release()
		
		self.outputPanel.run_command("append", {"characters": characters, "force": True, "scroll_to_end": True})
		
		# Find lines that match the error_regex
		if (self.buildSettings["show_error_phantoms"] and characters.find('\n') >= 0):
		#
			errors = self.SearchOutputWithRegex(self.buildSettings["error_regex"], self.buildSettings["error_match_groups"])
			for error in errors: error["type"] = "error"
			# print("%u Errors Found: %s" % (len(errors), str(errors)))
			
			warnings = self.SearchOutputWithRegex(self.buildSettings["warning_regex"], self.buildSettings["warning_match_groups"])
			for warning in warnings: warning["type"] = "warning"
			# print("%u Warnings Found: %s" % (len(warnings), str(warnings)))
			
			errors.extend(warnings)
			
			errorsByFile = {}
			for e in errors:
			#
				if (e["file_name"] not in errorsByFile): errorsByFile[e["file_name"]] = []
				errorsByFile[e["file_name"]].append(e)
			#
			self.errorsByFile = errorsByFile
			# print("Errors by file: ", self.errorsByFile)
			
			
			self.UpdatePhantoms()
		#
		
		# We need to get called again to continue processing the queue
		if (not isEmpty): sublime.set_timeout(self.ServiceQueue, 1)
	#
	
	def Finish(self, process):
	#
		elapsedTime = time.time() - process.startTime
		exitCode = process.ExitCode()
		
		if (exitCode == 0 or exitCode == None): self.PushOnQueue(process, "[Finished in %.1fs]" % elapsedTime)
		else:                                   self.PushOnQueue(process, "[Finished in %.1f with exit code %d]\n" % (elapsedTime, exitCode))
		
		if (process != self.process): return
		
		errors = self.outputPanel.find_all_results()
		if (len(errors) == 0): sublime.status_message("Build finished")
		else:                  sublime.status_message("Build finished with %d errors" % (len(errors)))
	#
	
	def SearchOutputWithRegex(self, regularExpression, matchGroups):
	#
		results = []
		
		matchRegions = self.outputPanel.find_all(regularExpression)
		# print("Found %u match regions:" % (len(matchRegions)))
		for mIndex in range(0, len(matchRegions)):
		#
			matchRegion = matchRegions[mIndex]
			regionStr = self.outputPanel.substr(matchRegion)
			# print("\tMatch[%u]: \"%s\"" % (mIndex, regionStr))
			match = re.search(regularExpression, regionStr)
			if (match != None):
			#
				# print("\tGroups: " + str(match.groups()))
				numGroups = len(match.groups())
				expectedNumGroups = len(matchGroups)
				
				if (numGroups == expectedNumGroups):
				#
					newResult = {}
					
					for gIndex in range(0, numGroups):
					#
						groupStr = match.group(gIndex+1)
						groupType = matchGroups[gIndex]
						
						if (groupType == "line_number"):
						#
							try:
							#
								intValue = int(groupStr)
								newResult["line_number"] = intValue
							#
							except ValueError:
							#
								print("Group[%u] was not a line_number: \"%s\"" % (gIndex, groupStr))
								newResult
							#
						#
						elif (groupType == "column"):
						#
							try:
							#
								intValue = int(groupStr)
								newResult["column"] = intValue
							#
							except ValueError:
							#
								print("Group[%u] was not a column: \"%s\"" % (gIndex, groupStr))
							#
						#
						elif (groupType == "file_name"):
						#
							newResult["file_name"] = groupStr
						#
						elif (groupType == "message"):
						#
							newResult["message"] = groupStr
						#
						else:
						#
							print("Group[%u] has an unknown type defined in build options: \"%s\"" % (gIndex, groupType))
						#
					#
					
					if ("file_name" in newResult and "line_number" in newResult):
					#
						results.append(newResult)
					#
					else:
					#
						print("Match did not produce a valid file_name and line_number")
					#
				#
				else:
				#
					print("Regex produced %u groups instead of expected %u groups" % (numGroups, expectedNumGroups))
					print("Groups:", match.groups())
				#
			#
			else: print("\tre.search returned None!")
		#
		
		return results
	#
	
	def UpdatePhantoms(self):
	#
		base_stylesheet = '''
			<style>
				div.error {
					padding: 0.1rem 0 0.1rem 0.7rem;
					margin: 0.0rem 0;
					border-radius: 2px;
					background-color: $background_color;
				}
				div.error span.message {
					padding-right: 0.7rem;
				}
				div.error a {
					text-decoration: inherit;
					padding: 0.35rem 0.7rem 0.45rem 0.8rem;
					position: relative;
					bottom: 0.05rem;
					border-radius: 0 2px 2px 0;
					font-weight: bold;
				}
				html.dark div.error a {
					background-color: #00000030;
				}
				html.light div.error a {
					background-color: #ffffff00;
				}
			</style>
		'''
		
		
		
		for fileName, errorList in self.errorsByFile.items():
		#
			view = self.window.find_open_file(fileName)
			if (view != None):
			#
				bufferId = view.buffer_id()
				if (bufferId not in self.phantomSetsByBuffer):
				#
					print("Creating new phantom set for buffer %d" % (bufferId))
					phantomSet = sublime.PhantomSet(view, "taylor_build")
					self.phantomSetsByBuffer[bufferId] = phantomSet
				#
				else:
				#
					phantomSet = self.phantomSetsByBuffer[bufferId]
				#
				
				phantomList = []
				
				for error in errorList:
				#
					line = 0
					column = 0
					message = ""
					if (error["type"] == "error"): message = html.escape(self.buildSettings["default_error_message"], quote=False)
					if (error["type"] == "warning"): message = html.escape(self.buildSettings["default_warning_message"], quote=False)
					
					if ("line_number" in error): line    = error["line_number"]
					if ("column"      in error): column  = error["column"]
					if ("message"     in error): message = html.escape(error["message"], quote=False)
					
					stylesheet = base_stylesheet
					if (error["type"] == "error"):
					#
						stylesheet = base_stylesheet.replace("$background_color", self.buildSettings["error_phantom_color"])
					#
					elif (error["type"] == "warning"):
					#
						stylesheet = base_stylesheet.replace("$background_color", self.buildSettings["warning_phantom_color"])
					#
					
					textPoint = view.text_point(line-1, column)
					region = sublime.Region(textPoint, view.line(textPoint).b)
					content  = '<body id=inline-error>'
					content += stylesheet;
					content += '<div class="error">'
					content += '<span class="message">' + message + '</span>'
					content += '<a href=hide>' + chr(0x00D7) + '</a>'
					content += '</div>'
					content += '</body>'
					
					print("Adding phantom to file %d \"%s\" at %u: " % (bufferId, fileName, textPoint))
					# print("\t", content)
					
					phantomList.append(sublime.Phantom(region, content, sublime.LAYOUT_BELOW, on_navigate=self.on_phantom_navigate))
				#
				
				phantomSet.update(phantomList)
			#
		#
	#
	
	def HidePhantoms(self):
	#
		print("Hiding phantoms in %u files" % (len(self.errorsByFile)))
		for fileName, errorList in self.errorsByFile.items():
		#
			view = self.window.find_open_file(fileName)
			# print("Looking for view for file \"%s\"" % (fileName))
			if (view != None):
			#
				# print("Erasing phantoms from view %d" % (view.buffer_id()))
				view.erase_phantoms("taylor_build")
			#
		#
		
		self.errorsByFile = {}
		self.phantomSetsByBuffer = {}
		self.showErrorsInline = False
	#
	
	# +--------------------------------------------------------------+
	# |                Sublime Plugin Implementations                |
	# +--------------------------------------------------------------+
	# Lets sublime know whether or not this command is ready to be run
	def is_enabled(self, kill=False, **kwargs):
	#
		if (kill): return (self.process is not None) and self.process.poll()
		else: return True
	#
	
	def on_phantom_navigate(self, url):
	#
		self.HidePhantoms()
	#
#

class TaylorBuildEventListener(sublime_plugin.EventListener):
#
	def on_load(self, view):
	#
		window = view.window()
		if (window != None): window.run_command("taylor_build", {"update_phantoms_only": True})
	#
#
