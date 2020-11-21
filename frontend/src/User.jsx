import React, { Component } from 'react';
import api from './api';
import { Button, FormGroup, FormControl, FormLabel } from 'react-bootstrap';
import ProxyMessageForm from './MessageForm';

class LogoutForm extends Component {
  constructor(props) {
    super(props);
    this.state = {
      form_valid: null,
      form_error: "",
    }
  }

  handleLogout = (event) => {
    this.props.setUser(null);
    this.props.setToken(null);
  }

  getValidationState() {
    return this.state.form_valid;
  }

  render () {
    var user = this.props.getUser()
    return (
      <div>
        <ProxyMessageForm
          updateMessages = {this.props.updateMessages}
          location = {this.props.location}
          getToken = {this.props.getToken}
        />
        <form onSubmit={this.handleLogout}>
          <FormGroup controlId="logoutForm">
          <span>
            <FormLabel>Currently known as <mark>{user.username}</mark></FormLabel>
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
    api.post("api/register", {
      username: this.state.form_username,
      location: this.props.location,
    })
    .then(results => {
      this.props.setUser(results.data);
      this.props.setToken(results.data.token);
    })
    .catch(error => {
      this.props.setUser(null);
      if (error.response && error.response.status) {
	const status = error.response.status;
	if (status === 409) {
	  this.setState({
            form_valid: "error",
            form_error: "Pseudo already in use, please choose another one!",
	  });
	} else if (status === 404) {
	  this.setState({
	    form_valid: "error",
	    form_error: "Cannot find your location, please allow sharing your location!",
	  });
        } else {
          this.setState({
            form_valid: "error",
            form_error: "Login error, please retry."
          });
	}
      } else {
	this.setState({
	  form_valid: "error",
	  form_error: "Login error, please retry.",
	});
      }
      console.log("cannot login", error);
    });
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
	  isInvalid={this.state.form_valid}
          placeholder="Choose your pseudo!"
          onChange={this.handleChange}
          ref={ref => { this.usernameInput = ref; }}
          />
	  <FormControl.Feedback type="invalid">
	    {this.state.form_error}
	  </FormControl.Feedback>
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
      user: null,
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
    var token = this.props.getToken();
    api.get("/api/user/", {
      headers: {
        'Authorization': `token ${token}`
      }
    })
    .then(results => {
      this.setState({user: results.data});
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

  setUser(userData) {
    this.setState({ user: userData});
  }

  getUser() {
    return this.state.user;
  }

  render () {
    if(this.state.user) {
      return (
        <LogoutForm
          setUser = {this.setUser}
          getUser = {this.getUser}
          updateMessages = {this.props.updateMessages}
          location = {this.props.location}
          getToken = {this.props.getToken}
          setToken = {this.props.setToken}
        />
      )
    } else {
      return (
        <LoginForm
          setUser = {this.setUser}
          updateMessages = {this.props.updateMessages}
          location = {this.props.location}
          setToken = {this.props.setToken}
        />
      )
    }
  }
}

export default ProxyUser;
