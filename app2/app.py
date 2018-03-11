from flask import Flask
from flask import request
import json

app = Flask(__name__)


@app.route("/hello", methods=['GET','POST'])
def hello():
    content=[]
    content = request.get_json(silent=True)
    print(content)
    return json.dumps({'message':'Helloworld','content':content})
