import React from 'react';
import { BrowserRouter, Routes, Route } from "react-router-dom"

import '@mantine/core/styles.css';
import { createTheme, MantineProvider } from '@mantine/core';

import Home from "./pages/Home"
import TestPage from './pages/TestAPI'; 
import Login from './pages/Login';
import Register from './pages/Register';

const theme = createTheme({
  /** Put your mantine theme override here */
});

function App() {

  return (
    <MantineProvider theme={theme}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/test" element={<TestPage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Routes>
      </BrowserRouter>
    </MantineProvider>
  )
}

export default App