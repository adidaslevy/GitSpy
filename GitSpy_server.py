#!/usr/bin/python
'''
server for GitSpy agents to aggregate
'''

from BaseHTTPServer import BaseHTTPRequestHandler
import sys
from os import path
from xml.etree.ElementTree import *
import xml.etree.ElementTree as ET


AGGREGATION_FILE 	= "/var/log/GitSpy/commitAggregations.xml"
ALL_COMMITS			= "allcommits"

ip = "127.0.0.1"
port = 3006

tree = ElementTree()

class GetHandler(BaseHTTPRequestHandler):
	def __return_response(self,data=None):
		self.send_response(200)
		self.end_headers()
		if data:
			self.wfile.write(data)

	def __return_error(self, msg="error"):
		self.send_response(400)
		self.end_headers()
		self.wfile.write(msg)
        
	def do_GET(self):
		return
    
	def do_POST(self):
		'''
		Client communicates with server via post, 
		So, aggregation actually done in this method. 
		'''
		global tree
		
		try:
			bodyLen = int(self.headers['Content-Length']) 
			body = self.rfile.read(bodyLen)
			commit = ET.fromstring(body)
			
			tree.append(commit)
			tree.write(AGGREGATION_FILE)
			self.__return_response()
		except Exception as e:
			print str(e)
			self.__return_error('something went wrong ' + str(e))
      
		return


def main():
	global tree
	from BaseHTTPServer import HTTPServer	
	# Check if file exists, if not, create it
	if (not path.exists(AGGREGATION_FILE)):
		file = open(AGGREGATION_FILE, 'w')
		file.close()
	try:
		tree.parse(AGGREGATION_FILE)
	except:
		print ("xml file doesn't exists, exiting")
		sys.exit(1)

	# check that the root element exists, if not, create it.
	
	# run server
	try:
		server = HTTPServer((ip,port), GetHandler)
		print 'Starting server, use <Ctrl-C> to stop'
		server.serve_forever()
	except KeyboardInterrupt:
		print '^C received, shutting down server'
		server.socket.close()


if __name__ == '__main__':
	
	main()

