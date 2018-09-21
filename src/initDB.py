from time import sleep

time = 30
print("sleep: " + str(time))
sleep(time)

try:
    import models
    for m in models.list():
        print(str(m))
        print(str(m.query.filter_by(id=1).first()))
except:
    print("DB ERROR")
    print("initDB now!")
    import create_db

    create_db
    print("initDB DONE")