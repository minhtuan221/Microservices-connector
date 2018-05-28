from cython_npm.cythoncompile import require
from functools import wraps
# from Interservices import SanicApp as Microservice

module = require('../../microservices_connector/Interservices')
Microservice = module.AioSocket
timeit = module.timeit

Micro = Microservice(__name__)

# run a normal function in python
print('one cat here')

# test return string


@Micro.route('/str')
@Micro.async_json
async def string1(key):
    return '-'+key

# test return multiple string


@Micro.route('/str2')
@Micro.async_json
async def string2(a, b, key):
    return a, key, b+'-'+key

# test return Integer and float


@Micro.typing('/int')
@Micro.async_json
async def int1(a, key):
    return a+key


@Micro.typing('/float')
@Micro.async_json
async def float2(a, key):
    return a+key


@Micro.typing('/int3')
@Micro.async_json
async def int3(a, key, key2):
    return a+key2, key*key, a*a

# test return list and dict


@Micro.typing('/list')
@Micro.async_json
async def list1(a, key):
    a.extend(key)
    return a


@Micro.typing('/dict')
@Micro.async_json
async def dict1(a, key):
    key['dict'] = a
    return key


@Micro.typing('/list3')
@Micro.async_json
async def list3(a, key):
    key.append('other value')
    c = None
    return a, key, c

# return None, class Object


@Micro.typing('/None')
@Micro.async_json
async def TestNoneValue(a, key):
    key.append('Do something in the server')


class testservice(object):
    name = 'test'
    Purpose = 'For test only'
    empty = None

    def __init__(self, value):
        self.value = value

    def onemethod(self):
        print('This is test class')


@Micro.typing('/class', token='123456')
@Micro.async_json
async def TestClass(a, key):
    t = testservice(a)
    return t


@Micro.typing('/class2', token='123456')
@Micro.async_json
async def TestClass2(a, key):
    t = testservice(key)
    return t, a, None


@Micro.typing('/class3', token='123456')
@Micro.async_json
@timeit
async def TestClass3(a, key):
    x = testservice(key)
    y = testservice(a)
    z = [y, x]
    return x, y, z


@Micro.typing('/json')
@Micro.async_json
@timeit
async def TestReceiveJson(a=1, b='string', c=None):
    return {'1':a,'2':b,'3':c}


@Micro.route('/json1')
@Micro.async_json
async def TestReceiveJson2(a=None):
    return a


# Option 1: run Microservice within file it's created
if __name__ == '__main__':
    Micro.run(port=5000, host='0.0.0.0')
