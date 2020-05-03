import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter as Router, Route } from 'react-router-dom';
import './index.css';
import 'bootstrap/dist/css/bootstrap.css';
import App from './App';
import ProxyAbout from './About';
import registerServiceWorker from './registerServiceWorker';

ReactDOM.render(
    <Router>
      <div>
        <Route path="/" exact component={App} />
        <Route path="/about/" component={ProxyAbout} />
      </div>
    </Router>,
    document.getElementById('root'));

registerServiceWorker();
