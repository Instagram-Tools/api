import json
from flask import request
from flask_cors import CORS
from sqlalchemy.dialects.postgresql import psycopg2
from sqlalchemy.exc import OperationalError

from config import setup_mail

from settings import dbg, app


mail = setup_mail(app)

CORS(app)

@app.route('/', methods=['GET'])
def ping():
    return "ping", 200

@app.route('/api/', methods=['GET'])
def login():
    try:
        app.logger.warning("GET /api %s" % request.args)
        email = request.args.get("email")
        e_password = request.args.get("e_password")
        username = request.args.get('username')
        account = dbg.get_account(email=email, password=e_password, username=username)
        if account:
            return account, 200
        else:
            return "Wrong Credentials", 403

    except OperationalError as oe:
        app.logger.error("GET /api/ %s" % oe)
        login()

    except Exception as exc:
        # 500 Internal Server Error
        app.logger.error("GET /api/ %s" % exc)
        return str(exc), 500


@app.route('/api/', methods=['PUT'])
def update_settings():
    try:
        data = json.loads(request.data)
        app.logger.warning("PUT /api/ %s" % data)

        if len(data) <= 1:
            return "nothing to update"

        user = dbg.update_account(data)
        dbg.update_timetable(user, data)

        return "updated %r" % user

    except OperationalError as oe:
        app.logger.error("GET /api/ %s" % oe)
        update_settings()

    except Exception as exc:
        # 500 Internal Server Error
        app.logger.error("PUT /api/ %s" % exc)
        return str(exc), 500


@app.route('/api/register/', methods=['PUT'])
def register():
    try:
        data = json.loads(request.data)
        app.logger.warning("PUT /api/register/ %s" % data)

        if len(data) <= 1:
            return "nothing to update"

        user = dbg.register_user(data)

        return "created %r" % user

    except OperationalError as oe:
        app.logger.error("PUT /api/ %s" % oe)
        register()

    except Exception as exc:
        # 500 Internal Server Error
        app.logger.error("PUT /api/register/ %s" % exc)
        return str(exc), 500

    except psycopg2.IntegrityError as exc:
        app.logger.error("PUT /api/register/ %s" % exc)
        return "Wrong Credentials", 403

@app.route('/api/bot/<user>/<pw>', methods=['POST', 'GET'])
def bot_activity(user, pw):
    try:
        if request.method == 'POST':
            app.logger.warning("POST /api/%s/%s %s: %s" % (user, pw, request.data))
            return dbg.add_bot_activity(request.data)

        elif request.method == 'GET':
            app.logger.warning("GET /api/%s/%s" % (user, pw))
            return dbg.get_bot_activity()

        return 404

    except OperationalError as oe:
        app.logger.error("GET /api/%s/%s %s" % (user, pw, oe))

    except Exception as exc:
        # 500 Internal Server Error
        app.logger.error("POST /api/%s/%s %s" % (user, pw, exc))
        return str(exc), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000)
