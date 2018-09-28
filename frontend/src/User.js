import React, { Component } from 'react';
import { FormGroup, FormControl } from 'react-bootstrap';

class UserLoginForm extends Component {
  constructor(props) {
    super(props);
    this.state = {
      value: '',
    }
  }

  getValidationState() {
    return null;
  }
  render () {
    return (
      <form onSubmit={this.handleSubmit}>
        <FormGroup
          controlId="userForm"
          validationState={this.getValidationState()}
        >
          <FormControl
            type="text"
            value={this.state.value}
            placeholder="Choose your pseudo!"
            onChange={this.handleChange}
          />
        </FormGroup>
      </form>
    )
  }
}

export default UserLoginForm;