import React, { Component } from 'react';
import { Well } from 'react-bootstrap';
import logo from './logo.svg';
import './App.css';
import Header from './Header.js';
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
    return (
      <article>
        <Well bsSize="small">
          <section className="message-text">
              <p>{this.props.message.message}</p>
          </section>
          <section className="message-info">
              <span className="message-author">
                  By <a onClick={this.handleClick}>{this.props.message.username}</a>
                  &nbsp;within {distance}
              </span>
              <span className="message-date">
                  <TimeAgo 
                    date={this.props.message.date} 
                    minPeriod={30}
                  />
              </span>
          </section>
        </Well>
    </article>
    )
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
    this.messageInterval = setInterval(this.updateMessages, 60 * 1000);
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
    console.log("fetching messages");
    api.get("api/messages/", {
      params: {
        search: search,
      }
    })
    .then(results => {
      console.log("data", results.data)
      let messages = results.data.map((message) => {
        console.log("message", message)
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
      console.log("state", this.state.messages);
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
        <div class="container">
          <section id="input" className="col-md-4">
            <ProxyUser 
              updateMessages = {this.updateMessages}
            />
          </section>
          <section id="main" className="col-md-8">
            <div className="messages">
              {this.state.messages}
            </div>
          </section>
        </div>
      </React.Fragment>
    );
  }
}

export default App;
