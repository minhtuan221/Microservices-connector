# from minisocket import SocketServer
from microservices_connector.Interservices import Microservice
import threading, time
from cython_npm.cythoncompile import require
SocketServer = require('../../microservices_connector/minisocket').SocketServer

sk = SocketServer(__name__)
app = Microservice('Flask_app').app

@app.route('/')
def helloworld():
    time.sleep(2)
    return 'Sleep 2s before response'


@sk.route('/hello/<name>')
def test(message, name):
    print(message,'hello:'+name)
    return 'hello:'+message


@sk.route('/xinchao')
def test2(message):
    print(message, 'End:')
    return 'xinchao:'+message


@sk.render('/render')
async def test3(ws, message):
    print(message, 'received')
    await ws.send('Render 1:'+message)
    x = await ws.recv()
    print(x, type(x))
    ws.close()

def socket_runner():
    sk.run()

def main():
    socket_runner()
    print('start web framework')
    app.run()


if __name__ == '__main__':
    main()
