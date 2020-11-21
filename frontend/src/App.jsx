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
      location: null,
      token: "",
      user: null,
    }
    this.updateMessages = this.updateMessages.bind(this);
    this.updatePosition = this.updatePosition.bind(this);
    this.setSearch = this.setSearch.bind(this);
    this.getToken = this.getToken.bind(this);
    this.setToken = this.setToken.bind(this);
    this.getUser = this.getUser.bind(this);
    this.setUser = this.setUser.bind(this);
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
    this.setState({
      location: {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
      }
    });
    this.updateMessages();
  }

  positionError(error) {
    console.log("error setting location", error);
  }

  updateMessages(search) {
    if(search === undefined) {
      search = this.state.search;
    }
    var message_params = {};
    if(this.state.location) {
      message_params = {
        search: search,
        latitude: this.state.location.latitude,
        longitude: this.state.location.longitude,
      };
    } else {
      message_params = {
        search: search,
      };
    }
    api.get("api/messages/", {
      params: message_params
    })
    .then(results => {
      let messages = results.data.map((message) => {
        return(
          <ProxyMessage
            key={message.uuid}
            message={message}
            setSearch={this.setSearch}
            updateMessages = {this.updateMessages}
            getUser = {this.getUser}
            getToken = {this.getToken}
          />
        )
      })
      this.setState({
        messages: messages,
      });
    })
    .catch(err => console.log("fetch error", err))
  }

  setToken(token) {
    this.setState({token: token});
    localStorage.setItem('token', token);
  }

  getToken() {
    var token;
    if(this.state.token){
      token = this.state.token;
    } else {
      token = localStorage.getItem('token');
      if(token) {
        this.setState({token: token});
      }
    }
    return token;
  }

  setUser(userData) {
    this.setState({ user: userData});
  }

  getUser() {
    return this.state.user;
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
              location = {this.state.location}
              setToken = {this.setToken}
              getToken = {this.getToken}
              setUser = {this.setUser}
              getUser = {this.getUser}
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
