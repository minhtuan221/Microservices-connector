import asyncio
import os

import aiohttp.web

class AioSocket(object):
    def __init__(self,name=None, port: int=5000, host: str='0.0.0.0', debug=None, **kwargs):
        self.port = port
        self.host = host
        self.debug = debug
        self.init_app(name, **kwargs)
    
    def init_app(self, name, **kwargs):
        loop = asyncio.get_event_loop()
        app = aiohttp.web.Application(loop=loop)
        self.app = app

HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8080))


async def testhandle(request):
    return aiohttp.web.Response(text='Test handle')


async def websocket_handler(request):
    print('Websocket connection starting')
    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)
    print('Websocket connection ready')

    async for msg in ws:
        print(msg)
        if msg.type == aiohttp.WSMsgType.TEXT:
            print(msg.data)
            if msg.data == 'close':
                await ws.close()
            else:
                await ws.send_str(msg.data + '/answer')
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())

    print('Websocket connection closed')
    return ws


def main():
    loop = asyncio.get_event_loop()
    app = aiohttp.web.Application(loop=loop)
    app.router.add_route('GET', '/', testhandle)
    # app.router.add_route('GET', '/ws', websocket_handler)
    app.add_routes([aiohttp.web.get('/ws', websocket_handler)])
    aiohttp.web.run_app(app, host=HOST, port=PORT)


if __name__ == '__main__':
    main()
