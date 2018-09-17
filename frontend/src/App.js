import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';

class ProxyMessage extends React.Component {
  render () {
    return (
      <article className="well well-small">
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
    </article>
    )
  }
}

class ProxyMessageList extends React.Component {
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
          <ProxyMessage message={message} />
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
      <div className="App">
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <h1 className="App-title">Welcome to React</h1>
        </header>
        <ProxyMessageList />
      </div>
    );
  }
}

export default App;
