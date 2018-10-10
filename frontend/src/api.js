import axios from 'axios';
import config from './config.js';

axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';
axios.defaults.withCredentials = true;

console.log(config);
console.log(config.api);

axios.defaults.baseURL = config.api;

export default axios.create({
  baseURL: config.api,
});