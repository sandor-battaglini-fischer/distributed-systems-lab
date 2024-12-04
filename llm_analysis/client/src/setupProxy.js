const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Proxy API requests
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:5000',
      changeOrigin: true,
      logLevel: 'debug',
      timeout: 60000,
      proxyTimeout: 61000,
      ws: false,
      onError: (err, req, res) => {
        console.error('Proxy Error:', err);
        res.writeHead(500, {
          'Content-Type': 'application/json',
        });
        res.end(JSON.stringify({ 
          success: false,
          error: 'Connection error occurred',
          details: err.code === 'ECONNRESET' ? 'Server connection was reset. Please try again.' : err.message 
        }));
      },
      onProxyReq: (proxyReq, req, res) => {
        proxyReq.setHeader('Connection', 'keep-alive');
        
        if (req.method === 'POST' && req.body) {
          const bodyData = JSON.stringify(req.body);
          proxyReq.setHeader('Content-Type', 'application/json');
          proxyReq.setHeader('Content-Length', Buffer.byteLength(bodyData));
          proxyReq.write(bodyData);
        }
      },
      onProxyRes: (proxyRes, req, res) => {
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
        res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
        res.setHeader('Connection', 'keep-alive');
      }
    })
  );

  // Proxy plot static files
  app.use(
    '/static/plots',
    createProxyMiddleware({
      target: 'http://localhost:5000',
      changeOrigin: true,
      logLevel: 'debug',
      timeout: 60000,
      proxyTimeout: 61000,
      ws: false,
      onError: (err, req, res) => {
        console.error('Static Plot Proxy Error:', err);
        res.writeHead(500, {
          'Content-Type': 'application/json',
        });
        res.end(JSON.stringify({ 
          success: false,
          error: 'Failed to load plot',
          details: err.message 
        }));
      },
      onProxyReq: (proxyReq, req, res) => {
        proxyReq.setHeader('Connection', 'keep-alive');
      },
      onProxyRes: (proxyRes, req, res) => {
        res.setHeader('Connection', 'keep-alive');
      }
    })
  );
};