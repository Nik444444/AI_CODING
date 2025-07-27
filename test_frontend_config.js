// Test script to verify frontend configuration
const fs = require('fs');
const path = require('path');

console.log('🔍 Checking Frontend Configuration...');

// Check .env file
const envPath = path.join(__dirname, 'frontend', '.env');
try {
  const envContent = fs.readFileSync(envPath, 'utf8');
  console.log('📄 Frontend .env file content:');
  console.log(envContent);
  
  if (envContent.includes('https://ai-coding-51ss.onrender.com')) {
    console.log('✅ Backend URL correctly updated to render.com');
  } else {
    console.log('❌ Backend URL not found or incorrect');
  }
} catch (error) {
  console.log('❌ Could not read .env file:', error.message);
}

// Check service file
const servicePath = path.join(__dirname, 'frontend', 'src', 'services', 'api.js');
try {
  const serviceContent = fs.readFileSync(servicePath, 'utf8');
  console.log('\n📄 API Service configuration:');
  
  const backendUrlLine = serviceContent.split('\n').find(line => 
    line.includes('REACT_APP_BACKEND_URL')
  );
  
  if (backendUrlLine) {
    console.log('Backend URL line:', backendUrlLine.trim());
    console.log('✅ Service correctly uses environment variable');
  } else {
    console.log('❌ Backend URL environment variable usage not found');
  }
} catch (error) {
  console.log('❌ Could not read api.js file:', error.message);
}

console.log('\n🎯 Next steps:');
console.log('1. Clear browser cache');
console.log('2. Test API key creation through frontend');
console.log('3. Check browser network tab for actual requests');