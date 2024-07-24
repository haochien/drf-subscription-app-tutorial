import React from 'react';
import { BrowserRouter, Routes, Route } from "react-router-dom"

import '@mantine/core/styles.css';
import { MantineProvider } from '@mantine/core';

import { theme } from './theme';
import Home from "./pages/Home"
import TestPage from './pages/TestAPI'; 
import TestDemo from './pages/TestDemo'; 
import Login from './pages/Login';
import Register from './pages/Register';


function App() {

  return (
    <MantineProvider theme={theme} defaultColorScheme="dark">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/test" element={<TestPage />} />
          <Route path="/test-demo" element={<TestDemo />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Routes>
      </BrowserRouter>
    </MantineProvider>
  )
}

export default App