from flask import Flask
from flask_security import RoleMixin, UserMixin, SQLAlchemyUserDatastore, Security
from flask_security.utils import hash_password, verify_password
from flask_sqlalchemy import SQLAlchemy


class DB:
    def __init__(self, app):
        """
        :type app: Flask
        """
        db = SQLAlchemy(app)

        class models:
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
                roles = db.relationship('Role',
                                        secondary=db.Table('roles_users',
                                                           db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                                                           db.Column('role_id', db.Integer(),
                                                                     db.ForeignKey('role.id'))),
                                        backref=db.backref('users', lazy='dynamic'))
                accounts = db.relationship('Account', backref='user', lazy=True)

                parent_id = db.Column(db.Integer, db.ForeignKey('user.id'))
                affiliates = db.relationship("User")

                def set_password(self, password):
                    self.password = hash_password(password)

                def check_password(self, password):
                    hash = verify_password(password, self.password)

                    if not hash:  # TODO remove after all Passwords are reset
                        from werkzeug.security import check_password_hash
                        hash = check_password_hash(self.password, password)
                        if hash:
                            self.set_password(password=password)
                            db.session.commit()

                    return hash

                def __repr__(self):
                    return '<User %r>' % self.email

            class Account(db.Model):
                __tablename__ = 'account'

                id = db.Column(db.Integer, primary_key=True)
                username = db.Column(db.String(80), unique=True)
                password = db.Column(db.String(80), nullable=False)
                settings = db.Column(db.Text(), nullable=False)
                timetables = db.relationship('TimeTable', backref='account', lazy=True)
                running = db.relationship('Running', backref='account', lazy=True)
                timestamp = db.Column(db.TIMESTAMP, nullable=False)
                started = db.Column(db.Boolean, default=True)
                user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
                credit = db.Column(db.Integer, default=0)

                subscription = db.Column(db.String(80), unique=True)
                paid = db.Column(db.Boolean, default=False)

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
                    return '<TimeTable %r %r:%r>' % (self.account_id, str(self.start), str(self.end))

            class Running(db.Model):
                __tablename__ = 'running'

                id = db.Column(db.Integer, primary_key=True)
                account_id = db.Column(db.Integer, db.ForeignKey('account.id'), unique=True, nullable=False)
                start = db.Column(db.DateTime(), nullable=False)
                end = db.Column(db.DateTime(), nullable=False)

                def __repr__(self):
                    return '<Running %r %r:%r>' % (self.account_id, str(self.start), str(self.end))

            @staticmethod
            def list():
                return [models.Role, models.Account, models.User, models.TimeTable, models.Running]

        user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
        security = Security(app, user_datastore)

        self.models = models
        self.db = db
        self.user_datastore = user_datastore
        self.security = security
