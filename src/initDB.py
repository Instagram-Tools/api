from sqlalchemy.exc import OperationalError

from server import database
models = database.models
from time import sleep

def s(time = 0):
    print("sleep: " + str(time))
    sleep(time)

def init():
    try:
        for m in models.list():
            print(str(m))
            print(str(m.query.filter_by(id=1).first()))
    except OperationalError as oe:
        print(oe)
        s(10)
        init()
    except Exception as e:
        print("DB ERROR: ", e)
        print("initDB now!")
        import create_db

        create_db
        print("initDB DONE")


s(30)
init()