import json
from flask import Flask
from flask import request
from flask_cors import CORS
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin
from flask_sqlalchemy import SQLAlchemy

from config import BaseConfig, setup_mail
from db_gateway import DB_GateWay

# Create app
app = Flask(__name__)
app.config.from_object(BaseConfig)

# Create database connection object
db = SQLAlchemy(app)

# Define models
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean(), default=False)
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    accounts = db.relationship('Account', backref='user', lazy=True)

    def __repr__(self):
        return '<User %r>' % self.email


class Account(db.Model):
    __tablename__ = 'account'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    settings = db.Column(db.Text(), nullable=False)
    timetables = db.relationship('TimeTable', backref='account', lazy=True)
    running = db.relationship('Running', backref='account', lazy=True)
    timestamp = db.Column(db.TIMESTAMP, nullable=False)
    paid = db.Column(db.Boolean, default=False)
    started = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<Account %r>' % self.username


class TimeTable(db.Model):
    __tablename__ = 'timetable'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    start = db.Column(db.DateTime(), nullable=False)
    end = db.Column(db.DateTime(), nullable=False)

    def to_json(self):
        return {"start": str(self.start), "end": str(self.end)}

    def __repr__(self):
        return '<TimeTable %r %r:%r>' % (self.user_id, str(self.start), str(self.end))


class Running(db.Model):
    __tablename__ = 'running'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), unique=True, nullable=False)
    start = db.Column(db.DateTime(), nullable=False)
    end = db.Column(db.DateTime(), nullable=False)

    def __repr__(self):
        return '<Running %r %r:%r>' % (self.user_id, str(self.start), str(self.end))



# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


class models:
    Role = Role
    Account = Account
    User = User
    TimeTable = TimeTable
    Running = Running

    @staticmethod
    def list():
        return [Role, Account, User, TimeTable, Running]


dbg = DB_GateWay(db, user_datastore, security, models)

mail = setup_mail(app)

CORS(app)

@app.route('/', methods=['GET'])
def get_root():
    try:
        user = request.args.get("user")
        return dbg.get_account_data(user)
    except Exception as exc:
        # 500 Internal Server Error
        return str(exc), 500


@app.route('/', methods=['PUT'])
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

@app.route('/reg', methods=['PUT'])
def put_reg():
    try:
        data = json.loads(request.data)

        if len(data) <= 1:
            return "nothing to update"

        user = dbg.register_user(data)

        return "updated %r" % user
    except Exception as exc:
        # 500 Internal Server Error
        return str(exc), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0')
