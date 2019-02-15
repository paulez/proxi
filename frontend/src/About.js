import React from 'react';
import { Jumbotron, Container, Row, Col } from 'react-bootstrap';
import { NavLink } from 'react-router-dom'
import Header from './Header.js';
import ProxyFooter from './Footer.js';


const ProxyAbout = () => (
  <React.Fragment>
    <Header/>
    <Container>
      <Row>
      <Col md={{span: 6, offset: 4}}>
        <Jumbotron>
          <h1>About Proxi</h1>
          <p>
          Proxi is a proximity messaging service.
          </p>
          <p>
          Your messages will be displayed to people around you, and the messages you see were posted by people around.<br />
          You want to know if there is an open bakery around? <NavLink to="/">Just ask!</NavLink>
          </p>
        </Jumbotron>
      </Col>
      </Row>
      </Container>
      <ProxyFooter/>
  </React.Fragment>
)
export default ProxyAbout;