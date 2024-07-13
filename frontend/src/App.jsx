import React from 'react';
import { BrowserRouter, Routes, Route } from "react-router-dom"

import { createTheme, MantineProvider } from '@mantine/core';

import Home from "./pages/Home"
import TestPage from './pages/TestAPI'; 

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
      </Routes>
    </BrowserRouter>
    </MantineProvider>
  )
}

export default App