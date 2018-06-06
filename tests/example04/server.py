import asyncio
import websockets
import spawn
import threading, time
from microservices_connector.Interservices import Microservice
Micro = Microservice(__name__)

async def hello(websocket, path):
    name = await websocket.recv()
    print(f"< {name}")

    greeting = f"Hello {name}!"

    await websocket.send(greeting)
    print(f"> {greeting}")

def socket_run():
    print('websocket is starting')
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_server = websockets.serve(hello, 'localhost', 8765)
    loop.run_until_complete(start_server)
    loop.run_forever()

@Micro.typing('/', methods=['GET'])
def string1():
    time.sleep(2)
    return 'Sleep 2s before response'

def flask_app():
    Micro.run(port=5000, host='0.0.0.0')

if __name__ == '__main__':
    # t = threading.Thread(target=flask_app)
    # t.start()
    s = threading.Thread(target=socket_run)
    s.start()
    flask_app()
# asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.get_event_loop().run_forever()
