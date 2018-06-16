import asyncio
import websockets
import minisocket

ws = minisocket.SocketClient(host='localhost:8765',url='/hello/minhtuan')
def hello(ws):
    greeting = '?'
    while greeting != 'exit':
        name = input("What's your name? ")
        ws.send(name)
        greeting = ws.recv()
        print(f"< {greeting}")
        if name == 'exit':
            break;

hello(ws)

ws = minisocket.SocketClient(host='localhost:8765', url='/xinchao')
hello(ws)
# async def hello():
#     async with websockets.connect('ws://localhost:8765/hello') as websocket:
#         greeting = '?'
#         while greeting != 'exit':
#             name = input("What's your name? ")
#             await websocket.send(name)
#             greeting = await websocket.recv()
#             print(f"< {greeting}")
