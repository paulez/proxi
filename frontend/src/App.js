import React, { Component } from 'react';
import { Well } from 'react-bootstrap';
import logo from './logo.svg';
import './App.css';
import Header from './Header.js';
import UserLoginForm from './User.js';

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
    this.state = {
      messages: [],
    }
  }

  componentDidMount() {
    console.log("fetching");
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
      <div className="messages">
      {this.state.messages}
      </div>
    )
  }
}

class App extends Component {
  render() {
    return (
      <React.Fragment>
        <Header />
        <div class="container">
          <section id="input" class="cold-md-4">
            <UserLoginForm />
          </section>
          <section id="main" class="col-md-8">
            <ProxyMessageList />
          </section>
        </div>
      </React.Fragment>
    );
  }
}

export default App;
