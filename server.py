import json

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

from config import BaseConfig
from db_gateway import DB_GateWay

application = Flask(__name__)
application.config.from_object(BaseConfig)
db = SQLAlchemy(application)
dbg = DB_GateWay(db)


@application.route('/', methods=['GET'])
def get_root():
    try:
        user = request.args.get("user")
        return dbg.get_user_data(user)
    except Exception as exc:
        return str(exc)


@application.route('/', methods=['PUT'])
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
    application.run(host='0.0.0.0')
