/**
 * Login Page for Debtor Portal
 * 
 * Supports magic link / code entry (placeholder for now).
 * All strings are translated via i18n.
 */

import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert
} from '@mui/material'
import { debtorPortalAPI } from '../services/api'

const Login: React.FC = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [code, setCode] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (!code.trim()) {
        setError(t('login.error'))
        setLoading(false)
        return
      }
      
      // Get current language
      const locale = localStorage.getItem('debtor_portal_language') || 'en'
      
      // Create portal session with Enforcement API
      const session = await debtorPortalAPI.createSession(code.trim(), locale)
      
      // Store token in session
      sessionStorage.setItem('debtor_portal_token', session.token)
      sessionStorage.setItem('debtor_portal_language', session.locale)
      
      // Navigate to case view
      navigate(`/case/${session.case_id}`)
    } catch (err: any) {
      console.error('Login error:', err)
      setError(err.response?.data?.detail || t('login.error'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container maxWidth="sm" sx={{ mt: 8 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          {t('login.title')}
        </Typography>
        
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
          <TextField
            fullWidth
            label={t('login.enterCode')}
            placeholder={t('login.codePlaceholder')}
            value={code}
            onChange={(e) => setCode(e.target.value)}
            margin="normal"
            required
            autoFocus
          />
          
          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
          
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={loading}
          >
            {loading ? t('login.loading') : t('login.submit')}
          </Button>
        </Box>
      </Paper>
    </Container>
  )
}

export default Login

