import React, { Component } from 'react';
import axios from 'axios';
import { Button, FormGroup, FormControl } from 'react-bootstrap';
import ProxyMessageForm from './MessageForm.js';


axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

class ProxyUser extends Component {
  constructor(props) {
    super(props);
    this.state = {
      form_username: "",
      form_valid: null,
      form_error: "",
      username: "",
    }
  }

  componentDidMount() {
    console.log("fetching user state");
    fetch("/api/user/")
    .then(results => {
      return results.json();
    })
    .then(data => {
      this.setState({username: data.username});
    })
    .catch(err => console.log("user fetch error", err))
  }

  handleSubmit = (event) => {
    axios.post("api/login", {
      username: this.state.form_username,
    })
    .then(data => {
      this.setState({ username: data.data.username});
    })
    .catch(error => {
      this.setState({
        form_valid: "error",
        form_error: "Pseudo already in use, please choose another one!",
        username: null,
      })
      console.log("cannot login", error);
    })
    this.props.updateMessages();
    event.preventDefault();
  }

  handleLogout = (event) => {
    axios.post("api/logout")
    .then(data => {
      this.setState({ username: null});
    })
    .catch(error => {
      if (error.response) {
        if(error.response.status === 404) {
          console.log("already logged out");
          this.setState({ username: null});
        }
      }
      console.log("cannot logout", error);
    })
    event.preventDefault();
  }

  handleChange = (event) => {
    this.setState({ form_username: event.target.value});
    event.preventDefault();
  }

  getValidationState() {
    return this.state.form_valid;
  }
  render () {
    if(this.state.username) {
      return (
        <div>
          <ProxyMessageForm 
            updateMessages = {this.props.updateMessages}
          />
          <div>Currently logged as {this.state.username}
            <form onSubmit={this.handleLogout}>
              <FormGroup
                controlId="logoutForm"
              />
              <Button type="submit" bsStyle="default">Logout</Button>
            </form>
          </div>
        </div>
      )
    } else {
      return (
        <form onSubmit={this.handleSubmit}>
          <FormGroup
            controlId="userForm"
            validationState={this.getValidationState()}
          >
            <FormControl
              type="text"
              name="username"
              value={this.state.form_username}
              placeholder="Choose your pseudo!"
              onChange={this.handleChange}
            />
          </FormGroup>
          <Button type="submit" bsStyle="primary">Use</Button>
        </form>
      )
    }
  }
}

export default ProxyUser;