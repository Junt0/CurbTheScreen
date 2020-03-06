import React, { Component } from 'react';
import logo from './logo.svg';
import './App.scss';
import { render } from '@testing-library/react';

class App extends Component{
  public render() {
    return (
      <div className="App">
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <p>
            Edit <code>src/App.tsx</code> and save to reload.
          </p>
          <a className="App-link" href="https://reactjs.org" target="_blank" rel="noopener noreferrer">
            Learn React and TypeScript
          </a>
        </header>
      </div>
    );
  }
}


export default App;
