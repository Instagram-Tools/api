import json

from flask import Flask, request
from flask_security import login_required
from flask_sqlalchemy import SQLAlchemy

from config import BaseConfig
from db_gateway import DB_GateWay

application = Flask(__name__)
application.config.from_object(BaseConfig)
db = SQLAlchemy(application)
dbg = DB_GateWay(application, db)


@application.route('/', methods=['GET'])
@login_required
def get_root():
    try:
        user = request.args.get("user")
        return dbg.get_account_data(user)
    except Exception as exc:
        # 500 Internal Server Error
        return str(exc), 500


@application.route('/', methods=['PUT'])
@login_required
def put_root():
    try:
        data = json.loads(request.data)

        if len(data) <= 1:
            return "nothing to update"

        user = dbg.update_account(data)
        dbg.update_timetable(user, data)

        return "updated %r" % user
    except Exception as exc:
        # 500 Internal Server Error
        return str(exc), 500


if __name__ == '__main__':
    application.run(host='0.0.0.0')
