import React from 'react';
import { Row, Col, Container } from 'react-bootstrap';

const ProxyFooter = () => (
  <footer>
    <Container>
      <Row>
        <Col offset={5} md={3}>
        <p>
          Proxi, talk to people around you.
        </p>
        <p>
          <a href="https://github.com/paulez/proxi">Proxi is on GitHub</a>
        </p>
        </Col>
      </Row>
    </Container>
  </footer>
  )
  export default ProxyFooter;