
# send json by request and received
import requests
from flask import request, Response
r = requests.post('http://httpbin.org/post', json={"key": "value"})
r.status_code
r.json()

# receive json in flask
@app.route('/api/add_message/<uuid>', methods=['GET', 'POST'])
def add_message(uuid):
    if request.is_json():
        content = request.json
        print(content)
    return uuid

# calculate response time in flask
@app.after_request
def after_request(response):
    diff = time.time() - g.start
    if (response.response):
        response.response[0] = response.response[0].replace(
            '__EXECUTION_TIME__', str(diff))
    return response


# response is a WSGI object, and that means the body of the response must be an iterable. For jsonify() responses that's just a list with just one string in it.

# However, you should use the response.get_data() method here to retrieve the response body, as that'll flatten the response iterable for you.
"""process_response(response)
Can be overridden in order to modify the response object before it’s sent to the WSGI server. By default this will call all the after_request() decorated functions.

Changed in version 0.5: As of Flask 0.5 the functions registered for after request execution are called in reverse order of registration.

Parameters:	response – a response_class object.
Returns:	a new response object or the same, has to be an instance of response_class."""
# The following should work:


@app.after_request
def after(response):
    d = json.loads(response.get_data())
    d['altered'] = 'this has been altered...GOOD!'
    response.set_data(json.dumps(d))
    return response
# Don't use jsonify() again here
# that returns a full new response object
# all you want is the JSON response body here.

# Do use response.set_data() as that'll also adjust the Content-Length header to reflect the altered response size.


@app.route('/data')
def get_data():
    return {'foo': 'bar'}


# Here is a custom response class that supports the above syntax, without affecting how other routes that do not return JSON work in any way:


class MyResponse(Response):
    @classmethod
    def force_type(cls, rv, environ=None):
        if isinstance(rv, dict):
            rv = jsonify(rv)
        return super(MyResponse, cls).force_type(rv, environ)


# Using a Custom Response Class
# By now I'm sure you agree that there are some interesting use cases that can benefit from using a custom response class. Before I show you some actual examples, let me tell you how simple it is to configure a Flask application to use a custom response class. Take a look at the following example:

from flask import Flask, Response


class MyResponse1(Response):
    pass


app = Flask(__name__)
app.response_class = MyResponse1

# ...
from flask import Flask, Response


class MyResponse2(Response):
    pass


class MyFlask(Flask):
    response_class = MyResponse2


app = MyFlask(__name__)

# ...

# Changing Response Defaults


class MyResponse3(Response):
    default_mimetype = 'application/xml'


# Determining Content Type Automatically
class MyResponse4(Response):
    def __init__(self, response, **kwargs):
        if 'mimetype' not in kwargs and 'contenttype' not in kwargs:
            if response.startswith('<?xml'):
                kwargs['mimetype'] = 'application/xml'
        return super(MyResponse, self).__init__(response, **kwargs)


def my_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        print('Calling decorated function')
        return f(*args, **kwds)
    return wrapper


def typing(text: str):
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
