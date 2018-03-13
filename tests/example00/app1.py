from microservices_connector.Interservices import Microservice

M = Microservice(__name__)

@M.typing('/helloworld')
@M.reply
def helloworld(name):
    return 'Welcome %s' % (name)

if __name__ == '__main__':
    M.run()