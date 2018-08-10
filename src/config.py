import os


class BaseConfig(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ['SECRET_KEY']
    DEBUG = os.environ['DEBUG']
    DB_NAME = os.environ['DB_NAME']
    DB_USER = os.environ['DB_USER']
    DB_PASS = os.environ['DB_PASS']
    DB_SERVICE = os.environ['DB_SERVICE']
    DB_PORT = os.environ['DB_PORT']
    SQLALCHEMY_DATABASE_URI = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
        DB_USER, DB_PASS, DB_SERVICE, DB_PORT, DB_NAME
    )
    SECURITY_PASSWORD_SALT = os.environ['SECURITY_PASSWORD_SALT']
    # SECURITY_CONFIRMABLE = True
    SECURITY_REGISTERABLE = True
    # SECURITY_RECOVERABLE = True
    # SECURITY_CHANGEABLE = True


# At top of file
from flask_mail import Mail


# After 'Create app'
def setup_mail(app):
    # app.config['MAIL_SERVER'] = 'smtp.example.com'
    # app.config['MAIL_PORT'] = 465
    # app.config['MAIL_USE_SSL'] = True
    # app.config['MAIL_USERNAME'] = 'username'
    # app.config['MAIL_PASSWORD'] = 'password'
    app.config['MAIL_DEBUG'] = 1 if app.debug else 0
    mail = Mail(app)
    return mail