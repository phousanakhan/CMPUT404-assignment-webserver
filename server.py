#  coding: utf-8
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

# https://stackoverflow.com/questions/3204782/how-to-check-if-a-file-is-a-directory-or-regular-file-in-python
# check whether directory is path or file


class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()
        # print("Got a request of: %s\n" % self.data)
        # self.request.sendall(bytearray("OK", 'utf-8'))
        data = self.data.decode('utf-8').split('\r\n')
        # print("DAATTAAA: ", data)
        # print("DATA: ", data)
        # print("Referer?: ", data.getHeader("referer"))
        # referer = list(filter(lambda x: x.startswith("Referer"), data))
        # print("REFER LAMBDA: ", referer)
        request = data[0].split()  # ['GET', '/base.css', 'HTTP/1.1']

        path_to_redirect = None
        try:
            #request_referer = data[7].split()[1]
            #print("request_referer:", request_referer, type(request_referer))
            #path_to_redirect = request_referer[21:]
            #print("path to redirect:", path_to_redirect, type(path_to_redirect))

            request_referer = list(
                filter(lambda x: x.startswith("Referer"), data))
            request_referer = request_referer[0].split()[1]
            path_to_redirect = request_referer[21:]
            # print("NEW request_referer:", request_referer_new,
            # type(request_referer_new))
            # print("NEW path to redirect:", path_to_redirect_new,
            # type(path_to_redirect_new))

            # print("path_to_redirect==path_to_redirect_new?:",
            # path_to_redirect == path_to_redirect_new)
            # print(path_to_redirect)
            # print(path_to_redirect_new)
            # request_referer == request_referer_new[0].split()[1])
            # print(request_referer)
            # print(request_referer_new[0].split()[1])
        except Exception:
            request_referer = None

        request_method = request[0]

        # base.css, index.html, basically ==> localhost:8080/whatever, the "/whatever" is request_resource
        request_resource = request[1]

        # handle when css redirect
        # print("IS IT EMPTY path_to_redirect ", path_to_redirect)
        # and path to redirect is not a file *MUST ADD THIS
        if request_resource[-4:] == ".css" and path_to_redirect != None and path_to_redirect[-1] != "/" and len(request_resource) != 1 and os.path.isfile("www"+request_resource) != True:
            if path_to_redirect[-1] != "/":
                path_to_redirect += "/"
            new_path = path_to_redirect+"deep.css"
            self.show_css(new_path)

        # if cannot handle ==> send 405 Method Not Allowed
        if request_method != "GET":
            self.send_405()

        # handle ==> localhost:8080/  ==> this should show index.html
        if len(request_resource) == 1 and request_resource[0] == "/":
            self.show_index_html(request_resource)

        # if the requested resource if a directory
        elif os.path.isdir("www"+request_resource) == True:
            # check if need to send 301 moved permanently or not
            # print("REQUEST_resource if is directory: ", request_resource)
            if request_resource[-1] != "/":
                request_resource += "/"
                self.send_301(request_resource)
            else:
                # it's a regular directory: must return index.html & base.css of that path
                self.show_index_html_in_directory(request_resource)

        # if the requested resouurce is a file
        elif os.path.isfile("www"+request_resource) == True and request_resource:
            if ".html" == request[1][-5:]:
                self.show_index_html(request_resource)

            elif ".css" == request[1][-4:]:
                # print("HERE: ", request[1][-4:])
                self.show_css(request_resource)
            else:
                # handle /../../../../../../../../../../../../etc/group
                self.send_404()
        else:
            # not a file + not a directory ==> must be 404 error
            self.send_404()

    def show_index_html(self, request_resource):
        try:
            if len(request_resource) == 1 and request_resource[0] == "/":
                f = open("www/index.html", 'r')
            else:
                f = open("www"+request_resource, 'r')
            data = f.read()
            len_data = len(data)
            message = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n\r\n"+data
            self.request.sendall(bytearray(message, 'utf-8'))
        except Exception:
            self.send_404()

    def show_css(self, request_resource):
        try:
            f = open("www"+request_resource, 'r')
            # print("SHOW_CSS: ", "www"+request_resource)
            data = f.read()
            len_data = len(data)
            message = "HTTP/1.1 200 OK\r\nContent-Type: text/css\r\n\r\n\r\n"+data
            self.request.sendall(bytearray(message, 'utf-8'))
        except Exception:
            self.send_404()

    def send_405(self):
        data = "405 Method Not Allowed\r\n\r\n"
        message = "HTTP/1.1 405 Method Not Allowed\r\nContent-Type: text/css\r\n\r\n\r\n"+data
        self.request.sendall(bytearray(message, 'utf-8'))

    def send_404(self):
        data = "404 Not Found\r\n\r\n"
        message = "HTTP/1.1 404 Not Found\r\nContent-Type: text/css\r\n\r\n\r\n"+data
        self.request.sendall(bytearray(message, 'utf-8'))

    def send_301(self, request_resource):
        try:
            # request_resource = www/deep/    *already tag on the "/" at the handle() func
            f = open("www"+request_resource+"index.html", 'r')
            data = f.read()
            # len_data = len(data)
            message = "HTTP/1.1 301 Moved Permanently\r\nContent-Type: text/html\r\n\r\n\r\n"+data
            self.request.sendall(bytearray(message, 'utf-8'))
        except Exception:
            self.send_404()

    def show_index_html_in_directory(self, request_resource):
        try:
            f = open("www"+request_resource+"index.html", 'r')
            data = f.read()
            # len_data = len(data)
            message = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n\r\n"+data
            self.request.sendall(bytearray(message, 'utf-8'))
        except Exception:
            self.send_404()


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
