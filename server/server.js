require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const axios = require('axios');
const config = require('./config');
const logger = require('./utils/logger');
const rateLimiter = require('./middleware/rateLimiter');

const app = express();

// Middleware setup
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use(helmet());
app.use(cors({
    origin: config.allowedOrigins,
    methods: ['GET']
}));
app.use(rateLimiter);

// Basic error handling
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send('Something went wrong!');
});

app.get('/health', (req, res) => {
    res.json({
        status: 'OK',
        timestamp: new Date().toISOString()
    });
});

app.get('/api/schedule', async (req, res) => {
    try {
        const { line, sta } = req.query;

        if (!line || !sta) {
            return res.status(400).json({
                error: 'Required parameters missing',
                details: 'Both line and station parameters are required'
            });
        }

        const response = await axios.get(config.mtrApi, {
            params: { line, sta },
            timeout: 5000
        });

        logger.info('MTR API request successful', {
            line,
            sta,
            status: response.status
        });

        res.json(response.data);
    } catch (error) {
        logger.error('MTR API request failed', {
            error: error.message,
            line: req.query.line,
            sta: req.query.station
        });

        if (error.response) {
            res.status(error.response.status).json({
                error: 'MTR API error',
                details: error.response.data
            });
        } else if (error.request) {
            res.status(503).json({
                error: 'MTR API unavailable',
                details: 'Service temporarily unavailable'
            });
        } else {
            res.status(500).json({
                error: 'Internal server error',
                details: 'An unexpected error occurred'
            });
        }
    }
});

// Start server
const server = app.listen(config.port, () => {
    logger.info(`Server running on port ${config.port}`);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('Gracefully shutting down...');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});

process.on('uncaughtException', (error) => {
    logger.error('Uncaught exception:', error);
    process.exit(1);
});

process.on('unhandledRejection', (error) => {
    logger.error('Unhandled rejection:', error);
    process.exit(1);
});

module.exports = app;

