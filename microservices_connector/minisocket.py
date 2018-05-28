import asyncio
import os
import traceback
import threading
import websockets
import uvloop
import time



class SocketServer(threading.Thread):
    def __init__(self, name=__file__):
        threading.Thread.__init__(self)
        self.name = name
        self.url = {}
        self.timeout = 1000*1000*60
    
    def router(self, rule):
        def response(handler):
            self.add_route(rule, handler)
            return handler
        return response
    
    def add_route(self, rule, handler):
        self.url[rule]=handler

    async def connect(self, websocket, path):
        if path in self.url:
            handler = self.url[path]
            message = '?'
            while message!='exit':
                message = await websocket.recv()
                reply = handler(message)
                if reply is not None:
                    await websocket.send(reply)
        else:
            await websocket.send('Websocket close: path does not exist')

    def run(self, host='localhost', port=8765):
        print("Starting socket in %s:%s" % (host,port))
        loop = uvloop.new_event_loop()
        asyncio.set_event_loop(loop)
        start_server = websockets.serve(self.connect, host, port)
        loop.run_until_complete(start_server)
        loop.run_forever()
