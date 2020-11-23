import React, { Component } from 'react';
import api from './api';
import { Button, FormLabel, FormGroup, FormControl } from 'react-bootstrap';

class ProxyMessageForm extends Component {
  constructor(props) {
    super(props);
    this.state = {
      form_message: "",
      form_valid: null,
      form_error: "",
      radius: null,
    };
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.onEnterPress = this.onEnterPress.bind(this);
    this.updateRadius = this.updateRadius.bind(this);
  }

  componentDidMount() {
    this.updateRadius();
    this.radiusInterval = setInterval(this.updateRadius, 5 * 60 * 1000);
    this.messageInput.focus();
  }

  componentWillUnmount() {
    clearInterval(this.radiusInterval);
  }

  componentDidUpdate(prevProps, prevState) {
    if(prevProps.location != this.props.location) {
      this.updateRadius();
    }
  }

  formatRadius() {
    if(this.state.radius == null) {
      return "unknown distance";
    }
    if(this.state.radius < 1000) {
      return `${this.state.radius} m`;
    } else {
      return `${this.state.radius / 1000} km`;
    }
  }

  updateRadius() {
    if(this.props.location) {
      let message_params;
      message_params = {
        latitude: this.props.location.latitude,
        longitude: this.props.location.longitude,
      };
      api.get("api/radius", {
        params: message_params
      })
         .then(result => {
           this.setState({radius: result.data.radius});
         })
         .catch(error => {console.log("Cannot get radius")});
    }
  }

  handleSubmit(event) {
    api.post("api/message", {
      message: this.state.form_message,
      location: this.props.location,
    }, {
      headers: {
        'Authorization': `token ${this.props.getToken()}`
      },
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
      });
      console.log("cannot post message", error);
    });
    event.preventDefault();
  }

  handleChange(event) {
    this.setState({ form_message: event.target.value});
    event.preventDefault();
  }

  onEnterPress(event) {
    if(event.keyCode === 13 && event.shiftKey === false) {
      event.preventDefault();
      this.handleSubmit(event);
    }
  }


  render () {
    return (
      <form onSubmit={this.handleSubmit}>
        <FormGroup
          controlId="messageForm"
        >
          <FormLabel>Post a new Proxi message within {this.formatRadius()}</FormLabel>
          <FormControl
            as="textarea"
            placeholder="Your message..."
            value={this.state.form_message}
            onChange={this.handleChange}
            onKeyDown={this.onEnterPress}
            ref={ref => { this.messageInput = ref; }}
          />
          <Button type="submit" variant="primary">Post</Button>
        </FormGroup>
      </form>
    );
  }
}

export default ProxyMessageForm;
