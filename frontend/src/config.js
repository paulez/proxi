const dev = {
  api: "https://localhost:8000/",
}

const prod = {
  api: "https://prxi.net/",
}

const config = process.env.REACT_APP_STAGE === 'production'
  ? prod
  : dev;

  export default {
      config
  };