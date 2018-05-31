from flask import Flask
from flask import request
from flask_sqlalchemy import SQLAlchemy
from config import BaseConfig
import json

app = Flask(__name__)
app.config.from_object(BaseConfig)
db = SQLAlchemy(app)

import models


@app.route('/', methods=['GET'])
def get_root():
    try:
        # data = json.loads(request.data)

        return str(request.args)
    except Exception as exc:
        return str(exc)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
