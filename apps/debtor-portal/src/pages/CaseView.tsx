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
  Grid,
} from '@mui/material';
import LanguageSelector from '../components/LanguageSelector';
import { portalAPI, CaseData } from '../services/api';

const CaseView: React.FC = () => {
  const { t, i18n } = useTranslation();
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [caseData, setCaseData] = useState<CaseData | null>(null);

  useEffect(() => {
    const fetchCase = async () => {
      if (!caseId) {
        setError(t('case.noCaseFound'));
        setLoading(false);
        return;
      }

      try {
        // Fetch case data with portal token
        // Locale is passed via Accept-Language header automatically by axios
        const data = await portalAPI.getCase(caseId);
        setCaseData(data);
      } catch (err: any) {
        setError(err.response?.data?.detail || t('common.error'));
      } finally {
        setLoading(false);
      }
    };

    fetchCase();
  }, [caseId, t]);

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
        ) : caseData ? (
          <Grid container spacing={2} sx={{ mt: 2 }}>
            <Grid item xs={12}>
              <Typography variant="body2" color="text.secondary">
                {t('case.caseNumber')}
              </Typography>
              <Typography variant="body1">{caseData.case_number}</Typography>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="body2" color="text.secondary">
                {t('case.status')}
              </Typography>
              <Typography variant="body1">{caseData.status}</Typography>
            </Grid>
            {caseData.amount && (
              <Grid item xs={12}>
                <Typography variant="body2" color="text.secondary">
                  {t('case.amount')}
                </Typography>
                <Typography variant="body1">{caseData.amount}</Typography>
              </Grid>
            )}
            {caseData.due_date && (
              <Grid item xs={12}>
                <Typography variant="body2" color="text.secondary">
                  {t('case.dueDate')}
                </Typography>
                <Typography variant="body1">{caseData.due_date}</Typography>
              </Grid>
            )}
            {caseData.description && (
              <Grid item xs={12}>
                <Typography variant="body2" color="text.secondary">
                  {t('case.description')}
                </Typography>
                <Typography variant="body1">{caseData.description}</Typography>
              </Grid>
            )}
          </Grid>
        ) : (
          <Typography variant="body1" color="text.secondary">
            {t('case.noCaseFound')}
          </Typography>
        )}
      </Paper>
    </Container>
  );
};

export default CaseView;

