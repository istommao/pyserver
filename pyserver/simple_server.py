"""pyserver simple_server."""
from wsgiref.simple_server import WSGIRequestHandler

from base.httpserver import BaseHttpServer

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
