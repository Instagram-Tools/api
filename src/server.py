import json
from flask import Flask
from flask import request
from flask_cors import CORS

from config import BaseConfig, setup_mail
from db_gateway import DB_GateWay, database

# Create app
app = Flask(__name__)
app.config.from_object(BaseConfig)

database = database.DB(app)
db = database.db
dbg = DB_GateWay(database)

mail = setup_mail(app)

CORS(app)


@app.route('/', methods=['GET'])
def get_root():
    try:
        user = request.args.get("user")
        return dbg.get_account_data(user)
    except Exception as exc:
        # 500 Internal Server Error
        return str(exc), 500


@app.route('/', methods=['PUT'])
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


@app.route('/reg', methods=['PUT'])
def put_reg():
    try:
        data = json.loads(request.data)

        if len(data) <= 1:
            return "nothing to update"

        user = dbg.register_user(data)

        return "created %r" % user
    except Exception as exc:
        # 500 Internal Server Error
        return str(exc), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000)
