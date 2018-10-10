const dev = {
  api: "https://proxi-dev-1:8000/",
};

const prod = {
  api: "https://api.prxi.net/",
};

const config = process.env.REACT_APP_STAGE === 'production'
  ? prod
  : dev;

  export default config;