import React from 'react';

const URLDebugger = () => {
  const backendUrl = process.env.REACT_APP_BACKEND_URL;
  const apiUrl = `${backendUrl}/api`;
  
  return (
    <div style={{
      position: 'fixed',
      top: '10px',
      right: '10px',
      background: 'black',
      color: 'white',
      padding: '10px',
      borderRadius: '5px',
      zIndex: 9999,
      fontSize: '12px',
      maxWidth: '300px'
    }}>
      <div><strong>Debug Info:</strong></div>
      <div>Backend URL: {backendUrl}</div>
      <div>API URL: {apiUrl}</div>
      <div>Time: {new Date().toLocaleTimeString()}</div>
    </div>
  );
};

export default URLDebugger;