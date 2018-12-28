const dev = {
  api: "https://localhost:8000/",
};

const prod = {
  api: "https://api.prxi.net/",
};

const config = process.env.REACT_APP_STAGE === 'dev'
  ? dev
  : prod;

  export default config;