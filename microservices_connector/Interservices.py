from flask import Flask
from flask import request, jsonify
import inspect
import json
from functools import wraps
import requests
import time
import traceback


def timeit(method):

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print('%r  %2.2f ms' %
              (method.__name__, (te - ts) * 1000))
        return result

    return timed


class Microservice(object):
    
    def __init__(self, name, port: int=5000, host: str='0.0.0.0', debug=None, token: dict = {}, secretKey=None, **kwargs):
        """Microservice(name, port: int=5000, host: str='0.0.0.0', debug=None, token: dict = {}, secretKey=None)

        Arguments:
            name {str} -- Require a name for your app, recommend put __name__ for it
            port {int} -- Choose from 3000 to 9000, default to 5000
            host {str} -- Host ip, Default 0.0.0.0 for localhost
            debug {boolean} -- True for development, False/None for production
            token {dict} -- A dict contain all rule and its token. It can be set later
        """
        self.port = port
        self.host = host
        self.debug = debug
        self.token = token
        self.secretKey = secretKey
        self.init_app(name, **kwargs)

    def init_app(self, name, **kwargs):
        self.app = Flask(name)

    def removeToken(self, token: str):
        return self.token.pop(token, None)

    def typing(self, rule: str, **options):
        if not rule.startswith('/'):
            rule = '/' + rule

        def decorator(f):
            endpoint = options.pop('endpoint', None)
            methods = options.pop('methods', None)
            token = options.pop('token', None)
            try:
                self.token[rule] = str(token)
            except:
                traceback.print_exc()
            # if the methods are not given and the view_func object knows its
            # methods we can use that instead.  If neither exists, we go with
            # a tuple of only ``POST`` as default.
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
            # else:
            #     raise ValueError('Request contain no json')
            # print(request.headers)
            return self.microResponse(f(*args, **kwargs))
        return wrapper

    def json(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            content = request.get_json(silent=True)
            for key in content:
                kwargs[key] = content[key]
            return self.microResponse(f(*args, **kwargs))
        return wrapper

    def run(self, port=None, host=None, debug=None):
        if port is None:
            port = self.port
        if host is None:
            host = self.host
        if debug is None:
            debug = self.debug
        self.app.run(port=port, host=host, debug=debug)

    def microResponse(self, *args):
        final = []
        # print(len(args), type(args))
        if len(args) == 0:
            return final
        else:
            args = list(args,)
            # print(args)
            for arg in args:
                if isinstance(arg, tuple):
                    arg = list(arg)
                    # print(arg)
                    for i in arg:
                        final.append(oneResponse(i))
                else:
                    final.append(oneResponse(arg))
        return jsonify(final)


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
            traceback.print_exc()
            return 'Error: Object type is not supported!'
    else:
        return 'Error: Object type is not supported!'

# send mess to a microservices. It's a friend


class Friend(object):
    def __init__(self, name: str, address: str, token: dict = {}, ruleMethods: dict = {}):
        self.name = name
        if not address.startswith('http://') and not address.startswith('https://'):
            address = 'http://'+address
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
        if len(args) > 0:
            for i in list(args):
                listargs.append(oneResponse(i))
        dictkwargs = dict()
        if len(kwargs) > 0:
            kwargs = dict(kwargs)
            for i in kwargs:
                dictkwargs[i] = oneResponse(kwargs[i])
        if rule in self.token:
            token = self.token[rule]
        else:
            token = None
        jsonsend = {"args": listargs, 'kwargs': dictkwargs, 'token': token}

        if rule in self.ruleMethods:
            ruleMethods = self.ruleMethods
        elif 'methods' in kwargs:
            methods = kwargs.pop('methods', None)
            ruleMethods = {rule: methods}
        else:
            ruleMethods = {}
        if rule in ruleMethods:
            method = ruleMethods[rule]
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
                    if isinstance(res, list):
                        final = []
                        for arg in res:
                            final.append(arg)
                        if len(final) <= 1:
                            return final[0]
                        return final
                    else:
                        final = res
                except Exception as identifier:
                    traceback.print_exc()
                    final = r.text
                    self.lastMessage = res
                return final
            self.lastMessage = r.text
            return r.text
        self.lastMessage = None
        return None

    def json(self, rule: str, method='POST', **kwargs):
        jsonsend = {}
        for key in kwargs:
            jsonsend[key] = kwargs[key]
        if method == 'GET':
            r = requests.get(self.address+rule, json=jsonsend)
        elif method == 'PUT':
            r = requests.put(self.address+rule, json=jsonsend)
        elif method == 'DELETE':
            r = requests.delete(self.address+rule, json=jsonsend)
        else:
            r = requests.post(self.address+rule, json=jsonsend)
        
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
                    if isinstance(res, list):
                        final = []
                        for arg in res:
                            final.append(arg)
                        if len(final) <= 1:
                            return final[0]
                        return final
                    else:
                        final = res
                except Exception as identifier:
                    traceback.print_exc()
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


from sanic import Sanic
from sanic import response


class SanicApp(Microservice):
    def __init__(self, name=None, port: int=5000, host: str='0.0.0.0', debug=None, token: dict = {}, secretKey=None, **kwargs):
        """SanicApp(name, port: int=5000, host: str='0.0.0.0', debug=None, token: dict = {}, secretKey=None)

        Arguments:
            name {str} -- Require a name for your app, recommend put __name__ for it
            port {int} -- Choose from 3000 to 9000, default to 5000
            host {str} -- Host ip, Default 0.0.0.0 for localhost
            debug {boolean} -- True for development, False/None for production
            token {dict} -- A dict contain all rule and its token. It can be set later
        """
        super().__init__(name, port, host, debug, token, secretKey, **kwargs)

    def init_app(self, name, **kwargs):
        self.app = Sanic(name)

    def typing(self, uri, methods=['POST'], token=None, host=None,
               strict_slashes=None, stream=False, version=None, name=None):
        """Decorate a function to be registered as a route

        :param uri: path of the URL
        :param methods: list or tuple of methods allowed
        :param host:
        :param strict_slashes:
        :param stream:
        :param version:
        :param name: user defined route name for url_for
        :return: decorated function
        """

        # Fix case where the user did not prefix the URL with a /
        # and will probably get confused as to why it's not working
        if not uri.startswith('/'):
            uri = '/' + uri

        if stream:
            self.app.is_request_stream = True

        if strict_slashes is None:
            strict_slashes = self.app.strict_slashes

        try:
            self.token[uri] = str(token)
        except:
            traceback.print_exc()

        def response(handler):
            if stream:
                handler.is_stream = stream
            self.app.router.add(uri=uri, methods=methods, handler=handler,
                                host=host, strict_slashes=strict_slashes,
                                version=version, name=name)
            return handler

        return response

    def reply(self, f):
        @wraps(f)
        def wrapper(sanicRequest, *args, **kwargs):
            content = sanicRequest.json
            if content is not None:
                if 'token' in content:
                    # print(request.path)
                    if self.token[sanicRequest.path] != content['token'] and self.token[sanicRequest.path] == None:
                        # print(self.token[request.path] is not None) will return true !!
                        return {'type': 'error', 'obj': 'Token is wrong'}
                    # check token
                if args is not None:
                    for arg in content['args']:
                        args += (arg,)
                if kwargs is not None:
                    for key in content['kwargs']:
                        kwargs[key] = content['kwargs'][key]
            # else:
            #     raise ValueError('Request contain no json')
            # print(request.headers)
            return self.microResponse(f(*args, **kwargs))
        return wrapper

    def json(self, f):
        @wraps(f)
        def wrapper(sanicRequest, *args, **kwargs):
            content = sanicRequest.json
            for key in content:
                kwargs[key] = content[key]
            return self.microResponse(f(*args, **kwargs))
        return wrapper

    def microResponse(self, *args):
        final = []
        # print(len(args), type(args))
        if len(args) == 0:
            return final
        else:
            args = list(args,)
            # print(args)
            for arg in args:
                if isinstance(arg, tuple):
                    arg = list(arg)
                    # print(arg)
                    for i in arg:
                        final.append(oneResponse(i))
                else:
                    final.append(oneResponse(arg))
        return response.json(final)
