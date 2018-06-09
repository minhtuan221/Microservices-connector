import asyncio
import websockets


async def hello():
    async with websockets.connect('ws://localhost:8765/hello') as websocket:
        greeting = '?'
        while greeting != 'exit':
            name = input("What's your name? ")
            await websocket.send(name)
            greeting = await websocket.recv()
            print(f"< {greeting}")

asyncio.get_event_loop().run_until_complete(hello())
