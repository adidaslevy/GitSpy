#!/usr/bin/python

'''
Date: 07-Dec-2013
Written By: Adi Levy
Description: This GitSpy client will be activated upon 2 hooks:
	* pre-commit hook - get the list of files, and changes that being done in files
	* commit-msg hook - get the commit message that user put in.
	
	The log will be rendered to XML file, and once all messages are in, will send the file to a remote overlord server. 
'''
import sys
import re
import subprocess
import os.path
from xml.etree.ElementTree import ElementTree
import ConfigParser

def PreHookActivation():
	''' 
	This function will form the following XML structure:
	<commit author=AUTHOR_NAME>
		<item name=FILE_NAME>
			file diff
		</item>
		<item name=FILE_NAME>
			file diff
		</item>
	</commit>
	
	And will save it to a file, where configuration stated
	'''
	
	tree = ElementTree()
	

def main():
	
	# check with which command line option the client was activated. 
	if (len(sys.argv) < 2):
		sys.exit("Usage: %s <pre|msg>" % sys.argv[0])
	
	if (sys.argv[1] == 'pre'):
		# activated in the pre hook
	elif (sys.argv[1] == 'msg'):
		# activated in the msg hook
	else:
		sys.exit("Activated with wrong parameter")


if __name__ == '__main__':
	main()
