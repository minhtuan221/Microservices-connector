import asyncio
import os
import traceback
import threading
import websockets
import websocket
import uvloop
import time
import threading
from microservices_connector.url_parser.url_namespace import ArgsParse


def SocketClient(host='localhost:8765', url='/'):
    return websocket.create_connection(f'ws://{host}{url}')


class SocketServer(threading.Thread):
    def __init__(self, name=__file__):
        threading.Thread.__init__(self)
        self.name = name
        self.url = {}
        self.url_args = {}
        self.timeout = 1000*1000*60

    def router(self, rule):
        def response(handler):
            self.add_route(rule, handler)
            return handler
        return response

    route = router

    def add_route(self, rule, handler, middleware=None):
        if middleware is None:
            middleware = self.basic_middleware
        args = ArgsParse(rule)
        if args.is_hashable():
            self.url[rule] = handler, middleware
        else:
            self.url_args[rule] = handler, middleware

    async def basic_middleware(self, websocket, handler, *args):
        message = '?'
        while message != 'exit':
            message = await websocket.recv()
            reply = handler(message, *args)
            if reply is not None:
                await websocket.send(reply)

    async def handle_immutalble_route(self, websocket, path, *args):
        handler, middleware = self.url[path]
        await middleware(websocket, handler, *args)

    async def handle_mutalble_route(self, websocket, path, *args):
        handler, middleware = self.url_args[path]
        await middleware(websocket, handler, *args)

    async def connect(self, websocket, path):
        # check if url is immutalble or contain args
        if path in self.url:
            await self.handle_immutalble_route(websocket, path)
        else:
            matched_rule = None
            for rule in self.url_args:
                args = ArgsParse(rule)
                if args.parse(path) is not None:
                    matched_rule = rule
                    break
            if matched_rule:
                    await self.handle_mutalble_route(websocket, rule, *args.parse(path))
            else:
                await websocket.send('Websocket close: path does not exist')

    def server(self, host='127.0.0.1', port=8765):
        print("Starting socket in %s:%s" % (host, port))
        loop = uvloop.new_event_loop()
        asyncio.set_event_loop(loop)
        start_server = websockets.serve(self.connect, host, port)
        loop.run_until_complete(start_server)
        loop.run_forever()

    def run(self, host='127.0.0.1', port=8765):
        s = threading.Thread(target=self.server, args=(host, port))
        s.daemon = True
        s.start()


def main():
    sk = SocketServer(__name__)

    @sk.router('/hello')
    def test(message):
        print(message)
        return 'ok:'+message
    sk.run()


if __name__ == '__main__':
    main()
