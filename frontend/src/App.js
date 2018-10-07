import React, { Component } from 'react';
import { Well } from 'react-bootstrap';
import logo from './logo.svg';
import './App.css';
import Header from './Header.js';
import ProxyUser from './User.js';
import axios from 'axios';

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

class ProxyMessage extends Component {

  render () {
    return (
      <article>
        <Well bsSize="small">
          <section className="message-text">
              <p>{this.props.message.message}</p>
          </section>
          <section className="message-info">
              <span className="message-author">
                  By {this.props.message.username} within {this.props.message.distance}
              </span>
              <span className="message-date">
                  {this.props.date}
              </span>
          </section>
        </Well>
    </article>
    )
  }
}

class ProxyMessageList extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div className="messages">
      {this.props.messages}
      </div>
    )
  }
}

class App extends Component {

  constructor(props) {
    super(props);
    this.state = {
      messages: [],
    }
    this.updateMessages = this.updateMessages.bind(this);
  }

  componentDidMount() {
    this.updateMessages();
    if ('geolocation' in window.navigator) {
      window.navigator.geolocation.getCurrentPosition(
        this.setPosition
      )
    } 
  }

  setPosition(position) {
    axios.post("api/position", {
      latitude: position.coords.latitude,
      longitude: position.coords.longitude
    })
    .then(() => {
      console.log("position posted", position);
      this.updateMessages();
    })
  }

  updateMessages() {
    console.log("fetching messages");
    fetch("/api/messages/")
    .then(results => {
      return results.json();
    })
    .then(results => {
      console.log("data", results)
      let messages = results.map((message) => {
        console.log("message", message)
        return(
          <ProxyMessage key={message.uuid} message={message} />
        )
      })
      this.setState({messages: messages});
      console.log("state", this.state.messages);
    })
    .catch(err => console.log("fetch error", err))
  }

  render() {
    return (
      <React.Fragment>
        <Header />
        <div class="container">
          <section id="input" className="col-md-4">
            <ProxyUser 
              updateMessages = {this.updateMessages}
            />
          </section>
          <section id="main" className="col-md-8">
            <ProxyMessageList 
              messages = {this.state.messages}
            />
          </section>
        </div>
      </React.Fragment>
    );
  }
}

export default App;
