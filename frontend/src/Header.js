import React, { Component } from 'react';
import { Nav, Navbar, Form, FormControl, FormGroup, NavItem } from 'react-bootstrap';
import { NavLink } from 'react-router-dom'
import { LinkContainer } from 'react-router-bootstrap'

class Header extends Component {
  constructor(props) {
    super(props);
    this.state = {
      search: null,
    }
  }

  handleSubmit = (event) => {
    if(this.state.search !== null && this.state.search !== this.props.search) {
      this.props.setSearch(this.state.search);
      this.setState({ search: null});
    }
    event.preventDefault();
  }

  handleChange = (event) => {
    this.setState({ search: event.target.value});
    event.preventDefault();
  }

  formValue () {
    if(this.state.search === null) {
      return this.props.search;
    } else {
      return this.state.search;
    }
  }

  render () {
    var formValue = this.formValue();
    return (
      <Navbar
        bg="dark"
        collapseOnSelect
        expand="lg"
        variant="dark"
        className="mb-4"
      >
        <Navbar.Brand>
          <LinkContainer to='/'>
            <Nav.Link>Proxi</Nav.Link>
          </LinkContainer>
        </Navbar.Brand>
        <Navbar.Toggle />
        <Navbar.Collapse>
        <Nav className="mr-auto">
          <LinkContainer to='/about'>
            <Nav.Link>About</Nav.Link>
          </LinkContainer>
        </Nav>
        <Form
          inline
          onSubmit={this.handleSubmit}
        >
            <FormControl
              type="text"
              className="mr-sm-2"
              value={formValue}
              onChange={this.handleChange}
              placeholder="Search" />
        </Form>
        </Navbar.Collapse>
      </Navbar>
    );
  }
}

export default Header;