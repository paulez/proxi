import React, { Component } from 'react';
import { FormGroup, FormControl } from 'react-bootstrap';

class ProxyUser extends Component {
  constructor(props) {
    super(props);
    this.state = {
      form_username: '',
      username: null
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
    const form = event.target;
    const data = new FormData(form);

    fetch("api/login", {
      method: 'POST',
      body: data,
    })
    .then(response => {
      if(!response.ok) throw new Error(response.status);
      else return response.json();
    })
    .then(data => {
      this.setState({ username: data.username});
    })
    event.preventDefault();
  }

  handleChange = (event) => {
    this.setState({ form_username: event.target.value});
    event.preventDefault();
  }

  getValidationState() {
    return null;
  }
  render () {
    if(this.state.username) {
      return (
        <div>Currently logged as {this.state.username}</div>
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
        </form>
      )
    }
  }
}

export default ProxyUser;