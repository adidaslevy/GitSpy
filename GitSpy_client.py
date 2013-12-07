#!/usr/bin/python

'''
Date: 07-Dec-2013
Written By: Adi Levy
Description: This GitSpy client will be activated upon 2 hooks:
	* post-commit hook - get the list of files, and changes that being done in files, along with commit message
	
	The log will be rendered to XML file, and once all messages are in, will send the file to a remote overlord server. 
'''
import sys
import subprocess
import urllib2
from xml.etree.ElementTree import *
import ConfigParser
from git import *

CONFIG			= ".GitSpy_agent.ini"
REPO_SECTION 	= "repository"
SERVER_SECTION	= "server"


def ReadConfiguration(section):
	config = ConfigParser.ConfigParser()
	config.read(CONFIG)
	if (not config.has_section(section)):
		print "Cannot run GitSpy - Configuration file corrupted"
		sys.exit(1)

	# return item lists
	return config.items(section)
	
def GatherCommitContent(repoName):
	'''
	This function creates a data structure with all commit information gathered on last commit done
	The Data structure will consist:
	author name
	commit date
	[path:(ablob, bblob), path:(ablob,bblob)....]

	Note: taking the blobs to later diff between them using git command line, as diff property doesn't return the diff text.
	'''
	repo = Repo(repoName)
	commitList = list(repo.iter_commits())
	author = commitList[0].author
	date = commitList[0].committed_date
	message = commitList[0].message
	
	# Gather all diffs, and absolute paths
	diffInfo = {}
	for x in commitList[0].diff(commitList[1]):
		ablob = None
		bblob = None
		absPath = ""
		
		if (x.a_blob is not None):
			# grab a side info
			ablob = x.a_blob
			absPath = x.a_blob.abspath

		if (x.b_blob is not None):
			# grsb b side info
			bblob = x.a_blob
			absPath = x.b_blob.abspath 
		diffInfo[absPath] = (ablob, bblob)

	return (author, date, message, diffInfo)

def constructChangeXML(author, date, message, diffInfo):
	''' 
	This function will form the following XML structure:
	<commit author=AUTHOR_NAME date=commited_date message=message>
		<item name=FILE_NAME>
			file diff
		</item>
		<item name=FILE_NAME>
			file diff
		</item>
	</commit>
	
	And will save it to a file, where configuration stated
	'''
	diffTree = ElementTree()
	commitElem = Element('commit', {'author':author, 'date':date, 'message':message})
	for diff in diffInfo:
		diffElem = element('diff', {'path':diff})
		
		# get the diff text from git, using the blobs
		command = ['git', 'diff']
		command.append(diffInfo[diff][0])
		command.append(diffInfo[diff][1])
		try:
			cmd = subprocess.Popen(command, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		except OSError:
			logger.error("Command: " + command + " Doesn't exist.")
			print "Command: " + command + " Doesn't exist. "
			sys.exit(1)
		except ValueError:
			logger.error("Unable to create a subprocess, please contact your system administrator, skipping post work")
			print "Unable to create a subprocess, please contact your system administrator, skipping post work"
			sys.exit(1)

		out,err = cmd.communicate()

		if (cmd.returncode != 0):
			logger.error("Command: " + commandForLog + " returned an error, : " + str(err))
			print "Command: " + commandForLog + " returned an error, : " + str(err)  
			sys.exit(1)
		
		diffElem.text = out
		commitElem.append(diffElem)
	diffTree._setroot(commitElem)
	return diffTree

def TransmitCommit(post_data):
	'''
	This function gets content to transmit to server
	server details are read from config file
	'''
	(ip, port) = ReadConfiguration(SERVER_SECTION)
	try:
		urllib2.urlopen('http://{0}:{1}/'.format(ip, port), post_data)
	except urllib2.URLError, e:
		status = 1
		msg = error('Failed to transmit commit data: {0}'.format(e))

	if status:
		print "Status: 400 {0}".format(msg)
    
	else:
		print ''.format(status, msg)
		print '</vps.device.response>'
		
def main():

	# Get repository path/name
	repoConfigItems = ReadConfiguration(REPO_SECTION)
	(author, date, message, diffinfo) = GatherCommitContent(repoConfigItems["repository_name"])

	# build the xml for transmission
	tree = constructChangeXML(author, date, message, diffinfo)

	# transmit
	transmitCommit(tree)
	
	
	
		

if __name__ == '__main__':
	main()
