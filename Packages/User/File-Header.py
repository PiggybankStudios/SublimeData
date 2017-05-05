import sublime
import sublime_plugin

class CreateFileHeaderCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		