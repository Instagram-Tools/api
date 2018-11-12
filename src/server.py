import json
from flask import Flask
from flask import request
from flask_cors import CORS

from config import BaseConfig, setup_mail
from db_gateway import DB_GateWay, db

# Create app
app = Flask(__name__)
app.config.from_object(BaseConfig)

database = db.DB(app)
db = database.db
dbg = DB_GateWay(database)

mail = setup_mail(app)

CORS(app)


@app.route('/api/', methods=['GET'])
def get_root():
    try:
        email = request.args.get("email")
        e_password = request.args.get("e_password")
        if not dbg.verify_user(email=email, password=e_password):
            return "Wrong Credentials", 500

        username = request.args.get("username")
        if username:
            return dbg.get_account_data(username)
        else:
            return "ping", 200
    except Exception as exc:
        # 500 Internal Server Error
        return str(exc), 500


@app.route('/api/', methods=['PUT'])
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


@app.route('/api/reg/', methods=['PUT'])
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
