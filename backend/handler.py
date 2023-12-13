import io
from collections import namedtuple
from random import choice
import sqlite3
import pandas as pd
import requests
import json
import matplotlib.pyplot as plt
from prophet import Prophet
import numpy as np
from base64 import encodebytes
from PIL import Image

from flask import Flask, jsonify

def get_response_image(image_path):
    pil_img = Image.open(image_path, mode='r') # reads the PIL image
    byte_arr = io.BytesIO()
    pil_img.save(byte_arr, format='PNG') # convert the PIL image to byte array
    encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii') # encode as base64
    return encoded_img

app = Flask(__name__)


@app.route("/crime-prediction", methods=["GET"])
def get_crime_data():
    data = {}
    conn = sqlite3.connect('historical_crime_data.db')
    historical_df = pd.read_sql('SELECT * FROM crimes', conn)

    # Get Crime Incidents July 2023 to Present and merge with Historical crime data
    # Upcoming Weekly Schedule
    # November 24, 2023
    # Decemeber 1, 2023
    # December 8, 2023

    offset = 0
    limit = 10000
    full_present_crime_data = []

    while True:
        url = f'https://data.princegeorgescountymd.gov/resource/xjru-idbe.json?$offset={offset}&$limit={limit}'
        x = requests.get(url)
        nested = json.loads(json.dumps(x.json(), indent=2))
        if len(nested) == 0:
            break
        full_present_crime_data = full_present_crime_data + nested
        offset = offset + limit

    print("Number of Crime Incidents July 2023 to Present:", len(full_present_crime_data))
    present_df = pd.json_normalize(full_present_crime_data)
    present_df = present_df[present_df['location'].notna()]
    present_df = present_df.drop(columns=['location'])

    frames = [historical_df, present_df]
    historical_df = pd.concat(frames, ignore_index=True)


    historical_df['date']= pd.to_datetime(historical_df['date'])
    historical_df['day_of_week'] = historical_df['date'].dt.dayofweek
    historical_df['day_of_week'] = historical_df['day_of_week'].map({
        0: 'Monday',
        1: 'Tuesday',
        2: 'Wednesday',
        3: 'Thursday',
        4: 'Friday',
        5: 'Saturday',
        6: 'Sunday'
    })
    historical_df['latitude'] = pd.to_numeric(historical_df['latitude'])
    historical_df['longitude'] = pd.to_numeric(historical_df['longitude'])

    historical_df = historical_df[(historical_df['latitude'] > 30) & (historical_df['latitude'] < 40)]
    historical_df = historical_df[(historical_df['longitude'] > -80) & (historical_df['longitude'] < -75)]

    print("Number of Crime Incidents February 2017 to Present:", len(historical_df.index))

    historical_df['date'] = pd.to_datetime(historical_df['date']).dt.date
    df = historical_df.groupby('date').count()['clearance_code_inc_type'].to_frame()
    df.reset_index(inplace=True)
    df.columns = ['ds','y']

    # Prediction Model
    # Predictions for Week, Month, Year
    # prediction_times = [7, 30, 365]
    prediction_times = [7]

    for prediction_period in prediction_times:
        current_data = {}
        # Make another copy of the data frame as m2
        df_m2 = df.copy()
        df_m2['ds'] = pd.to_datetime(df_m2['ds'])

        print(df_m2.dtypes)

        # Define the Upper Control Limit and Lower Control Limit as 3 standard deviations from the mean
        ucl = df_m2.mean() + df_m2.std()*3
        lcl = df_m2.mean() - df_m2.std()*3

        # Print the number of outliers found
        print('Above 3 standard deviations: ', df_m2[df_m2['y'] > ucl['y']]['y'].count(), 'entries')
        print('Below 3 standard deviations: ', df_m2[df_m2['y'] < lcl['y']]['y'].count(), 'entries')

        # Remove them by setting their value to None. Prophet says it can handle null values.
        df_m2.loc[df_m2['y'] > ucl['y'], 'y'] = None
        df_m2.loc[df_m2['y'] < lcl['y'], 'y'] = None

        # Log transformation
        df_m2['y'] = np.log(df_m2['y'])

        # Run Prophet using model 2
        m2_no_outlier = Prophet()
        m2_no_outlier.fit(df_m2)
        future = m2_no_outlier.make_future_dataframe(periods=prediction_period)
        forecast_m2 = m2_no_outlier.predict(future)

        m2_no_outlier.plot(forecast_m2)
        plt.xlabel('Date')
        plt.ylabel('Log(Crime Count)')
        plt.legend(['Actual', 'Trend', 'Uncertainty'])
        plt.title(f'PG County Crime Predictions for the next {prediction_period} days')
        plt.savefig(f'./plot_images/crime_prediction_{prediction_period}.jpg', bbox_inches='tight')
        current_data['predicted_plot'] = [get_response_image(f'./plot_images/crime_prediction_{prediction_period}.jpg')]

        start_day_of_predicted_week = forecast_m2["ds"].max() - pd.to_timedelta(prediction_period, unit='d')

        print("Forecast: ")
        # predicted_data = forecast_m2[forecast_m2['ds'] > start_day_of_predicted_week][['ds', 'yhat']]
        predicted_data = forecast_m2[forecast_m2['ds'] > start_day_of_predicted_week][['ds', 'yhat']]
        for index, row in predicted_data.iterrows():
            predicted_data.at[index, 'prediction'] = np.exp(row['yhat'])
        current_data['predicted_data'] = predicted_data.to_dict()
        
        fig = m2_no_outlier.plot_components(forecast_m2)
        fig.savefig(f'./plot_images/crime_trends_{prediction_period}.jpg', bbox_inches='tight')
        current_data['predicted_trend'] = [get_response_image(f'./plot_images/crime_trends_{prediction_period}.jpg')]

        # First, let's get some useful variables: "y" for the actual value and "n" for the number of observations.
        y = df['y'].to_frame()
        y.index = df['ds']
        n = int(y.count())

        # Inverse the log
        forecast_m2_exp = np.exp(forecast_m2[['yhat','yhat_lower','yhat_upper']])
        forecast_m2_exp.index = forecast_m2['ds']

        # Calculate the error
        error = forecast_m2_exp['yhat'] - y['y']
        MAPE_m2 = (error/y['y']).abs().sum()/n *100
        current_data['MAPE'] = round(MAPE_m2,2)

        data[str(prediction_period)] = current_data
    
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
