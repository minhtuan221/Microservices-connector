import asyncio
import websockets

from cython_npm.cythoncompile import require
minisocket = require('../../microservices_connector/minisocket')

# ws = minisocket.SocketClient(host='localhost:8765',url='/hello/minhtuan')
def hello(ws):
    greeting = '?'
    while greeting != 'exit':
        name = input("What's your name? ")
        ws.send(name)
        greeting = ws.recv()
        print(f"< {greeting}")
        if name == 'exit':
            break

# hello(ws)

ws = minisocket.SocketClient(host='localhost:8765', url='/render')
ws.send('test render socket')
x = ws.recv()
# ws.send('other things')
# ws.send('other things')
ws.send(None)
print(x)
