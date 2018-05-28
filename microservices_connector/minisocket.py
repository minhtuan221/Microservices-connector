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
            message = await websocket.recv()
            while message!='exit':
                message = await websocket.recv()
                reply = handler(message)
                if reply is not None:
                    await websocket.send(reply)
        else:
            await websocket.send('Websocket close: path does not exist')

    def run(self):
        print("Starting socket " + self.name)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_server = websockets.serve(self.connect, 'localhost', 8765)
        loop.run_until_complete(start_server)
        loop.run_forever()

sk = SocketServer(__name__)
@sk.router('/hello')
def test(message):
    print(message)
    return 'ok:'+message

def main():
    sk.run()

if __name__ == '__main__':
    main()
