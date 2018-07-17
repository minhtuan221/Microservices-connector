from cython_npm.cythoncompile import require
from functools import wraps
module = require('../../microservices_connector/Interservices')
Microservice = module.Microservice

# app = Flask(__name__)
Micro = Microservice(__name__, port=5010)

# run a normal function in python
print('one cat here')

# test return string
@Micro.route('/str')
@Micro.reply
def string1(a,key):
    return a+'-'+key

# test return multiple string
@Micro.route('/str2')
@Micro.reply
def string2(a, b, key):
    return a, key, b+'-'+key

# test return Integer and float
@Micro.route('/int')
@Micro.reply
def int1(a, key):
    return a+key


@Micro.route('/float')
@Micro.reply
def float2(a, key):
    return a+key


@Micro.route('/int3')
@Micro.reply
def int3(a, key, key2):
    return a+key2, key*key, a*a

# test return list and dict
@Micro.route('/list')
@Micro.reply
def list1(a, key):
    a.extend(key)
    return a


@Micro.route('/dict')
@Micro.reply
def dict1(a, key):
    key['dict'] = a
    return key


@Micro.route('/list3')
@Micro.reply
def list3(a, key):
    key.append('other value')
    c = None
    return a, key, c

# return None, class Object
@Micro.route('/None')
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


@Micro.route('/class',token='123456')
@Micro.reply
def TestClass(a, key):
    t = testservice(a)
    return t


@Micro.route('/class2', token='123456')
@Micro.reply
def TestClass2(a, key):
    t = testservice(key)
    return t, a, None


@Micro.route('/class3', token='123456')
@Micro.reply
def TestClass3(a, key):
    x = testservice(key)
    y = testservice(a)
    z = [y,x]
    return x, y, z 


@Micro.route('/one', methods=['POST','GET'])
@Micro.dict
def TestOne():
    return [12121212]


@Micro.route('/one2', methods=['POST', 'GET'])
@Micro.dict
def TestOne2():
    return {'data':'something'}

# Option 1: run Microservice within file it's created
if __name__ == '__main__':
    Micro.run(port=5010, host='0.0.0.0', debug=True)
