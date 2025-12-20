import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import Login from './pages/Login'
import CaseView from './pages/CaseView'
import LanguageSelector from './components/LanguageSelector'

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
})

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
          {/* Language selector at top */}
          <div style={{ padding: '16px', display: 'flex', justifyContent: 'flex-end' }}>
            <LanguageSelector />
          </div>
          
          {/* Main content */}
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/case/:caseId" element={<CaseView />} />
            <Route path="/" element={<Navigate to="/login" replace />} />
          </Routes>
        </div>
      </BrowserRouter>
    </ThemeProvider>
  )
}

export default App



