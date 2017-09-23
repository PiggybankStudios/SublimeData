import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

# If the cursor is within the quotation marks or angle brackets of a C #include line
# then this command will attempt to extract the file name and open up the goto window
# with the file name pre-entered
class OpenStringFileCommand(sublime_plugin.TextCommand):
#
	def want_event(self):
	#
		return True
	#
	
	def run(self, edit, event = None, forcePos = None):
	#
		region = self.view.sel()[0]
		# If we were passed an event we want to look at the point
		# that was clicked on by the mouse instead of selected points
		if (event != None):
		#
			textPos = self.view.window_to_text([event['x'], event['y']])
			region = sublime.Region(textPos, textPos)
		#
		if (forcePos != None):
		#
			region = sublime.Region(forcePos, forcePos)
		#
		
		fileName = GetCString(self.view, region)
		
		if (len(fileName) > 0):
		#
			print("Opening file overlay for filename \"" + fileName + "\"")
			targetGroup = (self.view.window().active_group() + 1) % self.view.window().num_groups()
			self.view.window().focus_group(targetGroup)
			self.view.window().run_command("show_overlay", 
				{"overlay": "goto", "show_files": True, "text": fileName})
		#
	#
	
	# This function determines whether this command shows up in the context menu
	def is_visible(self, event = None):
	#
		region = self.view.sel()[0]
		# If we were passed an event we want to look at the point
		# that was clicked on by the mouse instead of selected points
		if (event != None):
		#
			textPos = self.view.window_to_text([event['x'], event['y']])
			region = sublime.Region(textPos, textPos)
		#
		
		return LineIsInclude(self.view, region)
	#
#

# This listener works in tandem with the OpenStringFileCommand to provide a little
# helpful window that shows up when hovering over a C #include line
class IncludeHoverEventListener(sublime_plugin.ViewEventListener):
#
	def OnPopupLinkClicked(self, link):
	#
		self.view.window().run_command("show_overlay", {"overlay": "goto", "show_files": True, "text": link})
	#

	def on_hover(self, point, hover_zone):
	#
		region = sublime.Region(point, point);
		if (hover_zone == sublime.HOVER_TEXT and
		#
			LineIsInclude(self.view, region)):
			# print("Line is #include!")
			fileName = GetCString(self.view, region)
			if (len(fileName) > 0):
			#
				htmlCode = ("<p style=\"padding:0px;margin:0px\">#included file:</p>" + 
					"<a href=\"" + fileName +"\">" + 
					fileName + "</a>?")
				self.view.show_popup(htmlCode, 
					sublime.HIDE_ON_MOUSE_MOVE_AWAY, point, 
					100000, 10000, self.OnPopupLinkClicked)
			#
		#
	#
#

