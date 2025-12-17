/**
 * Debtor Portal Main Application
 * Multilingual React application for debtors
 */

import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Initialize i18n
import './i18n/config';

// Pages
import Login from './pages/Login';
import CaseView from './pages/CaseView';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/login" element={<Login />} />
          <Route path="/case/:caseId" element={<CaseView />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;

