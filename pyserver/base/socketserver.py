"""pyserver socketserver."""
import http.client

import shutil
import socket
import socketserver


class BaseServer:

    address_family = socket.AF_INET

    socket_type = socket.SOCK_STREAM

    allow_reuse_address = False

    request_queue_size = 5

    def __init__(self, server_address, RequestHandlerClass):
        self.server_address = server_address
        self.RequestHandlerClass = RequestHandlerClass

        self.socket = socket.socket(self.address_family,
                                    self.socket_type)
        try:
            if self.allow_reuse_address:
                self.socket.setsockopt(
                    socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(self.server_address)

            self.socket.listen(self.request_queue_size)
        except:
            self.socket.close()
            raise

    def serve_forever(self, poll_interval=0.5):
        try:
            self._handle_request_noblock()
        finally:
            pass

    def _handle_request_noblock(self):
        try:
            request, client_address = self.socket.accept()
        except OSError:
            return

        try:
            self.process_request(request, client_address)
        except:
            self.close_request(request)
            raise

    def process_request(self, request, client_address):
        self.RequestHandlerClass(request, client_address, self)

    def close_request(self, request):
        request.close()


class BaseRequestHandler:

    rbufsize = -1
    wbufsize = 0

    # A timeout to apply to the request socket, if not None.
    timeout = None

    # Disable nagle algorithm for this socket, if True.
    # Use only when wbufsize != 0, to avoid small packets.
    disable_nagle_algorithm = False

    def __init__(self, request, client_address, server):
        self.request = request
        self.client_address = client_address
        self.server = server
        self.setup()
        try:
            self.handle()
        finally:
            self.finish()

    def setup(self):
        self.connection = self.request
        if self.timeout is not None:
            self.connection.settimeout(self.timeout)
        if self.disable_nagle_algorithm:
            self.connection.setsockopt(socket.IPPROTO_TCP,
                                       socket.TCP_NODELAY, True)
        self.rfile = self.connection.makefile('rb', self.rbufsize)
        if self.wbufsize == 0:
            self.wfile = socketserver._SocketWriter(self.connection)
        else:
            self.wfile = self.connection.makefile('wb', self.wbufsize)

    def handle(self):
        """Handle multiple requests if necessary."""
        self.close_connection = True

        self.handle_one_request()
        while not self.close_connection:
            self.handle_one_request()

    def finish(self):
        if not self.wfile.closed:
            try:
                self.wfile.flush()
            except socket.error:
                # A final socket error may have occurred here, such as
                # the local error ECONNABORTED.
                pass
        self.wfile.close()
        self.rfile.close()

    def handle_one_request(self):
        self.raw_requestline = self.rfile.readline(65537)

        f = None
        try:
            shutil.copyfileobj(f, self.wfile)
        finally:
            f.close()

        self.wfile.flush()  # actually send the response if not already done.
