/**
 * Case View Page - Read-only case details
 * Displays case information with localized labels
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Container,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  Button,
} from '@mui/material';
import LanguageSelector from '../components/LanguageSelector';

const CaseView: React.FC = () => {
  const { t } = useTranslation();
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // TODO: Fetch case data from Enforcement API
    // GET /portal/cases/:caseId with portal token
    setTimeout(() => {
      setLoading(false);
      // Placeholder: no case data yet
    }, 1000);
  }, [caseId]);

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
        }}
      >
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>{t('common.loading')}</Typography>
      </Box>
    );
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ position: 'absolute', top: 16, right: 16 }}>
        <LanguageSelector />
      </Box>

      <Box sx={{ mt: 4, mb: 2 }}>
        <Button onClick={() => navigate('/login')}>{t('common.back')}</Button>
      </Box>

      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {t('case.title')}
        </Typography>

        {error ? (
          <Alert severity="error">{error}</Alert>
        ) : (
          <Box>
            <Typography variant="body1" color="text.secondary">
              {t('case.noCaseFound')}
            </Typography>
            <Typography variant="body2" sx={{ mt: 2 }}>
              Case ID: {caseId}
            </Typography>
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default CaseView;

