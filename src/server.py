import json

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

from config import BaseConfig, setup_mail
from db_gateway import DB_GateWay

from flask_cors import CORS

application = Flask(__name__)
application.config.from_object(BaseConfig)
db = SQLAlchemy(application)
dbg = DB_GateWay(application, db)

mail = setup_mail(application)

CORS(application)

@application.route('/', methods=['GET'])
def get_root():
    try:
        user = request.args.get("user")
        return dbg.get_account_data(user)
    except Exception as exc:
        # 500 Internal Server Error
        return str(exc), 500


@application.route('/', methods=['PUT'])
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

@application.route('/reg', methods=['PUT'])
def put_reg():
    try:
        data = json.loads(request.data)

        if len(data) <= 1:
            return "nothing to update"

        user = dbg.register_user(data)

        return "updated %r" % user
    except Exception as exc:
        # 500 Internal Server Error
        return str(exc), 500


@application.before_first_request
def initDB():
    import models

    try:
        for m in models.list():
            print(str(m))
            print(str(m.query.filter_by(id=1).first()))
    except:
        print("sqlalchemy.exc.ProgrammingError")
        print("initDB now!")
        import create_db
        create_db
        print("initDB DONE")


if __name__ == '__main__':
    initDB()
    application.run(host='0.0.0.0')
