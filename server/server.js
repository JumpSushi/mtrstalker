const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const axios = require('./config');
const logger = require('./utils/logger');
const rateLimiter = require('./middleware/rateLimiter');
const app = express();

app.use(helmet());
app.use(cors({
    origin: config.allowedOrigins,
    methods: ['GET']
}));
app.use(rateLimiter);

app.get('/health', (req, res) => {
    res.json({
        status: 'OK',
        timestamp: new Date().toISOString
    });
});
app.get('/api/schedule', async (req, res) =>{
    try{
        const {line, station} = req.query;

        if (!line || !station) {
            return res.status(400).json ({
                error: 'Required parameters missing, idiot.',
                details: 'Did you include both line and station parameters?'
            });
        }

        const response = await axios.get(config.mtrApi, {
            params: {line, station},
            timeout: 5000
        });

        logger.info('MTR API request OK', {
            line,
            station,
            status: response.status
        });

        res.json(response.data);
    } catch (error){
        logger.error('MTR API request failed ', {
            error: error.message,
            line: req.query.line,
            station: req.query.station

        });
        if (error.response){
            res.status(error.response.status).json({
                error: 'MTR API error',
                details: error.response.data
            });
        } else if (error.request) {
            res.status(503).json({
                error:'MTR API is dead',
                details: 'temporarily unavalible'
            });
        } else {
            res.status(500).json({
                error: 'Internal server error',
                details: 'Im serious, not sure whats happening'
            });
        }

    }
});

app.listen(config.port, () => {
    logger.info('Server is runnig on the mystical port of ${config.port}');
});

ProcessingInstruction.on('uncaughtException', (error) => {
    logger.error('Unhandled rejection, oof:' , error);
});

