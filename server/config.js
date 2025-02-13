require('dotenv').config();

const config = {
    port: process.env.PORT || 39507,
    allowedOrigins: process.env.ALLOWED_ORIGINS || '*',
    rateLimit: {
        windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 15 * 60 * 1000,
        max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 100
    },
    mtrApi: process.env.MTR_API_URL || 'https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php',
    logging: {
        level: process.env.LOG_LEVEL || 'info',
        files: {
            error: 'error.log',
            combined: 'combined.log'
        }
    }
};

module.exports = config;