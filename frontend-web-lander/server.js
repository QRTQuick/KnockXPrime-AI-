const express = require('express');
const path = require('path');
const compression = require('compression');
const helmet = require('helmet');

const app = express();
const PORT = process.env.PORT || 3000;

// Security middleware
app.use(helmet({
    contentSecurityPolicy: {
        directives: {
            defaultSrc: ["'self'"],
            styleSrc: ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com", "https://cdnjs.cloudflare.com"],
            fontSrc: ["'self'", "https://fonts.gstatic.com", "https://cdnjs.cloudflare.com"],
            scriptSrc: ["'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com"],
            imgSrc: ["'self'", "data:", "https:"],
            connectSrc: ["'self'"]
        }
    }
}));

// Compression middleware
app.use(compression());

// Static file serving with caching
app.use(express.static(path.join(__dirname), {
    maxAge: '1d', // Cache static files for 1 day
    etag: true,
    lastModified: true
}));

// Set proper MIME types
app.use((req, res, next) => {
    if (req.path.endsWith('.css')) {
        res.type('text/css');
    } else if (req.path.endsWith('.js')) {
        res.type('application/javascript');
    } else if (req.path.endsWith('.svg')) {
        res.type('image/svg+xml');
    }
    next();
});

// Routes for all HTML pages
const pages = [
    'index',
    'product',
    'features', 
    'pricing',
    'api',
    'about',
    'blog',
    'careers',
    'contact',
    'help',
    'status',
    'privacy',
    'terms'
];

// Serve HTML pages
pages.forEach(page => {
    app.get(`/${page === 'index' ? '' : page}`, (req, res) => {
        const filePath = path.join(__dirname, `${page}.html`);
        res.sendFile(filePath, (err) => {
            if (err) {
                res.status(404).sendFile(path.join(__dirname, '404.html'));
            }
        });
    });
});

// Handle 404 errors
app.use((req, res) => {
    res.status(404).sendFile(path.join(__dirname, '404.html'), (err) => {
        if (err) {
            res.status(404).send(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>404 - Page Not Found</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        h1 { color: #FF6B35; }
                        a { color: #1E90FF; text-decoration: none; }
                    </style>
                </head>
                <body>
                    <h1>404 - Page Not Found</h1>
                    <p>The page you're looking for doesn't exist.</p>
                    <a href="/">← Back to Home</a>
                </body>
                </html>
            `);
        }
    });
});

// Health check endpoint for Render
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        service: 'KnockXPrime AI Frontend',
        version: '1.0.0'
    });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 KnockXPrime AI Frontend running on port ${PORT}`);
    console.log(`📱 Environment: ${process.env.NODE_ENV || 'development'}`);
    console.log(`🌐 Access at: http://localhost:${PORT}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('👋 Received SIGTERM, shutting down gracefully');
    process.exit(0);
});

process.on('SIGINT', () => {
    console.log('👋 Received SIGINT, shutting down gracefully');
    process.exit(0);
});