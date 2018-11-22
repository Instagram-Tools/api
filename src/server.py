import json
from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS
from sqlalchemy.dialects.postgresql import psycopg2

from config import BaseConfig, setup_mail
from db_gateway import DB_GateWay, database_db

# Create app
app = Flask(__name__)
app.config.from_object(BaseConfig)


def init_db_gateway():
    global database, db, dbg
    database = database_db.DB(app)
    db = database.db
    dbg = DB_GateWay(database)


init_db_gateway()

mail = setup_mail(app)

CORS(app)

@app.route('/', methods=['GET'])
def ping():
    return "ping", 200

@app.route('/api/', methods=['GET'])
def get_root():
    try:
        app.logger.warning("GET /api %s" % request.args)
        email = request.args.get("email")
        e_password = request.args.get("e_password")
        user = dbg.verify_user(email=email, password=e_password)
        app.logger.warning("GET /api user: %s" % user)
        if user:
            username = request.args.get('username')
            if not (username and len(str(username)) > 0):
                if len(user.accounts) > 0:
                    username = user.accounts[0].username
                    app.logger.warning("GET /api username: %s" % username)
                    result = dbg.get_account_data(username)
                else:
                    app.logger.warning("GET /api There is no Account owned by %s" % user)
                    result = jsonify({})
            app.logger.warning("GET /api result: %s" % result)
            return result
        else:
            return "Wrong Credentials", 403

    except psycopg2.OperationalError as oe:
        app.logger.error("GET /api/ %s" % oe)
        init_db_gateway()

    except Exception as exc:
        # 500 Internal Server Error
        app.logger.error("GET /api/ %s" % exc)
        return str(exc), 500


@app.route('/api/', methods=['PUT'])
def put_root():
    try:
        data = json.loads(request.data)
        app.logger.warning("PUT /api/ %s" % data)

        if len(data) <= 1:
            return "nothing to update"

        user = dbg.update_account(data)
        dbg.update_timetable(user, data)

        return "updated %r" % user

    except psycopg2.OperationalError as oe:
        app.logger.error("GET /api/ %s" % oe)
        init_db_gateway()

    except Exception as exc:
        # 500 Internal Server Error
        app.logger.error("PUT /api/ %s" % exc)
        return str(exc), 500


@app.route('/api/register/', methods=['PUT'])
def register():
    try:
        data = json.loads(request.data)
        app.logger.warning("/api/register/", data)

        if len(data) <= 1:
            return "nothing to update"

        user = dbg.register_user(data)

        return "created %r" % user

    except psycopg2.OperationalError as oe:
        app.logger.error("PUT /api/ %s" % oe)
        init_db_gateway()

    except Exception as exc:
        # 500 Internal Server Error
        app.logger.error("PUT /api/register/ %s" % exc)
        return str(exc), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000)
