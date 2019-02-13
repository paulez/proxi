import React, { Component } from 'react';
import { Card, Jumbotron, Button } from 'react-bootstrap';
import { Row, Col, Container } from 'react-bootstrap';
import { LinkContainer } from 'react-router-bootstrap';
import './App.css';
import Header from './Header.js';
import ProxyFooter from './Footer.js';
import ProxyUser from './User.js';
import TimeAgo from 'react-timeago';
import api from './api.js';

class ProxyMessage extends Component {
  constructor(props) {
    super(props);
    this.handleClick = this.handleClick.bind(this);
  }

  handleClick() {
    this.props.setSearch(this.props.message.username);
  }

  formatDistance(distance) {
    if(distance < 1000) {
      return `${distance} m`
    } else {
      distance = distance / 1000
      return `${distance} km`
    }
  }

  render () {
    var distance = this.formatDistance(this.props.message.distance);
    if (this.props.message.current_user) {
      return (
        <article>
          <Card bg="light" className="mb-1">
            <Card.Body>
              <Card.Text>
                {this.props.message.message}
              </Card.Text>
              <Card.Link href="#" onClick={this.handleClick}>
                  {this.props.message.username}
              </Card.Link>
            </Card.Body>
            <Card.Footer>
              <small className="text-white">
                <TimeAgo
                  date={this.props.message.date}
                  minPeriod={30}
                /> within {distance}
              </small>  
            </Card.Footer>
          </Card>
      </article>
      )
    } else {
      return (
        <article>
          <Card bg="primary" text="white" className="mb-1">
            <Card.Body>
              <Card.Text>
                {this.props.message.message}
              </Card.Text>
              <Card.Link href="#" onClick={this.handleClick}>
                  {this.props.message.username}
              </Card.Link>
            </Card.Body>
            <Card.Footer>
              <small className="text-white">
                <TimeAgo
                  date={this.props.message.date}
                  minPeriod={30}
                /> within {distance}
              </small>  
            </Card.Footer>
          </Card>
      </article>
      )
    }
  }
}

class MessageList extends Component {

  render () {
    if (this.props.messages.length > 0) {
      return (
        <div className="messages">
          {this.props.messages}
        </div>
      );
    } else {
      return (
        <Jumbotron>
          <h2>Start the local discussion!</h2>
          <p>
          No recent message nearby!
          </p>
          <p>
            Choose a pseudo, and start the discussion with people nearby by posting a message!
          </p>
          <p>
          <LinkContainer to="/about">
            <Button variant="info">About proxi</Button>
          </LinkContainer>
          </p>
        </Jumbotron>
      );
    }
  }
}

class App extends Component {

  constructor(props) {
    super(props);
    this.state = {
      messages: [],
      search: "",
    }
    this.updateMessages = this.updateMessages.bind(this);
    this.updatePosition = this.updatePosition.bind(this);
    this.setSearch = this.setSearch.bind(this);
  }

  setSearch(search) {
    this.setState({
      search: search,
    });
    this.updateMessages(search);
  }

  componentDidMount() {
    this.updateMessages();
    this.updatePosition();
    this.messageInterval = setInterval(this.updateMessages, 20 * 1000);
    this.positionInterval = setInterval(this.updatePosition, 60 * 1000);
  }

  componentWillUnmount() {
    clearInterval(this.messageInterval);
    clearInterval(this.positionInterval);
  }

  updatePosition() {
    if ('geolocation' in window.navigator) {
      window.navigator.geolocation.getCurrentPosition((position) => {
        this.setPosition(position);
      })
    }
  }

  setPosition(position) {
    api.post("api/position", {
      latitude: position.coords.latitude,
      longitude: position.coords.longitude
    })
    .then(() => {
      this.updateMessages();
    })
  }

  updateMessages(search) {
    if(search === undefined) {
      search = this.state.search;
    }
    api.get("api/messages/", {
      params: {
        search: search,
      }
    })
    .then(results => {
      let messages = results.data.map((message) => {
        return(
          <ProxyMessage
            key={message.uuid}
            message={message}
            setSearch={this.setSearch}
          />
        )
      })
      this.setState({
        messages: messages,
      });
    })
    .catch(err => console.log("fetch error", err))
  }

  render() {
    return (
      <React.Fragment>
        <Header
          search={this.state.search}
          setSearch={this.setSearch}
        />
        <Container>
          <Row>
          <Col md={4}>
            <ProxyUser
              updateMessages = {this.updateMessages}
            />
          </Col>
          <Col md={6}>
            <MessageList
              messages = {this.state.messages}
            />
          </Col>
            </Row>
          </Container>
        <ProxyFooter/>
      </React.Fragment>
    );
  }
}

export default App;
