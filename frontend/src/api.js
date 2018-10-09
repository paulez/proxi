import axios from 'axios';

axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';

var config = require('./config');
console.log(config);

export default axios.create({
  baseURL: config.api,
});