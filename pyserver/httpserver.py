"""pyserver http."""
from wsgiref import simple_server
from wsgiref.simple_server import WSGIRequestHandler


class BaseHttpServer(simple_server.WSGIServer):
    """Base http server."""

    request_queue_size = 10

    def __init__(self, *args, ipv6=False, allow_reuse_address=True, **kwargs):
        if ipv6:
            self.address_family = socket.AF_INET6
        self.allow_reuse_address = allow_reuse_address
        super().__init__(*args, **kwargs)

    def handle_error(self, request, client_address):
        if is_broken_pipe_error():
            logger.info("- Broken pipe from %s\n", client_address)
        else:
            super().handle_error(request, client_address)


if __name__ == '__main__':
    try:
        print('http://127.0.0.1:3500/')
        server_address = ('127.0.0.1', 3500)

        def demo_app(environ, start_response):
            retdata = 'Hello world!'.encode('utf-8')

            start_response(
                "200 OK", [('Content-Type', 'text/plain; charset=utf-8')]
            )
            return iter([retdata])

        httpd = BaseHttpServer(server_address, WSGIRequestHandler)

        httpd.set_app(demo_app)
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
