import React, { Component } from 'react';
import { Jumbotron, Button } from 'react-bootstrap';
import { Row, Col, Container } from 'react-bootstrap';
import { LinkContainer } from 'react-router-bootstrap';
import './App.css';
import Header from './Header';
import ProxyFooter from './Footer';
import ProxyMessage from './ProxyMessage';
import ProxyUser from './User';
import api from './api';


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
      window.navigator.geolocation.getCurrentPosition(
        position => this.setPosition(position),
        error => this.positionError(error));
    } else {
      console.log("Location not available from browser");
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

positionError(error) {
  console.log("error setting location", error);
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
            updateMessages = {this.updateMessages}
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
