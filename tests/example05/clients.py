import asyncio
import websockets


async def hello():
    async with websockets.connect('ws://localhost:8765/hello') as websocket:
        name = input("What's your name? ")
        await websocket.send(name)
        print(f"> {name}")
        greeting = await websocket.recv()
        print(f"< {greeting}")
        while greeting != 'close':
            name = input("What's your name? ")
            await websocket.send(name)
            greeting = await websocket.recv()
            print(f"< {greeting}")

asyncio.get_event_loop().run_until_complete(hello())
