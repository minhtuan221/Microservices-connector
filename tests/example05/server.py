from minisocket import SocketServer

sk = SocketServer(__name__)


@sk.router('/hello')
def test(message):
    print(message)
    return 'ok:'+message


def main():
    sk.run()


if __name__ == '__main__':
    main()
