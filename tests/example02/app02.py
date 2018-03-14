from cython_npm.cythoncompile import require
from functools import wraps
# from ...microservices_connector.Sanicservices import SanicApp as Microservice

module = require('../../microservices_connector/Interservices')
Microservice = module.SanicApp

M = Microservice(__name__)

# run a normal function in python
print('one cat here')

# test return string


@M.typing('/str')
@M.reply
def string1(a, key):
    return a+'-'+key

# test return multiple string


@M.typing('/str2')
@M.reply
def string2(a, b, key):
    return a, key, b+'-'+key

# test return Integer and float


@M.typing('/int')
@M.reply
def int1(a, key):
    return a+key


@M.typing('/float')
@M.reply
def float2(a, key):
    return a+key


@M.typing('/int3')
@M.reply
def int3(a, key, key2):
    return a+key2, key*key, a*a

# test return list and dict


@M.typing('/list')
@M.reply
def list1(a, key):
    a.extend(key)
    return a


@M.typing('/dict')
@M.reply
def dict1(a, key):
    key['dict'] = a
    return key


@M.typing('/list3')
@M.reply
def list3(a, key):
    key.append('other value')
    c = None
    return a, key, c

# return None, class Object


@M.typing('/None')
@M.reply
def TestNoneValue(a, key):
    key.append('Do something in the server')


class testservice(object):
    name = 'test'
    Purpose = 'For test only'
    empty = None

    def __init__(self, value):
        self.value = value

    def onemethod(self):
        print('This is test class')


@M.typing('/class', token='123456')
@M.reply
def TestClass(a, key):
    t = testservice(a)
    return t


@M.typing('/class2', token='123456')
@M.reply
def TestClass2(a, key):
    t = testservice(key)
    return t, a, None


@M.typing('/class3', token='123456')
@M.reply
def TestClass3(a, key):
    x = testservice(key)
    y = testservice(a)
    z = [y, x]
    return x, y, z


# Option 1: run Microservice within file it's created
if __name__ == '__main__':
    M.run(port=5000, host='0.0.0.0', debug=True)
