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
    print('port',r.json())


@timeit
def dopost():
    r = requests.post('http://localhost:5000/hello', json={"args": ["value",], 'kwargs':{'onekey':'value of key'}})
    r.status_code
    r.json()
    print('get',r.json())


@timeit
def doput():
    r = requests.put('http://localhost:5000/hello', json={"key": "value"})
    r.status_code
    r.json()
    print('put',r.json())


@timeit
def dodelete():
    r = requests.delete('http://localhost:5000/hello', json={"key": "value"})
    r.status_code
    r.json()
    print('delete',r.json())

# doget()
# dopost()
# doput()
# dodelete()


# send mess to a microservices. It's a friend
class Friend(object):
    def __init__(self, name:str, address:str, token=None):
        self.name = name
        self.address = address
        self.token = token

    def send(self, rule:str, *args, **kwargs):
        listargs = None
        if args is not None:
            listargs = list(args)
        r = requests.post(self.address+rule,
                        json={"args": listargs, 'kwargs': kwargs, 'token':self.token})
        print(r.headers)
        # print(r.text)
        if r.status_code == 200:
            print(r.headers['Content-Type'] == 'application/json')
            if r.headers['Content-Type'] == 'application/json':
                print(r.text)
                res = r.json()
                try:
                    res = json.loads(res['res'])
                    if 'obj' in res:
                        final = res['obj']
                except Exception as identifier:
                    final = res['res']
                return final
            return r.text
        return None

def typing(text:str):
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
    result = (F.send('/hello','value',onekey = 'value of Key'))
    return result

x = test()
print(x, type(x))
# y = json.loads(test())
# print(y, type(y))
