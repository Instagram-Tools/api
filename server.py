from flask import Flask
from flask import request
from flask_sqlalchemy import SQLAlchemy
from config import BaseConfig
import json

from db_gateway import update_user, update_timetable, get_user_data

app = Flask(__name__)
app.config.from_object(BaseConfig)
db = SQLAlchemy(app)


@app.route('/', methods=['GET'])
def get_root():
    try:
        user = request.args.get("user")
        return get_user_data(user)
    except Exception as exc:
        return str(exc)


@app.route('/', methods=['PUT'])
def put_root():
    try:
        data = json.loads(request.data)
        user = update_user(data)
        update_timetable(user, data)

        return "updated %r" % user
    except Exception as exc:
        return str(exc)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
