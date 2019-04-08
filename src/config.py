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
    # SECURITY_CONFIRMABLE = True   # /confirm
    # SECURITY_REGISTERABLE = True  # /register
    # SECURITY_CHANGEABLE = True    # /change
    SECURITY_RECOVERABLE = True  # /reset
    SECURITY_RESET_URL = '/api/reset'

    SECURITY_EMAIL_SENDER = os.environ['SECURITY_EMAIL_SENDER']

# At top of file
from flask_mail import Mail


# After 'Create app'
def setup_mail(app):
    app.config['MAIL_SERVER'] = os.environ['MAIL_SERVER']
    app.config['MAIL_PORT'] = os.environ['MAIL_PORT']
    app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', True)
    app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
    app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
    app.config['MAIL_DEBUG'] = 1 if app.debug else 0
    mail = Mail(app)
    return mail
