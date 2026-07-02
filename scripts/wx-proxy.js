/**
 * 微信API反向代理
 * 用法: WECHAT_PROXY_TOKEN=你的token node wx-proxy.js
 */
const http = require('http');
const https = require('https');
const url = require('url');

const PROXY_PORT = process.env.WECHAT_PROXY_PORT || 8787;
const TARGET_HOST = 'api.weixin.qq.com';
const AUTH_TOKEN = process.env.WECHAT_PROXY_TOKEN || '';

const ALLOWED_PATHS = [
  '/cgi-bin/token',
  '/cgi-bin/material',
  '/cgi-bin/draft',
  '/cgi-bin/freepublish',
  '/cgi-bin/media',
];

function isPathAllowed(pathname) {
  return ALLOWED_PATHS.some(p => pathname.startsWith(p));
}

function jsonRes(res, data, status = 200) {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(data, null, 2));
}

const server = http.createServer((req, res) => {
  const parsed = url.parse(req.url);
  const pathname = parsed.pathname;

  if (pathname === '/health') {
    return jsonRes(res, { status: 'ok', proxy: 'wx-api-proxy' });
  }

  if (AUTH_TOKEN) {
    const headerToken = req.headers['x-publish-token'] ||
                       (req.headers['authorization'] || '').replace('Bearer ', '');
    if (headerToken !== AUTH_TOKEN) {
      return jsonRes(res, { error: 'unauthorized' }, 401);
    }
  }

  if (!isPathAllowed(pathname)) {
    return jsonRes(res, { error: 'path not allowed: ' + pathname }, 403);
  }

  const chunks = [];
  req.on('data', chunk => chunks.push(chunk));
  req.on('end', () => {
    const body = chunks.length > 0 ? Buffer.concat(chunks) : null;

    const options = {
      hostname: TARGET_HOST,
      port: 443,
      path: req.url,
      method: req.method,
      headers: {
        'Content-Type': req.headers['content-type'] || 'application/json',
        'Host': TARGET_HOST,
      },
    };

    if (body) {
      options.headers['Content-Length'] = body.length;
    }

    const proxyReq = https.request(options, (proxyRes) => {
      res.writeHead(proxyRes.statusCode, proxyRes.headers);
      proxyRes.pipe(res);
    });

    proxyReq.on('error', (err) => {
      console.error('[PROXY ERROR]', err.message);
      jsonRes(res, { error: 'proxy error: ' + err.message }, 502);
    });

    if (body) {
      proxyReq.write(body);
    }
    proxyReq.end();
  });
});

server.listen(PROXY_PORT, '0.0.0.0', () => {
  console.log(`微信API代理已启动 端口:${PROXY_PORT}`);
  console.log(`测试: curl http://localhost:${PROXY_PORT}/health`);
});