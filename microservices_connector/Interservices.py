from flask import Flask, Response
from flask import request, jsonify
import inspect
import json
from functools import wraps
import requests
import time


def timeit(method):

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print('%r  %2.2f ms' %
              (method.__name__, (te - ts) * 1000))
        return result

    return timed


class FlaskResponse(Response):
    default_mimetype = 'application/json'
    # set default content-type to json

    @classmethod
    def force_type(cls, rv, environ=None):
        # rv = jsonify(res=rv)
        # print(rv)
        if isinstance(rv, (dict, list, int, float)):
            rv = jsonify(rv) 
        # if isinstance(rv, (int)):
        #     rv = jsonify(int=rv)
        return super(FlaskResponse, cls).force_type(rv, environ)


class Microservice(object):
    """Microservice(name, port: int=5000, host: str='0.0.0.0', debug=None, token: dict = {}, secretKey=None)
    
    Arguments:
        name {str} -- Require a name for your app, recommend put __name__ for it
        port {int} -- Choose from 3000 to 9000, default to 5000
        host {str} -- Host ip, Default 0.0.0.0 for localhost
        debug {boolean} -- True for development, False/None for production
        token {dict} -- A dict contain all rule and its token. It can be set later
    """
    def __init__(self, name, port: int=5000, host: str='0.0.0.0', debug=None, token: dict = {}, secretKey=None, **kwargs):
        self.app = Flask(name)
        self.port = port
        self.host = host
        self.debug = debug
        self.token = token
        self.secretKey = secretKey
        self.init_app(**kwargs)

    def init_app(self, **kwargs):
        self.app.response_class = FlaskResponse

    def remove(self, token: str):
        return self.token.pop(token, None)

    def typing(self, rule: str, **options):
        def decorator(f):
            endpoint = options.pop('endpoint', None)
            methods = options.pop('methods', None)
            token = options.pop('token', None)
            try:
                self.token[rule] = str(token)
            except:
                raise ValueError('Token must be a string')
            # if the methods are not given and the view_func object knows its
            # methods we can use that instead.  If neither exists, we go with
            # a tuple of only ``GET`` as default.
            if methods is None:
                options['methods'] = ('POST',)
            self.app.add_url_rule(rule, endpoint, f, **options)
            return f
        return decorator

    def reply(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            content = request.get_json(silent=True)
            if content is not None:
                if 'token' in content:
                    # print(request.path)
                    if self.token[request.path] != content['token'] and self.token[request.path] == None:
                        # print(self.token[request.path] is not None) will return true !!
                        return {'type': 'error', 'obj': 'Token is wrong'}
                    # check token
                if args is not None:
                    for arg in content['args']:
                        args += (arg,)
                if kwargs is not None:
                    for key in content['kwargs']:
                        kwargs[key] = content['kwargs'][key]
            else:
                raise ValueError('Request contain no json')
            # print(request.headers)
            return microResponse(f(*args, **kwargs))
        return wrapper

    def run(self, **kwargs):
        self.app.run(**kwargs)


def microResponse(*args):
    final = {'res': []}
    print(len(args), type(args))
    if len(args) == 0:
        return final
    else:
        args = list(args,)
        print(args)
        for arg in args:
            if isinstance(arg, tuple):
                arg = list(arg)
                print(arg)
                for i in arg:
                    final['res'].append({'obj':oneResponse(i)})
            else:
                final['res'].append({'obj':oneResponse(arg)})
    return final


def oneResponse(res):
    if res is None:
        return None
    elif isinstance(res, (float, int, str)):
        return res
    elif isinstance(res, (list, tuple)):
        return [oneResponse(i) for i in res]
    elif isinstance(res, (dict, set)):
        resDict = {}
        for i in res:
            resDict[i] = oneResponse(res[i])
        return resDict
    elif isinstance(res, object):
        try:
            return propsOBJ(res)
        except Exception:
            return 'Error: Object type is not supported!'
    else:
        return 'Error: Object type is not supported!'

# send mess to a microservices. It's a friend


class Friend(object):
    def __init__(self, name: str, address: str, token: dict = {}, ruleMethods: dict = {}):
        self.name = name
        self.address = address
        self.token = token
        self.lastMessage = None
        self.lastreply = None
        self.ruleMethods = ruleMethods

    def setRule(self, rule: str, method: str = None, token: str = None):
        self.ruleMethods[rule] = method
        self.token[rule] = token

    def send(self, rule: str, *args, **kwargs):
        listargs = []
        if len(args)>0:
            for i in list(args):
                listargs.append(oneResponse(i))
        dictkwargs = dict()
        if len(kwargs)>0:
            kwargs = dict(kwargs)
            for i in kwargs:
                dictkwargs[i] = oneResponse(kwargs[i])
        if rule in self.token:
            token = self.token[rule]
        else:
            token = None
        jsonsend = {"args": listargs, 'kwargs': dictkwargs, 'token': token}
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
        # print(r.headers)
        self.lastreply = r
        # print(r.text)
        if r.status_code == 200:
            # print(r.headers['Content-Type'] == 'application/json')
            if r.headers['Content-Type'] == 'application/json':
                # print(r.text)
                res = r.json()
                try:
                    # res = json.loads(res['res'])
                    self.lastMessage = res
                    if 'res' in res and isinstance(res['res'], list):
                        final = []
                        for arg in res['res']:
                            final.append(arg['obj'])
                        if len(final)<=1:
                            return final[0]
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




def propsOBJ(obj):
    pr = {}
    for name in dir(obj):
        value = getattr(obj, name)
        if not name.startswith('__') and not inspect.ismethod(value):
            pr[name] = value
    return pr
