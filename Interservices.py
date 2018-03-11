from flask import Flask, Response
from flask import request, jsonify
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


def typing(text: str):
    res = text
    try:
        res = json.loads(text)['res']
    except Exception as error:
        print(error)
        try:
            res = json.loads('{"res":{}}'.format(text))['res']
        except Exception:
            pass
    return res


class Friend(object):

    # send mess to a microservices. It's a friend
    def __init__(self, name: str, address: str, token=None):
        self.name = name
        self.address = address
        self.token = token

    def send(self, rule: str, *args, **kwargs):
        listargs = None
        if args is not None:
            listargs = list(args)
        r = requests.post(self.address+rule,
                          json={"args": listargs, 'kwargs': kwargs, 'token': self.token})
        print(r.headers)
        print(r.text)
        if r.status_code == 200:
            res = typing(r.text)
            return json.loads(res)
        return None

class FlaskResponse(Response):
    default_mimetype = 'application/json'
    # set default content-type to json
    @classmethod
    def force_type(cls, rv, environ=None):
        # rv = jsonify(res=rv)
        # print(rv)
        if isinstance(rv, (dict,list,int,float)):
            rv = jsonify(obj=rv) #,{'Var-Type':'dict-list'}
        # if isinstance(rv, (int)):
        #     rv = jsonify(int=rv)
        return super(FlaskResponse, cls).force_type(rv, environ)


class Microservice(object):
    # friendList = {'name':{'address':'name','token':'abcxyz'}}
    def __init__(self, name, port: int=5000, host: str='0.0.0.0', debug=None, secretKey=None, **kwargs):
        self.app = Flask(name)
        self.port = port
        self.host = host
        self.debug = debug
        self.friendList = {}
        self.secretKey = secretKey
        self.init_app(**kwargs)

    def init_app(self, **kwargs):
        self.app.response_class = FlaskResponse
        @self.app.after_request
        def after(response):
            # if response.headers['Content-Type'] == 'application/json':
            #     if isinstance(response.get_data().decode('utf-8'), str):
            # print(json.dumps(response.get_data().decode('utf-8')))
            # print(type(response.get_data().decode('utf-8')))
            # response.headers['Content-Type'] == 'application/json'
            d = {"res": json.loads(json.dumps(response.get_data().decode('utf-8')))}
            # print(response.headers)
            response.set_data(json.dumps(d))
            return response

    def addFriend(self, F:Friend):
        # onefriend have only one token
        # afriend = {'address': address,'token':token}
        self.friendList[F.name] = F

    def removeFriend(self, name):
        self.friendList.pop(name, None)

    def send(self, port: int, host: str, token=None, **kwargs):
        pass

    def typing(self, rule: str, **options):
        def decorator(f):
            endpoint = options.pop('endpoint', None)
            methods = options.pop('methods', None)
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
                if args is not None:
                    for arg in content['args']:
                        args += (arg,)
                if kwargs is not None:
                    for key in content['kwargs']:
                        kwargs[key] = content['kwargs'][key]
            else:
                raise ValueError('Request contain no json')
            # print(request.headers)
            return f(*args, **kwargs)
        return wrapper

    def run(self, **kwargs):
        self.app.run(**kwargs)
