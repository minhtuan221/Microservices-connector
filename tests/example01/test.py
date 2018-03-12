import requests
import time
import json


def timeit(method):

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print('%r  %2.2f ms' %
              (method.__name__, (te - ts) * 1000))
        return result

    return timed

# post is the fastest way


@timeit
def doget():
    r = requests.get('http://0.0.0.0:5000/hello', json={"key": "value"})
    r.status_code
    r.json()
    print('port', r.json())


@timeit
def dopost():
    r = requests.post('http://localhost:5000/hello',
                      json={"args": ["value", ], 'kwargs': {'onekey': 'value of key'}})
    r.status_code
    r.json()
    print('get', r.json())


@timeit
def doput():
    r = requests.put('http://localhost:5000/hello', json={"key": "value"})
    r.status_code
    r.json()
    print('put', r.json())


@timeit
def dodelete():
    r = requests.delete('http://localhost:5000/hello', json={"key": "value"})
    r.status_code
    r.json()
    print('delete', r.json())

# doget()
# dopost()
# doput()
# dodelete()


# send mess to a microservices. It's a friend
class Friend(object):
    def __init__(self, name: str, address: str, token:dict = {} , ruleMethods:dict = {}):
        self.name = name
        self.address = address
        self.token = token
        self.lastMessage = None
        self.ruleMethods = ruleMethods

    def setRule(self, rule: str, method: str = None, token: str = None):
        self.ruleMethods[rule] = method
        self.token[rule] = token

    def send(self, rule: str, *args, **kwargs):
        listargs = None
        if args is not None:
            listargs = list(args)
        if rule in self.token:
            token = self.token[rule]
        else:
            token = None
        jsonsend = {"args": listargs, 'kwargs': kwargs, 'token': token}
        if rule in self.ruleMethods:
            method = self.ruleMethods[rule]
            if method == 'GET':
                r = requests.get(self.address+rule,
                                 json=jsonsend)
            elif method == 'PUT':
                r = requests.put(self.address+rule,
                                 json=jsonsend)
            elif method == 'DELETE':
                r = requests.delete(self.address+rule,
                                    json=jsonsend)
            else:
                r = requests.post(self.address+rule,
                                  json=jsonsend)
        else:
            r = requests.post(self.address+rule,
                              json=jsonsend)
        print(r.headers)
        # print(r.text)
        if r.status_code == 200:
            print(r.headers['Content-Type'] == 'application/json')
            if r.headers['Content-Type'] == 'application/json':
                print(r.text)
                res = r.json()
                try:
                    # res = json.loads(res['res'])
                    self.lastMessage = res
                    if 'res' in res and isinstance(res['res'],list):
                        final = []
                        for arg in res['res']:
                            final.append(arg['obj'])
                        return final
                    else:
                        final = res
                except Exception as identifier:
                    final = r.text
                    self.lastMessage = res
                return final
            self.lastMessage = r.text
            return r.text
        self.lastMessage = None
        return None


def typing(text: str):
    res = text
    try:
        res = json.loads(text)['res']
        print(res, 'try 1')
    except Exception as error:
        print(error)
        try:
            res = json.loads('{"res":{}}'.format(text))['res']
            print(res, 'try 2')
        except Exception:
            pass
    return res


# @timeit
def test():
    F = Friend('app1', 'http://localhost:5000')
    F.setRule('/hello')
    result = (F.send('/hello', 'value', onekey='value of Key'))
    print('lastMessage', F.lastMessage, type(F.lastMessage))
    return result


x, y = test()
print(x, type(x))
# y = json.loads(test())
print(y, type(y))
