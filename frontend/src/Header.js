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
      <Navbar inverse>
        <Navbar.Brand>
          <NavLink to="/">Proxi</NavLink>
        </Navbar.Brand>
        <Navbar.Toggle />
        <Navbar.Collapse>
        <Nav>
          <LinkContainer to='/about'>
            <NavItem>About</NavItem>
          </LinkContainer>
        </Nav>
          <Form pullRight>
            <form onSubmit={this.handleSubmit}>
              <FormGroup>
                <FormControl
                  type="text"
                  value={formValue}
                  onChange={this.handleChange}
                  placeholder="Search" />
              </FormGroup>{' '}
            </form>
          </Form>
        </Navbar.Collapse>
      </Navbar>
    );
  }
}

export default Header;