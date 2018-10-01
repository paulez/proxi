import React, { Component } from 'react';
import axios from 'axios';
import { Button, ControlLabel, FormGroup, FormControl } from 'react-bootstrap';

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

class ProxyMessageForm extends Component {
  constructor(props) {
    super(props);
    this.state = {
      form_message: "",
      form_valid: null,
      form_error: ""
    }
  }

  handleSubmit = (event) => {
    axios.post("api/message", {
      message: this.state.form_message,
    })
    .then(data => {
      this.setState({ form_message: ""});
      this.props.updateMessages();
    })
    .catch(error => {
      this.setState({
        form_valid: "error",
        form_error: "Cannot post message!",
        form_message: this.state.form_message,
      })
      console.log("cannot post message", error);
    })
    event.preventDefault();
  }

  handleChange = (event) => {
    this.setState({ form_message: event.target.value});
    event.preventDefault();
  }

  render () {
    return (
      <form onSubmit={this.handleSubmit}>
        <FormGroup
          controlId="messageForm"
        >
          <ControlLabel>Post a new Proxi message</ControlLabel>
          <FormControl
            componentClass="textarea"
            placeholder="Your message..."
            value={this.state.form_message}
            onChange={this.handleChange}
          />
          <Button type="submit" bsStyle="primary">Post</Button>
        </FormGroup>
      </form>
    )
  }
}

export default ProxyMessageForm;