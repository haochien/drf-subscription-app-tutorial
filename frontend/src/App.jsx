import React from 'react';
import { BrowserRouter, Routes, Route } from "react-router-dom"

import '@mantine/core/styles.css';
import { MantineProvider } from '@mantine/core';

import { theme } from './theme';
import Home from "./pages/Home"
import { TestAPI, TestProtectedAPI } from './pages/TestAPI'; 
import TestDemo from './pages/TestDemo'; 
import Login from './pages/Login';
import ProtectedRoute from "./components/ProtectedRoute"


function App() {

  return (
    <MantineProvider theme={theme} defaultColorScheme="dark">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/test" element={<TestAPI />} />
          <Route path="/test-protected" element={
            <ProtectedRoute>
              <TestProtectedAPI />
            </ProtectedRoute>
          } />
          <Route path="/test-demo" element={<TestDemo />} />
        </Routes>
      </BrowserRouter>
    </MantineProvider>
  )
}

export default App