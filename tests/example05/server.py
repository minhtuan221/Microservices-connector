from minisocket import SocketServer
from microservices_connector.Interservices import Microservice
import threading, time

sk = SocketServer(__name__)
app = Microservice('Flask_app').app

@app.route('/')
def helloworld():
    time.sleep(2)
    return 'Sleep 2s before response'


@sk.router('/hello')
def test(message):
    print(message)
    return 'ok:'+message

def socket_runner():
    sk.run()

def main():
    s = threading.Thread(target=sk.run)
    s.start()
    print('start web framework')
    app.run()


if __name__ == '__main__':
    main()
