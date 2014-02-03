#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle, Clinton Wong
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib
import urlparse

def help():
    print "httpclient.py [GET/POST] [URL]\n"

# Edit: Seems dumb to store the HTTP response in 
# a class called HTTPRequest
class HTTPResponse(object):
    def __init__(self, code=200, body="", headers=""):
        self.code = code
        self.body = body
        self.headers = headers

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        # use sockets!
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((host, port))
        return s

    def get_code(self, data):
        code = data.split('\r\n')[0].split(' ')[1]
        return int(code)

    def get_headers(self,data):
        headers = data.split('\r\n\r\n')[0]
        return headers

    def get_body(self, data):
        body = data.split('\r\n\r\n')[1]
        return body

    # read everything from the socket
    # Clinton: had to modify this as this was probably for Python 3.3
    # In Python 2.7, socket.recv puts things into strings
    # Also set a timeout for the socket so it won't hang
    def recvall(self, sock):
        buffer = ""
        done = False
        while True:
            try:
                part = sock.recv(1024)
                if(part == ""):
                    break
                buffer = buffer + part
            except socket.error:
                break
        return buffer

    def GET(self, url, args=None):
        # Why the hell are you using args?

        # Parse the URL
        o = urlparse.urlparse(url)
        socket_url = o.hostname
        
        if(o.port == None):
            # We'll just set a default port of 80 here, if the port isn't specified.
            socket_port = 80
        else:
            socket_port = o.port

        socket = self.connect(socket_url, socket_port)

        # Prepare the HTTP GET
        if(o.path == ""):
            getString = "GET / HTTP/1.1\r\n"
        else:
            getString = "GET " + o.path + " HTTP/1.1\r\n"
        hostHeader = "Host: " + o.hostname + "\r\n"
        acceptHeader = "Accept: */*\r\n"
        connectionHeader = "Connection: close\r\n"

        requestString = getString + hostHeader + acceptHeader + connectionHeader + "\r\n"

        # Then write to the socket!
        socket.send(requestString)

        # Let's see what we get back!
        responseString = self.recvall(socket)

        # Preparing the response object
        code = self.get_code(responseString)
        headers = self.get_headers(responseString)
        body = self.get_body(responseString)

        socket.close()
        return HTTPResponse(code, body, headers)

    def POST(self, url, args=None):
        # We assume that the args will come in as a dictionary.
        if(args.__class__.__name__ != "dict"):
            print "Arguments are not in a dictionary.  Ignoring arguments."
            args = None

        # Parse the URL
        o = urlparse.urlparse(url)
        socket_url = o.hostname
        
        if(o.port == None):
            # We'll just set a default port of 80 here, if the port isn't specified.
            socket_port = 80
        else:
            socket_port = o.port

        socket = self.connect(socket_url, socket_port)

        # Prepare the HTTP POST

        getString = "POST " + o.path + " HTTP/1.1\r\n"
        hostHeader = "Host: " + o.hostname + "\r\n"
        acceptHeader = "Accept: */*\r\n"
        contentTypeHeader = "Content-Type: application/x-www-form-urlencoded\r\n"

        contentString = ""

        # Prepare the arguments
        if(args != None):
            contentString = urllib.urlencode(args)

        contentLengthHeader = "Content-Length: " + str(len(contentString)) + "\r\n"

        requestString = getString + hostHeader + acceptHeader + contentTypeHeader + contentLengthHeader + "\r\n" + contentString

        # Then write to the socket!
        socket.send(requestString)

        # Let's see what we get back!
        responseString = self.recvall(socket)

        # Preparing the response object
        code = self.get_code(responseString)
        headers = self.get_headers(responseString)
        body = self.get_body(responseString)
        socket.close()

        return HTTPResponse(code, body, headers)

    def command(self, url, command="GET", args=None):
        # Format the URL nicely
        if (url[:7] != "http://"):
            url = "http://" + url

        if (command == "POST"):
            response = self.POST( url, args )
        else:
            response = self.GET( url, args )

        return response.headers + "\n\n" + response.body
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1])
    else:
        print client.command( sys.argv[1], command)    
