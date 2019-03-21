import json
from flask import request
from flask_cors import CORS
from sqlalchemy.exc import OperationalError, IntegrityError, InvalidRequestError

from config import setup_mail

from settings import dbg, app, db


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
        app.logger.error("OperationalError at GET /api/ %s" % oe)
        return login()

    except InvalidRequestError as oe:
        app.logger.error("InvalidRequestError at GET /api/ %s" % oe)
        app.logger.warning("run rollback()")
        db.session.rollback()
        return login()

    except Exception as exc:
        # 500 Internal Server Error
        app.logger.error("GET /api/ %s" % exc)
        app.logger.warning("run rollback()")
        db.session.rollback()
        return str(exc), 500


@app.route('/api/', methods=['PUT'])
def update_settings():
    try:
        data = json.loads(request.data)
        app.logger.warning("PUT /api/ %s" % data)

        if len(data) <= 1:
            return "nothing to update"

        email = data.get("email")
        e_password = data.get("e_password")
        username = data.get('username')
        usernames = dbg.get_account_usernames(email=email, password=e_password)
        if not username in usernames:
            return "Wrong Credentials. You have only access to: %s" % usernames, 403

        account = dbg.update_account(data)
        dbg.update_timetable(account, data)

        return "updated Account %r" % account

    except OperationalError as oe:
        app.logger.error("OperationalError at PUT /api/ %s" % oe)
        return update_settings()


    except InvalidRequestError as oe:
        app.logger.error("InvalidRequestError at PUT /api/ %s" % oe)
        app.logger.warning("run rollback()")
        db.session.rollback()
        return update_settings()

    except Exception as exc:
        # 500 Internal Server Error
        app.logger.error("PUT /api/ %s" % exc)
        app.logger.warning("run rollback()")
        db.session.rollback()
        return str(exc), 500


@app.route('/api/register/', methods=['PUT'])
def register():
    try:
        data = json.loads(request.data)
        app.logger.warning("PUT /api/register/ %s" % data)

        if len(data) <= 1:
            return "nothing to update"

        account = dbg.get_account(email=data.get("email"), password=data.get("password"), username=data.get("username"))
        if account:
            return account, 201

        user = dbg.register_user(data)

        return "created %r" % user, 200

    except OperationalError as oe:
        app.logger.error("OperationalError at PUT /api/register/ %s" % oe)
        return register()

    except InvalidRequestError as oe:
        app.logger.error("InvalidRequestError at PUT /api/register/ %s" % oe)
        app.logger.warning("run rollback()")
        db.session.rollback()
        return register()

    except IntegrityError as exc:
        app.logger.error("PUT /api/register/ %s" % exc)
        return "Wrong Credentials", 403

    except Exception as exc:
        # 500 Internal Server Error
        app.logger.error("PUT /api/register/ %s" % exc)
        app.logger.warning("run rollback()")
        db.session.rollback()
        return str(exc), 500


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
        app.logger.error("OperationalError at GET/POST /api/%s/%s %s" % (user, pw, oe))
        return bot_activity(user, pw)


    except InvalidRequestError as oe:
        app.logger.error("InvalidRequestError at GET/POST /api/%s/%s %s" % (user, pw, oe))
        app.logger.warning("run rollback()")
        db.session.rollback()
        return bot_activity(user, pw)

    except Exception as exc:
        # 500 Internal Server Error
        app.logger.error("POST /api/%s/%s %s" % (user, pw, exc))
        app.logger.warning("run rollback()")
        db.session.rollback()
        return str(exc), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000)
