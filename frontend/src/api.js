import axios from 'axios';
import config from './config.js';

axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';
axios.defaults.withCredentials = true;

axios.defaults.baseURL = config.api;

export default axios.create({
  baseURL: config.api,
});