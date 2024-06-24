import React, { useState, useEffect } from 'react';
import api from './api';

function App() {
  const [data, setData] = useState('');

  useEffect(() => {
    api.get('/auth/test')
      .then(response => {
        setData(response.data);
      });
  }, []);

  return (
    <>
      <p>{JSON.stringify(data)}</p>
    </>
  )
}

export default App