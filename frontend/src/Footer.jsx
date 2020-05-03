import React from 'react';
import { Row, Col, Container } from 'react-bootstrap';

const ProxyFooter = () => (
  <footer>
    <Container>
      <Row>
        <Col md={{ span: 3, offset: 5}} className="mt-4">
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