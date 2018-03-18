from cython_npm.cythoncompile import require
from functools import wraps
module = require('../../microservices_connector/Interservices')
Microservice = module.Microservice

# app = Flask(__name__)
Micro = Microservice(__name__, port=5010)

# run a normal function in python
print('one cat here')

# test return string
@Micro.typing('/str')
@Micro.reply
def string1(a,key):
    return a+'-'+key

# test return multiple string
@Micro.typing('/str2')
@Micro.reply
def string2(a, b, key):
    return a, key, b+'-'+key

# test return Integer and float
@Micro.typing('/int')
@Micro.reply
def int1(a, key):
    return a+key


@Micro.typing('/float')
@Micro.reply
def float2(a, key):
    return a+key


@Micro.typing('/int3')
@Micro.reply
def int3(a, key, key2):
    return a+key2, key*key, a*a

# test return list and dict
@Micro.typing('/list')
@Micro.reply
def list1(a, key):
    a.extend(key)
    return a


@Micro.typing('/dict')
@Micro.reply
def dict1(a, key):
    key['dict'] = a
    return key


@Micro.typing('/list3')
@Micro.reply
def list3(a, key):
    key.append('other value')
    c = None
    return a, key, c

# return None, class Object
@Micro.typing('/None')
@Micro.reply
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


@Micro.typing('/class',token='123456')
@Micro.reply
def TestClass(a, key):
    t = testservice(a)
    return t


@Micro.typing('/class2', token='123456')
@Micro.reply
def TestClass2(a, key):
    t = testservice(key)
    return t, a, None


@Micro.typing('/class3', token='123456')
@Micro.reply
def TestClass3(a, key):
    x = testservice(key)
    y = testservice(a)
    z = [y,x]
    return x, y, z 

# Option 1: run Microservice within file it's created
if __name__ == '__main__':
    Micro.run(port=5010, host='0.0.0.0', debug=True)
