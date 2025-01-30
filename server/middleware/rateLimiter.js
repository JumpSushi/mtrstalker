const rateLimit = require('express-rate-limit');
const config = require('../config')
const limiter = rateLimit(config.rateLimit);
module.exports = limiter;

