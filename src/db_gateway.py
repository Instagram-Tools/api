import json
from flask import jsonify
from werkzeug.security import generate_password_hash

import database as db
from time_util import timestamp, parse_datetime


def check_affiliation(account):
    # return str(account) in str(list(current_user.accounts))
    return True


class DB_GateWay:
    def __init__(self, database):
        # type: (db) -> DB_GateWay
        self.db = database.db
        self.user_datastore = database.user_datastore
        self.security = database.security
        self.models = database.models

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

    def get_account_data(self, username):
        first: self.models.Account = self.find_account(username)
        if first and check_affiliation(first):
            class Encoder(json.JSONEncoder):
                def default(self, o):
                    return o.to_json()

            tables = json.dumps(first.timetables, cls=Encoder)
            return jsonify({"settings": first.settings, "timetable": tables,
                            "timestamp": str(first.timestamp)})
        else:
            # 403 Forbidden
            return "That is not your Account", 403

    def update_account(self, data):
        first: self.models.Account = self.find_account(data.get("username"))
        if first and check_affiliation(first):
            if data.get("password"):
                first.password = data.get("password")
            if data.get("settings"):
                first.settings = json.dumps(data.get("settings"))
            if data.get("started"):
                first.started = data.get("started")
            if data.get("user_id"):
                first.started = data.get("user_id")
            first.timestamp = timestamp()
            self.db.session.commit()
            return first

        user: self.models.User = self.find_user(data.get("email"))
        account = self.models.Account(username=data.get("username"), password=data.get("password"),
                                      settings=data.get("settings"), timestamp=timestamp(),
                                      started=data.get("started"), user_id=user.id,
                                      subscription=data.get("subscription"), paid=True)  # TODO set paid via pay-manager
        self.db.session.add(account)
        self.db.session.commit()
        return account

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

    def delete_timetables(self, account):
        self.models.TimeTable.query.filter_by(account_id=account.id).delete()
