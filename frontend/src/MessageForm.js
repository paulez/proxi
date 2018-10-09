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
      form_error: "",
      radius: null,
    }
  }

  componentDidMount() {
    this.updateRadius();
    this.radiusInterval = setInterval(this.updateRadius, 5 * 60 * 1000);
  }

  componentWillUnmount() {
    clearInterval(this.radiusInterval);
  }

  formatDistance(distance) {
    if(distance < 1000) {
      return `${distance} m`
    } else {
      distance = distance / 1000
      return `${distance} km`
    }
  }

  updateRadius() {
    axios.get("api/radius")
    .then(data => {
      this.setState({radius: data.data.radius});
    })
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

  onEnterPress = (event) => {
    if(event.keyCode == 13 && event.shiftKey == false) {
      event.preventDefault();
      this.handleSubmit(event);
    }
  }
  

  render () {
    var radius = this.formatDistance(this.state.radius);
    return (
      <form onSubmit={this.handleSubmit}>
        <FormGroup
          controlId="messageForm"
        >
          <ControlLabel>Post a new Proxi message within {radius}</ControlLabel>
          <FormControl
            componentClass="textarea"
            placeholder="Your message..."
            value={this.state.form_message}
            onChange={this.handleChange}
            onKeyDown={this.onEnterPress}
          />
          <Button type="submit" bsStyle="primary">Post</Button>
        </FormGroup>
      </form>
    )
  }
}

export default ProxyMessageForm;