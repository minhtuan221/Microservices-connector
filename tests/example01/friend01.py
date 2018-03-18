import requests
import time
import json
from cython_npm.cythoncompile import require
# from ../
Interservices = require('../../microservices_connector/Interservices')
Friend = Interservices.Friend

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
    r = requests.post('http://localhost:5010/hello',
                      json={"args": ["value", ], 'kwargs': {'onekey': 'value of key'}})
    r.status_code
    r.json()
    print('get', r.json())


@timeit
def doput():
    r = requests.put('http://localhost:5010/hello', json={"key": "value"})
    r.status_code
    r.json()
    print('put', r.json())


@timeit
def dodelete():
    r = requests.delete('http://localhost:5010/hello', json={"key": "value"})
    r.status_code
    r.json()
    print('delete', r.json())

# doget()
# dopost()
# doput()
# dodelete()


# @timeit
# def test():
#     aFriend= Friend('app1', 'http://localhost:5010')
#     aFriend.setRule('/hello')
#     r = aFriend.send('/hello', 'A variable value', onekey='A keyword variable value')
#     return r

# python run.py
# test return a string
@timeit
def testStr():
    print(
        """##############################
    Test return string
    """)
    aFriend= Friend('app1', 'localhost:5010')
    print('Test: return a simple string')
    x = aFriend.send('/str', 'A variable value', key='A keyword variable value')
    print('x=', x, type(x))
    print('==========================')
    print('Test: return multiple string')
    x, y, z = aFriend.send('/str2', 'A variable value','second Variable',
                  key='A keyword variable value')
    print('x=' ,x, type(x))
    print('y=', y, type(y))
    print('z=', z, type(z))
    
testStr()
"""[Result]
Test: return a simple string
x= A variable value-A keyword variable value <class 'str'>
==========================
Test: return multiple string
x= A variable value <class 'str'>
y= A keyword variable value <class 'str'>
z= A variable value-A keyword variable value <class 'str'>
'testStr'  23.17 ms
"""


@timeit
def testInt():
    print(
        """##############################
    Test return a int, float
    """)
    aFriend= Friend('app1', 'localhost:5010')
    print('Test: return a simple Value')
    x = aFriend.send('/int', 2018, key=312)
    print('x=', x, type(x))
    print('==========================')
    print('Test: return a simple Value')
    x = aFriend.send('/float', 2.018, key=3.12)
    print('x=', x, type(x))
    print('==========================')
    print('Test: return multiple Value')
    x, y, z = aFriend.send('/int3', 3.1427,
                     key=1000000000, key2=2.71230)
    print('x=', x, type(x))
    print('y=', y, type(y))
    print('z=', z, type(z))
testInt()
"""[result]
Test: return a simple Value
x= 2330 <class 'int'>
==========================
Test: return a simple Value
x= 5.138 <class 'float'>
==========================
Test: return multiple Value
x= 1000000003.1427 <class 'float'>
y= 1000000000000000000 <class 'int'>
z= 9.87656329 <class 'float'>
"""


@timeit
def testListDict():
    print(
    """##############################
    Test return a list, dict
    """)
    aFriend= Friend('app1', 'localhost:5010')
    print('Test: return a simple Value')
    x = aFriend.send('/list', [12,34,45], key=['abc','zyz'])
    print('x=', x, type(x))
    print('==========================')
    print('Test: return a simple Value')
    x = aFriend.send('/dict', {'keyword':['anything']}, key={'int':20,'str':'adfafsa','float':0.2323})
    print('x=', x, type(x))
    print('==========================')
    print('Test: return multiple Value')
    x, y, z = aFriend.send('/list3', {'keyword': ['anything']},
                     key=['abc', 'zyz'])
    print('x=', x, type(x))
    print('y=', y, type(y))
    print('z=', z, type(z))


testListDict()
"""[Result]
Test: return a simple Value
x= [12, 34, 45, 'abc', 'zyz'] <class 'list'>
==========================
Test: return a simple Value
x= {'dict': {'keyword': ['anything']}, 'float': 0.2323, 'int': 20, 'str': 'adfafsa'} <class 'dict'>
==========================
Test: return multiple Value
x= {'keyword': ['anything']} <class 'dict'>
y= ['abc', 'zyz', 'other value'] <class 'list'>
z= None <class 'NoneType'>
'testListDict'  22.19 ms
"""


class testservice(object):
    name = 'test'
    Purpose = 'For test only'
    empty = None

    def __init__(self, value):
        self.value = value

    def onemethod(self):
        print('This is test class')


@timeit
def testClassType():
    print(
        """##############################
    Test return NoneType, Class, use of Token
    """)
    aFriend= Friend('app1', 'localhost:5010')
    print('Test: return a simple Value')
    x = aFriend.send('/None', [12, 34, 45], key=['abc', 'zyz'])
    print('x=', x, type(x))
    print('==========================')
    print('Test: return a simple Value with token')
    aFriend.setRule('/class', token='123456')
    x = aFriend.send('/class', {'keyword': ['anything']},
               key={'int': 20, 'str': 'adfafsa', 'float': 0.2323})
    print('x=', x, type(x))
    print('==========================')
    print('Test: return multiple Value')
    aFriend.setRule('/class2', token='123456')
    x,y,z = aFriend.send('/class2', {'keyword': ['anything']},
               key={'int': 20, 'str': 'adfafsa', 'float': 0.2323})
    print('x=', x, type(x))
    print('y=', y, type(y))
    print('z=', z, type(z))

    # Test send class and list of class object
    print('Test: send class and list of class object')
    aFriend.setRule('/class3', token='123456')
    t1 = testservice('value1')
    t2 = testservice('value2')
    x, y, z = aFriend.send('/class3', [t1,t2],
                     key={'t1': t1, 't2': t2, 'list': [t1, t2]})
    print('x=', x, type(x))
    print('y=', y, type(y))
    print('z=', z, type(z))



testClassType()
"""[Results]
##############################
    Test return NoneType, Class, use of Token

Test: return a simple Value
x= None <class 'NoneType'>
==========================
Test: return a simple Value with token
x= {'Purpose': 'For test only', 'empty': None, 'name': 'test', 'value': {'keyword': ['anything']}} <class 'dict'>
==========================
Test: return multiple Value
x= {'Purpose': 'For test only', 'empty': None, 'name': 'test', 'value': {'float': 0.2323, 'int': 20, 'str': 'adfafsa'}} <class 'dict'>
y= {'keyword': ['anything']} <class 'dict'>
z= None <class 'NoneType'>
'testClassType'  19.20 ms
"""
