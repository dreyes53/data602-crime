import "./App.css";

import React, {useState, useEffect} from "react";
import Spinner from 'react-bootstrap/Spinner';

import useConfig from "./components/useConfig";
import logo from "./logo.svg";


const API_URL = 'http://localhost:5000/crime-prediction'

const Divider = () => {
  return (
      <hr
          style={{ borderTop: "1px solid lightgrey" }}
      ></hr>
  );
};

/**
 * Our Web Application
 */
export default function App() {
  const [data, setData] = useState(null)

  useEffect(() => {
    fetch(API_URL)
    .then(response => {
      console.log(response)
      return response.json()})
    .then(json => {
      console.log(json)
      setData(json)})
    .catch(error => console.error(error))
  }, [])

  const to_table = (data: never) => {
    const dataset = data['7']['predicted_data']
    const idx_keys = Object.keys(dataset['ds'])
    const clean_data = []

    for (let i = 0; i < idx_keys.length; i++) {
      clean_data.push({'date': dataset['ds'][idx_keys[i]], 'value': dataset['yhat'][idx_keys[i]]})
    } 
    return clean_data
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1 className="App-title">PG County Crime Predictor</h1>
        <h2 className="App-title">By Dennis Reyes, Edmund Park, Cole Bromfield</h2>
      </header>
      <p className="App-intro">
        Upcoming Data Refresh Schedule:
      </p>
      <ul>
        <li>December 15</li>
        <li>December 22</li>
        <li>December 29</li>
      </ul>  
      <div>
        {data ? '' : 
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>}
      </div>
      <div className="row">
      <div className="column">
      {data ? <img src={`data:image/png;base64,${data['7']['predicted_plot']}`}/>: ''}
      </div>
      {/* <div className="column">
      {data ? <img src={`data:image/png;base64,${data['7']['predicted_trend']}`}/>: ''}
      </div> */}
      <div className="column">
      {data ? <table>
                <tr>
                    <th>Date</th>
                    <th>Prediction Value</th>
                </tr>
                {to_table(data).map((val, key) => {
                    return (
                        <tr key={key}>
                            <td>{val.date}</td>
                            <td>{val.value}</td>
                        </tr>
                    )
                })}
            </table>: ''}
        </div>
        <div className="column">
        {data ? <b>Mean Absolute Percentage Error: </b>: ''} {data ? data['7']['MAPE'] : ''}
      </div>
      </div>
      {data ?
      <><div>
          <h2 className="App-title">Additional Plots:</h2>
        </div><div>
            <img src={'http://localhost:8080/images/crime_categories.jpg'} />
            <img src={'http://localhost:8080/images/crime_confusion_matrix.jpg'} />
            <img src={'http://localhost:8080/images/crime_day_of_week.jpg'} />
            <img src={'http://localhost:8080/images/pg_county_map.jpg'} />
          </div></>: ''}
    </div>
  );
}
