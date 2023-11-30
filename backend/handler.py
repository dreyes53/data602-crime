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
