import React, { Component } from 'react';
import { Navbar, FormControl, FormGroup } from 'react-bootstrap';

class Header extends Component {
  constructor(props) {
    super(props);
    this.state = {
      search: null,
    }
    this.handleHomeClick = this.handleHomeClick.bind(this);
  }

  handleHomeClick() {
    this.props.setSearch("");
  }

  handleSubmit = (event) => {
    this.props.setSearch(this.state.search);
    this.setState({ search: null});
    event.preventDefault();
  }

  handleChange = (event) => {
    this.setState({ search: event.target.value});
    event.preventDefault();
  }

  formValue () {
    if(!this.state.search) {
      return this.props.search;
    } else {
      return this.state.search;
    }
  }
  
  render () {
    var formValue = this.formValue();
    return (
      <Navbar inverse>
        <Navbar.Header>
          <Navbar.Brand>
            <a onClick={this.handleHomeClick}>Proxi</a>
          </Navbar.Brand>
          <Navbar.Toggle />
        </Navbar.Header>
        <Navbar.Collapse>
          <Navbar.Form pullRight>
            <form onSubmit={this.handleSubmit}>
              <FormGroup>
                <FormControl 
                  type="text"
                  value={formValue}
                  onChange={this.handleChange}
                  placeholder="Search" />
              </FormGroup>{' '}
            </form>
          </Navbar.Form>
        </Navbar.Collapse>
      </Navbar>
    );
  }
}

export default Header;