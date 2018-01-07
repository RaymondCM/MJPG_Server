#!/usr/bin/python
import socket
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
from urlparse import urlparse
from camera import Camera
from time import sleep


class CamHandler(BaseHTTPRequestHandler):
    def __init__(self, capture, *args):
        self.capture = capture
        self.content = open('index.html', 'r').read()
        BaseHTTPRequestHandler.__init__(self, *args)

    def do_GET(self):
        url = urlparse("http://{}:{}{}".format(self.client_address[0], self.client_address[1], self.path))
        if url.path.endswith('.mjpg'):
            while True:
                try:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/jpeg')
                    self.end_headers()
                    self.wfile.write(self.capture.get_frame())
                    if url.query.startswith("dt="):
                        break
                except socket.error as ex:
                    print("Pipe closed: " + ex.args[1] if len(ex.args >= 2) else "")
                    break
            return
        elif self.path.endswith('.html'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.content)
            return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


def main():
    ip = "0.0.0.0"
    port = 8080

    try:
        def handler(*args):
            CamHandler(Camera(), *args)

        server = ThreadedHTTPServer((ip, port), handler)

        print("Server Started on " + ip + ":" + str(port))
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()


if __name__ == '__main__':
    main()
