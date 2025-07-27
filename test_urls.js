// Test to verify the frontend is using correct backend URL
const https = require('https');
const http = require('http');

function testEndpoint(url) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith('https:') ? https : http;
    
    const req = client.get(url, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        resolve({
          status: res.statusCode,
          headers: res.headers,
          data: data.substring(0, 200) // First 200 chars
        });
      });
    });
    
    req.on('error', (err) => {
      resolve({
        status: 'ERROR',
        error: err.message
      });
    });
    
    req.setTimeout(5000, () => {
      req.destroy();
      resolve({
        status: 'TIMEOUT',
        error: 'Request timeout'
      });
    });
  });
}

async function main() {
  console.log('🧪 Testing Backend URLs...\n');
  
  const urls = [
    'https://ai-coding-51ss.onrender.com/api/health', // New correct URL
    'https://miniapp-wvsxfa.fly.dev/api/health', // Old incorrect URL
    'http://localhost:3000/' // Local frontend
  ];
  
  for (const url of urls) {
    console.log(`Testing: ${url}`);
    const result = await testEndpoint(url);
    
    if (result.status === 200) {
      console.log(`✅ Status: ${result.status} - Working`);
    } else if (result.status === 'ERROR' || result.status === 'TIMEOUT') {
      console.log(`❌ ${result.status}: ${result.error}`);
    } else {
      console.log(`⚠️  Status: ${result.status}`);
    }
    console.log('');
  }
}

main().catch(console.error);