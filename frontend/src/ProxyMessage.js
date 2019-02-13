import React, { Component } from 'react';
import Button from 'react-bootstrap/Button';
import Card from 'react-bootstrap/Card';
import TimeAgo from 'react-timeago';
import api from './api.js';

class ProxyMessage extends Component {
  constructor(props) {
    super(props);
    this.handleClick = this.handleClick.bind(this);
    this.deleteClick = this.deleteClick.bind(this);
  }

  handleClick() {
    this.props.setSearch(this.props.message.username);
  }
  
  deleteClick() {
    this.delete();
  }

  delete() {
    api.delete("api/message/" + this.props.message.uuid)
  }

  formatDistance(distance) {
    if(distance < 1000) {
      return `${distance} m`
    } else {
      distance = distance / 1000
      return `${distance} km`
    }
  }

  render () {
    var distance = this.formatDistance(this.props.message.distance);
    if (!this.props.message.current_user) {
      return (
        <article>
          <Card bg="light" className="mb-1">
            <Card.Body>
              <Card.Text>
                {this.props.message.message}
              </Card.Text>
            </Card.Body>
            <Card.Footer>
              <small>
                By <a href="#" onClick={this.handleClick}>{this.props.message.username}</a>
                &nbsp;within {distance}
              </small>
              <small className="message-date">
                <TimeAgo
                  date={this.props.message.date}
                  minPeriod={30}
                />
            </small>
            </Card.Footer>
          </Card>
      </article>
      )
    } else {
      return (
        <article>
          <Card bg="primary" text="white" className="mb-1">
            <Card.Body>
              <Card.Text>
                {this.props.message.message}
              </Card.Text>
              <Button variant="danger" onClick={this.deleteClick}>
                Delete
              </Button>
            </Card.Body>
            <Card.Footer>
              <small className="text-white">
                By <a href="#" onClick={this.handleClick}>{this.props.message.username}</a>
                &nbsp;within {distance}
              </small>
              <small className="text-white message-date">
                <TimeAgo
                  date={this.props.message.date}
                  minPeriod={30}
                />
              </small>
            </Card.Footer>
          </Card>
      </article>
      )
    }
  }
}

export default ProxyMessage;
