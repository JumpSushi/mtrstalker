require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const axios = require('axios');
const config = require('./config');
const logger = require('./utils/logger');
const rateLimiter = require('./middleware/rateLimiter');

// Initialize express app
const app = express();

app.use(helmet());
app.use(cors({
    origin: config.allowedOrigins,
    methods: ['GET']
}));
app.use(rateLimiter);

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'OK',
        timestamp: new Date().toISOString()
    });
});

app.get('/api/schedule', async (req, res) => {
    try {
        const { line, station } = req.query;

        if (!line || !station) {
            return res.status(400).json({
                error: 'Required parameters missing',
                details: 'Both line and station parameters are required'
            });
        }

        const response = await axios.get(config.mtrApi, {
            params: { line, station },
            timeout: 5000
        });

        logger.info('MTR API request successful', {
            line,
            station,
            status: response.status
        });

        res.json(response.data);
    } catch (error) {
        logger.error('MTR API request failed', {
            error: error.message,
            line: req.query.line,
            station: req.query.station
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
app.listen(config.port, () => {
    logger.info(`Server running on port ${config.port}`);
});

// Error handling
process.on('uncaughtException', (error) => {
    logger.error('Uncaught exception:', error);
    process.exit(1);
});

process.on('unhandledRejection', (error) => {
    logger.error('Unhandled rejection:', error);
    process.exit(1);
});

