import json

from flask import jsonify

import models
from server import db
from time_util import timestamp, parse_datetime


def get_user_data(user):
    first: models.User = models.User.query.filter_by(username=user).first()
    if first:
        class Encoder(json.JSONEncoder):
            def default(self, o):
                return o.to_json()

        tables = json.dumps(first.timetables, cls=Encoder)
        return jsonify({"settings": first.settings, "timetables": tables,
                        "timestamp": str(first.timestamp)})
    else:
        return jsonify({"settings": {}, "timetables": []})


def update_user(data):
    user = models.User(username=data.get("username"), password=data.get("password"),
                       settings=data.get("settings"), timestamp=timestamp())
    first = models.User.query.filter_by(username=user.username).first()
    if first:
        first.password = user.password
        first.settings = user.settings
        first.timestamp = user.timestamp

        for t in first.timetables:
            db.session.delete(t)

        db.session.add(first)
        user = first
    db.session.add(user)
    db.session.commit()
    return user


def update_timetable(user, data):
    timetable = data.get("timetable", [])
    for i in range(0, len(timetable), 2):
        timetable = models.TimeTable(user_id=user.id, start=parse_datetime(timetable[i]),
                                     end=parse_datetime(timetable[i + 1]))
        db.session.add(timetable)
    db.session.commit()