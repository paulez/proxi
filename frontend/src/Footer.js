import React from 'react';
import { Row, Col, Grid } from 'react-bootstrap';

const ProxyFooter = () => (
  <footer>
    <Grid>
      <Row>
        <Col mdOffset={5} md={3}>
        <p>
          Proxi, talk to people around you.
        </p>
        <p>
          <a href="https://github.com/paulez/proxi">Proxi is on GitHub</a>
        </p>
        </Col>
      </Row>
    </Grid>
  </footer>
  )
  export default ProxyFooter;