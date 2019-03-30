import json
from flask import jsonify
from werkzeug.security import generate_password_hash

from exceptions import AuthenticationException
from time_util import timestamp, parse_datetime,decode_datetime



class DB_GateWay:
    def __init__(self, database, logger):
        self.logger = logger
        self.db = database.db
        self.user_datastore = database.user_datastore
        self.security = database.security
        self.models = database.models

    def check_affiliation(self, username, email, e_password):
        return username in self.get_account_usernames(email=email, password=e_password)

    def register_user(self, data):
        user = self.user_datastore.create_user(email=data.get("email"), password=generate_password_hash(data.get("password")))
        self.db.session.commit()
        return user

    def verify_user(self, email, password):
        user = self.find_user(email)
        if user and user.check_password(password):
            return user
        else:
            return None

    def get_account_data(self, username, email, e_password):
        first: self.models.Account = self.find_account(username)

        if first and self.check_affiliation(username, email, e_password):
            tables = self.decode_timetable(first.timetables)
            return {"password": first.password, "username": first.username,
                            "subscription": first.subscription,
                            "settings": first.settings, "timetable": tables,
                    "timestamp": str(first.timestamp)}
        else:
            # 403 Forbidden
            return "That is not your Account", 403

    def get_account(self, email, password, username):
        user = self.verify_user(email=email, password=password)
        if not user:
            self.logger.warning("Wrong Password for User with Email: %s" % email)
            return None

        if not (username and len(str(username)) > 0):
            if user and len(user.accounts) > 0:
                username = user.accounts[0].username
                self.logger.warning("GET /api username: %s" % username)
            else:
                self.logger.warning("There is no Account owned by %s" % user)
                return jsonify({})

        result = self.get_account_data(username, email, password)
        self.logger.warning("GET /api result: %s" % result)
        return jsonify(result)

    def get_account_usernames(self, email, password):
        user = self.verify_user(email=email, password=password)
        if not user:
            self.logger.warning("Wrong Password for User with Email: %s" % email)
            return []

        if user:
            return list(map(lambda account: account.username, user.accounts))
        else:
            self.logger.warning("There is no Account owned by %s" % user)
            return []

    def update_account(self, data):
        first: self.models.Account = self.find_account(data.get("username"))
        if first and self.check_affiliation(data.get("username"), data.get("email"), data.get("e_password")):
            if data.get("password"):
                first.password = data.get("password")
            if data.get("set_username"):
                first.username = data.get("set_username")
            if data.get("subscription"):
                first.subscription = data.get("subscription")
            if data.get("settings"):
                first.settings = json.dumps(data.get("settings"))
            if data.get("started"):
                first.started = data.get("bot_on")
            first.timestamp = timestamp()
            self.db.session.commit()
            return first

        raise AuthenticationException("Wrong Credentials")

    def add_account(self, data):
        user: self.models.User = self.find_user(data.get("email"))
        account = self.models.Account(username=data.get("username"), password=data.get("password"),
                                      settings=data.get("settings"), timestamp=timestamp(),
                                      started=data.get("bot_on"), user_id=user.id,
                                      subscription=data.get("subscription"), paid=True)  # TODO set paid via pay-manager
        self.db.session.add(account)
        self.db.session.commit()
        return account

    def update_user(self, data):
        first: self.models.User = self.find_user(data.get("email"))
        if first and self.check_affiliation(data.get("username"), data.get("email"), data.get("e_password")):
            if data.get("set_e_password"):
                first.password = generate_password_hash(data.get("set_e_password"))
            self.db.session.commit()
            return first

        return None

    def find_account(self, username):
        return self.models.Account.query.filter_by(username=username).first()

    def find_user(self, email):
        return self.models.User.query.filter_by(email=email).first()

    def update_timetable(self, account, data):
        timetable = data.get("timetable")
        if timetable:
            self.delete_timetables(account)
            for i in range(0, len(timetable), 2):
                self.db.session.add(self.models.TimeTable(
                    account_id=account.id, start=parse_datetime(timetable[i]),
                    end=parse_datetime(timetable[i + 1])))
            self.db.session.commit()

    def decode_timetable(self, timetables):
        decoded = []
        for t in timetables:
            decoded += [(decode_datetime(t.start)), (decode_datetime(t.end))]
        return decoded


    def delete_timetables(self, account):
        self.models.TimeTable.query.filter_by(account_id=account.id).delete()

    def get_bot_activity(self):
        return 404

    def add_bot_activity(self):
        return 404
