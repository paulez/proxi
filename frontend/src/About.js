import React, { Component } from 'react';
import { Jumbotron } from 'react-bootstrap';
import Header from './Header.js';


const ProxyAbout = () => (
  <React.Fragment>
    <Header/>
    <div class="container">
      <section id="input" className="col-md-4">
      </section>
      <section id="main" className="col-md-8">
        <Jumbotron>
          <h1>About Proxi</h1>
          <p>
          Proxi is a proximity messaging service.
          </p>
          <p>
          Your messages will be displayed to people around you, and the messages you see were posted by people around.<br />
          You want to know if there is an open bakery around? Just ask!
          </p>
        </Jumbotron>
      </section>
    </div>
  </React.Fragment>
)
export default ProxyAbout;