#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200,header="", body=""):
        self.code = code
        self.header = header
        self.body = body
    
    def __repr__(self):
        return self.header+"\r\n"+self.body

class HTTPClient(object):
    # generator the request with given method host path and args
    def make_request(self,method,host,path,args=None):
        body = None
        if args != None:
            body = urllib.urlencode(args)
        request = method + " " + path
        request += " HTTP/1.1\r\n"
        request += "Host: " + host+"\r\n"
        request += "Accept:*/*\r\n"
        request += "User-Agent:httpclient.py\r\n"
        request += "Connection:close\r\n"
        if body != None or method == "POST":
            request += "Content-Length: "+str(len(str(body)))+"\r\n"
            request += "Content-Type: application/x-www-form-urlencoded\r\n"
        request += "\r\n"
        if body != None:
            request += body
        return request
        
    # get host path and port separately from url
    def get_host_port(self,url):
        if url[0:7].lower() == "http://":
            url = url[7:]
        elif url[0:8].lower() == "https://":
            url = url[8:]
        path_index = len(url)
        port_index = None
        port = 80
        path = "/"
        host = ""
        for i in range(len(url)):
            if url[i] == "/" and path_index == len(url):
                path_index = i
            if url[i] == ":":
                port_index = i
        if port_index== None or path_index<port_index:
            host = url[:path_index]
        else:
            host = url[:port_index]
            port = int(url[port_index+1:path_index])
        if path_index != len(url):
            path = url[path_index:]
        return host,path,port

    # connect to a socket with given host and port
    def connect(self, host, port):
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect((host,port))
        return sock

    def get_code(self, data):
        return int(data.split()[1])

    def get_headers(self,data):
        return data.split("\r\n\r\n")[0]+"\r\n"
        
    def get_body(self, data):
        return data.split("\r\n\r\n")[1]

    # read everything from the socket
    def recvall(self,sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    # send the request with give url,mode and args
    def send_request(self,url,mode,args=None):
        code = 500
        body = ""
       
        host,path,port = self.get_host_port(url)
        sock = self.connect(host,port)
        request = self.make_request(mode,host,path,args)
        sock.sendall(request)
        data = self.recvall(sock)
        code = self.get_code(data)
        header = self.get_headers(data)
        body = self.get_body(data)
        return HTTPResponse(code,header,body)


    def GET(self, url, args=None):
        return self.send_request(url,'GET',args)

    def POST(self, url, args=None):
        return self.send_request(url,'POST',args)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1] )   
