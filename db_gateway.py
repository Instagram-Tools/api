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
        user = self.models.User(username=data.get("username"), password=data.get("password"),
                           settings=data.get("settings"), timestamp=timestamp())
        first = self.models.User.query.filter_by(username=user.username).first()
        if first:
            first.password = user.password
            first.settings = user.settings
            first.timestamp = user.timestamp

            self.models.TimeTable.query.filter_by(user_id=first.id).delete()

            self.db.session.commit()
            return first

        self.db.session.add(user)
        self.db.session.commit()
        return user

    def update_timetable(self, user, data):
        timetable = data.get("timetable", [])
        for i in range(0, len(timetable), 2):
            timetable = self.models.TimeTable(user_id=user.id, start=parse_datetime(timetable[i]),
                                         end=parse_datetime(timetable[i + 1]))
            self.db.session.add(timetable)
        self.db.session.commit()
