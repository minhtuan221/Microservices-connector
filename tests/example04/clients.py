import asyncio
import websockets


async def hello():
    async with websockets.connect('ws://localhost:8765/abcdzyx') as websocket:
        name = input("What's your name? ")
        print(f"> {name}")
        greeting = await websocket.recv()
        print(f"< {greeting}")
        while greeting != 'close':
            await websocket.send(name)
            greeting = await websocket.recv()
            print(f"< {greeting}")
            name = input("What's your name? ")

asyncio.get_event_loop().run_until_complete(hello())
