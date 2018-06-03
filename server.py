import json

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

from config import BaseConfig
from db_gateway import DB_GateWay

app = Flask(__name__)
app.config.from_object(BaseConfig)
db = SQLAlchemy(app)
dbg = DB_GateWay(db)


@app.route('/', methods=['GET'])
def get_root():
    try:
        user = request.args.get("user")
        return dbg.get_user_data(user)
    except Exception as exc:
        return str(exc)


@app.route('/', methods=['PUT'])
def put_root():
    try:
        data = json.loads(request.data)

        if len(data) <= 1:
            return "nothing to update"

        user = dbg.update_user(data)
        dbg.update_timetable(user, data)

        return "updated %r" % user
    except Exception as exc:
        return str(exc)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
