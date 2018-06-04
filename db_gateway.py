import json

from flask import jsonify

from time_util import timestamp, parse_datetime


class DB_GateWay:

    def __init__(self, db):
        import models
        self.models = models
        self.db = db

    def get_user_data(self, user):
        first: self.models.User = self.models.User.query.filter_by(username=user).first()
        if first:
            class Encoder(json.JSONEncoder):
                def default(self, o):
                    return o.to_json()

            tables = json.dumps(first.timetables, cls=Encoder)
            return jsonify({"settings": first.settings, "timetables": tables,
                            "timestamp": str(first.timestamp)})
        else:
            return jsonify({"settings": {}, "timetables": []})

    def update_user(self, data):
        first: self.models.User = self.models.User.query.filter_by(username=data.get("username")).first()
        if first:
            if data.get("password"):
                first.password = data.get("password")
            if data.get("settings"):
                first.settings = data.get("settings")
            if data.get("paid"):
                first.paid = data.get("paid")
            if data.get("started"):
                first.started = data.get("started")
            first.timestamp = timestamp()
            self.db.session.commit()
            return first

        user = self.models.User(username=data.get("username"), password=data.get("password"),
                                settings=data.get("settings"), timestamp=timestamp(),
                                paid=data.get("paid"), started=data.get("started"))
        self.db.session.add(user)
        self.db.session.commit()
        return user

    def update_timetable(self, user, data):
        timetable = data.get("timetable")
        if timetable:
            self.deleteTimeTables(user)
            for i in range(0, len(timetable), 2):
                timetable = self.models.TimeTable(user_id=user.id, start=parse_datetime(timetable[i]),
                                                  end=parse_datetime(timetable[i + 1]))
                self.db.session.add(timetable)
            self.db.session.commit()

    def deleteTimeTables(self, user):
        self.models.TimeTable.query.filter_by(user_id=user.id).delete()
