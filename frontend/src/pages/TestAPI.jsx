import React, { useEffect, useState } from 'react';
import api from '../api'; 

const TestPage = () => {
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

export default TestPage;