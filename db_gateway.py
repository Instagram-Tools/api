import json

from flask import jsonify
from flask_security import Security, SQLAlchemyUserDatastore

from time_util import timestamp, parse_datetime


def check_affiliation(account):
    return str(account) in str(list(current_user.accounts))


class DB_GateWay:

    def __init__(self, application, db):
        import models
        self.models = models
        self.db = db
        # Setup Flask-Security
        self.user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
        self.security = Security(application, self.user_datastore)

    def get_account_data(self, username):
        first: self.models.Account = self.models.Account.query.filter_by(username=username).first()
        if first and check_affiliation(first):
            class Encoder(json.JSONEncoder):
                def default(self, o):
                    return o.to_json()

            tables = json.dumps(first.timetables, cls=Encoder)
            return jsonify({"settings": first.settings, "timetables": tables,
                            "timestamp": str(first.timestamp)})
        else:
            # 403 Forbidden
            return "That is not your Account", 403

    def update_account(self, data):
        first: self.models.Account = self.models.Account.query.filter_by(username=data.get("username")).first()
        if first and check_affiliation(first):
            if data.get("password"):
                first.password = data.get("password")
            if data.get("settings"):
                first.settings = data.get("settings")
            if data.get("paid"):
                first.paid = data.get("paid")
            if data.get("started"):
                first.started = data.get("started")
            if data.get("user_id"):
                first.started = data.get("user_id")
            first.timestamp = timestamp()
            self.db.session.commit()
            return first

        account = self.models.Account(username=data.get("username"), password=data.get("password"),
                                      settings=data.get("settings"), timestamp=timestamp(),
                                      paid=data.get("paid"), started=data.get("started"),
                                      user_id=data.get("user_id"))
        self.db.session.add(account)
        self.db.session.commit()
        return account

    def update_timetable(self, account, data):
        timetable = data.get("timetable")
        if timetable:
            self.delete_timetables(account)
            for i in range(0, len(timetable), 2):
                timetable = self.models.TimeTable(account_id=account.id, start=parse_datetime(timetable[i]),
                                                  end=parse_datetime(timetable[i + 1]))
                self.db.session.add(timetable)
            self.db.session.commit()

    def delete_timetables(self, account):
        self.models.TimeTable.query.filter_by(account_id=account.id).delete()
