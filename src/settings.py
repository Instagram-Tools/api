from flask import Flask
from config import BaseConfig
from db_gateway import DB_GateWay, database_db

app = Flask(__name__)
app.config.from_object(BaseConfig)
database = database_db.DB(app)
db = database.db
dbg = DB_GateWay(database)
