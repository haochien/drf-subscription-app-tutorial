import React, { useEffect, useState } from 'react';
import api from '../api'; 

export const TestAPI = () => {
  const [data, setData] = useState('');

  useEffect(() => {
    api.get('/auth/test')
      .then(response => {
        setData(response.data);
      });
  }, []);

  return (
    <div>
      <h1>Test API Page</h1>
      <p>My API Data:</p>
      <p>{JSON.stringify(data)}</p>
    </div>
  );
};


export const TestProtectedAPI = () => {
  const [data, setData] = useState('');

  useEffect(() => {
    api.get('/auth/test-protected')
      .then(response => {
        setData(response.data);
      });
  }, []);

  return (
    <div>
      <h1>Test Protected API Page</h1>
      <p>My Protected API Data:</p>
      <p>{JSON.stringify(data)}</p>
    </div>
  );
}