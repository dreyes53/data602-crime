import "./App.css";

import React, {useState, useEffect} from "react";

import useConfig from "./components/useConfig";
import logo from "./logo.svg";

const API_URL = 'https://5b12yu9a45.execute-api.us-east-1.amazonaws.com/dev/quote'

/**
 * Our Web Application
 */
export default function App() {
  const config = useConfig();
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

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <h1 className="App-title">Welcome to {config.app.TITLE}</h1>
      </header>
      <p className="App-intro">
        To get started, edit <code>src/App.tsx</code> and save to reload.
      </p>
      <div>
        {data ? <pre>{JSON.stringify(data, null, 2)}</pre> : 'Loading...'}
      </div>
    </div>
  );
}
