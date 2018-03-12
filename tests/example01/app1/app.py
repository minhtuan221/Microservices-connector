from cython_npm.cythoncompile import require
from functools import wraps
module = require('../Interservices')
Microservice = module.Microservice

# app = Flask(__name__)
M = Microservice(__name__)

def my_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        print('Calling decorated function')
        return f(*args, **kwds)
    return wrapper

# M.run()
print('one cat here')

@M.typing('/hello')
@M.reply
def hello(v,onekey):
    print(v, onekey)
    # return v+onekey, 200, {'Content-Type': 'text/html'}
    # return [v,onekey]
    # return 'hello world'
    return {v: onekey}, 20
    # return 120
    # return 120.78, 30
    # return v,onekey
