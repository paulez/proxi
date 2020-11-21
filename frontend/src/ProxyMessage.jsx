import React, { Component } from 'react';
import Button from 'react-bootstrap/Button';
import Card from 'react-bootstrap/Card';
import TimeAgo from 'react-timeago';
import Linkify from 'react-linkify';
import api from './api';

class ProxyMessage extends Component {
  constructor(props) {
    super(props);
    this.handleClick = this.handleClick.bind(this);
    this.deleteClick = this.deleteClick.bind(this);
  }

  handleClick() {
    this.props.setSearch(this.props.message.user.username);
  }
  
  deleteClick() {
    api.delete("api/message/" + this.props.message.uuid)
    .then(data => {
      this.props.updateMessages();
    })
  }

  formatDistance(distance) {
    if(distance < 1000) {
      return `${distance} m`;
    } else {
      distance = distance / 1000;
      return `${distance} km`;
    }
  }

  whiteLinkDecorator = (href, text, key) => (
    <a
      href={href}
      key={key}
      target="_blank"
      style= {{color: 'white'}}
      >
      {text}
    </a>
  );

  blankLinkDecorator = (href, text, key) => (
    <a
      href={href}
      key={key}
      target="_blank"
      >
      {text}
    </a>
  );

  render () {
    var distance = this.formatDistance(this.props.message.distance);
    let user = this.props.getUser();
    if (user && this.props.message.user.uuid == user.uuid) {
      return (
        <article>
          <Card bg="primary" text="white" className="mb-1">
            <Card.Body>
              <Card.Text>
		<Linkify
		  componentDecorator={this.whiteLinkDecorator}
		  >
                  {this.props.message.message}
		</Linkify>
                <Button
                  className="delete-button"
                  size="sm"
                  variant="danger"
                  onClick={this.deleteClick}
                >
                  Delete
                </Button>
              </Card.Text>
            </Card.Body>
            <Card.Footer>
              <small className="text-white">
                From <a href="#" className="text-white" onClick={this.handleClick}>{this.props.message.username}</a>
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
      );
    } else {
      return (
        <article>
          <Card bg="light" className="mb-1">
            <Card.Body>
              <Card.Text>
		<Linkify
		  componentDecorator={this.blankLinkDecorator}
		  >
                  {this.props.message.message}
		</Linkify>
              </Card.Text>
            </Card.Body>
            <Card.Footer>
              <small>
                From <a href="#" onClick={this.handleClick}>{this.props.message.user.username}</a>
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
      );
    }
  }
}

export default ProxyMessage;
