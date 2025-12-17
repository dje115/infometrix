/**
 * Login Page - Magic Link / Code Entry
 * Placeholder for debtor portal authentication
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Alert,
} from '@mui/material';
import LanguageSelector from '../components/LanguageSelector';

const Login: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [code, setCode] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // TODO: Implement actual authentication
    // For now, placeholder - will call POST /portal/sessions
    if (code.length > 0) {
      // Placeholder: navigate to case view
      navigate(`/case/placeholder-${code}`);
    } else {
      setError(t('login.error'));
    }
  };

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Box sx={{ position: 'absolute', top: 16, right: 16 }}>
          <LanguageSelector />
        </Box>

        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          <Typography variant="h4" component="h1" gutterBottom align="center">
            {t('login.title')}
          </Typography>

          <Typography variant="body1" color="text.secondary" align="center" sx={{ mb: 3 }}>
            {t('login.enterCode')}
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label={t('login.codePlaceholder')}
              value={code}
              onChange={(e) => setCode(e.target.value)}
              margin="normal"
              required
              autoFocus
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
            >
              {t('login.submit')}
            </Button>
          </form>
        </Paper>
      </Box>
    </Container>
  );
};

export default Login;

