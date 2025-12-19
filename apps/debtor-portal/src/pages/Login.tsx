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
      // TODO: Implement actual authentication with Enforcement API
      // For now, placeholder that accepts any code
      if (code.trim()) {
        // Store token in session (placeholder)
        sessionStorage.setItem('debtor_portal_token', 'placeholder_token')
        
        // Navigate to cases (placeholder - will show empty list)
        navigate('/case/placeholder-case-id')
      } else {
        setError(t('login.error'))
      }
    } catch (err) {
      setError(t('login.error'))
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

