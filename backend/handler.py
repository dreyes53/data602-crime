from collections import namedtuple
from random import choice
import sqlite3
import pandas as pd

from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/crime", methods=["GET"])
def get_crime_data():
     conn = sqlite3.connect('historical_crime_data.db')
     df = pd.read_sql('SELECT * FROM crimes', conn)
     data = df['incident_case_id'].head(5).to_dict()
     
     response = jsonify(data)
     response.headers.add('Access-Control-Allow-Origin', '*')
     return response

@app.route("/test", methods=["GET"])
def test_connect():
     response = jsonify({'Backend': 'Up and Running!!'})
     response.headers.add('Access-Control-Allow-Origin', '*')
     return response

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=5000)
