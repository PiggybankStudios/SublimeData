import os, sys, sublime, sublime_plugin
from Taylor.Functions import *

import os.path
import platform
import fnmatch

class MoveTabBetweenGroupsCommand(sublime_plugin.WindowCommand):

	def run(self, right):
	#
		view = self.window.active_view();
		(group, index) = self.window.get_view_index(view);
		if index < 0: return;
		numGroups = self.window.num_groups();
		if (right):
		#
			if (group+1 < numGroups): group += 1;
			elif (group > 0): group = 0;
			else: return;
		#
		else:
		#
			if (group > 0): group -= 1;
			elif (numGroups > 1): group = numGroups-1;
			else: return;
		#
		print("Moving tab %d to group %d" % (index, group));
		newGroupViewCount = len(self.window.views_in_group(group));
		newViewIndex = newGroupViewCount;
		self.window.set_view_index(view, group, newViewIndex);
		self.window.focus_group(group);
		self.window.focus_view(view);
	#
	
	def is_enabled(self):
	#
		view = self.window.active_view();
		if view == None: return False;
		(group, index) = self.window.get_view_index(view);
		return len(self.window.views_in_group(group)) > 1;
	#

	def is_visible(self):
	#
		return True;
	#

	def description(self):
	#
		return None;
	#