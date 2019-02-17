import React, { Component } from 'react';
import api from './api.js';
import { Button, FormGroup, FormControl, FormLabel } from 'react-bootstrap';
import ProxyMessageForm from './MessageForm.js';

class LogoutForm extends Component {
  constructor(props) {
    super(props);
    this.state = {
      form_valid: null,
      form_error: "",
    }
  }

  handleLogout = (event) => {
    api.post("api/logout")
    .then(data => {
      this.props.setUser(null);
    })
    .catch(error => {
      if (error.response) {
        if(error.response.status === 404) {
          console.log("already logged out");
          this.props.setUser(null);
        }
      }
      console.log("cannot logout", error);
    })
    event.preventDefault();
  }

  getValidationState() {
    return this.state.form_valid;
  }

  render () {
    var username = this.props.getUser()
    return (
      <div>
        <ProxyMessageForm
          updateMessages = {this.props.updateMessages}
        />
        <form onSubmit={this.handleLogout}>
          <FormGroup controlId="logoutForm">
          <span>
            <FormLabel>Currently known as <mark>{username}</mark></FormLabel>
          </span>
          { " " }
          <span>
            <Button type="submit" size="small">Logout</Button>
          </span>
          </FormGroup>
        </form>
      </div>
    )
  }
}

class LoginForm extends Component {
  constructor(props) {
    super(props);
    this.state = {
      form_username: "",
      form_valid: null,
      form_error: "",
    }
  }

  handleSubmit = (event) => {
    api.post("api/login", {
      username: this.state.form_username,
    })
    .then(data => {
      this.props.setUser(data.data.username);
    })
    .catch(error => {
      this.props.setUser(null);
      this.setState({
        form_valid: "error",
        form_error: "Pseudo already in use, please choose another one!",
      })
      console.log("cannot login", error);
    })
    this.props.updateMessages();
    event.preventDefault();
  }

  handleChange = (event) => {
    this.setState({ form_username: event.target.value});
    event.preventDefault();
  }

  getValidationState() {
    return this.state.form_valid;
  }

  componentDidMount() {
    this.usernameInput.focus();
  }

  render () {
    return (
      <form onSubmit={this.handleSubmit}>
        <FormGroup
          controlId="userForm"
          validated={this.getValidationState()}
        >
        <FormControl
          type="text"
          name="username"
          value={this.state.form_username}
          placeholder="Choose your pseudo!"
          onChange={this.handleChange}
          ref={ref => { this.usernameInput = ref; }}
        />
        </FormGroup>
        <Button type="submit" variant="primary">Use</Button>
      </form>
    )
  }
}


class ProxyUser extends Component {
  constructor(props) {
    super(props);
    this.state = {
      username: "",
    }
    this.getUserState = this.getUserState.bind(this);
    this.setUser = this.setUser.bind(this);
    this.getUser = this.getUser.bind(this);
  }

  componentDidMount() {
    this.getUserState();
    this.positionInterval = setInterval(this.getUserState, 1 * 60 * 1000);
  }

  componentWillUnmount() {
    clearInterval(this.positionInterval);
  }

  getUserState() {
    api.get("/api/user/")
    .then(results => {
      this.setState({username: results.data.username});
    })
    .catch(error => {
      if (error.response) {
        if(error.response.status === 404) {
          console.log("user logged out");
          this.setUser(null);
        }
      }
      console.log("user fetch error", error);
    })
  }

  setUser(username) {
    this.setState({ username: username});
  }

  getUser() {
    return this.state.username;
  }

  render () {
    if(this.state.username) {
      return (
        <LogoutForm
          setUser = {this.setUser}
          getUser = {this.getUser}
          updateMessages = {this.props.updateMessages}
        />
      )
    } else {
      return (
        <LoginForm
          setUser = {this.setUser}
          updateMessages = {this.props.updateMessages}
        />
      )
    }
  }
}

export default ProxyUser;