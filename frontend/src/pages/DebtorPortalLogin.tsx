import React, { useState } from 'react';
import {
  Container,
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const DebtorPortalLogin: React.FC = () => {
  const navigate = useNavigate();
  const [caseReference, setCaseReference] = useState('');
  const [debtorToken, setDebtorToken] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Verify credentials by fetching cases
      const response = await axios.get(
        `${API_BASE_URL}/api/v1/debtor-portal/cases`,
        {
          params: { case_reference: caseReference },
          headers: {
            'X-Debtor-Token': debtorToken
          }
        }
      );

      // Store token and case reference for subsequent requests
      localStorage.setItem('debtor_token', debtorToken);
      localStorage.setItem('debtor_case_reference', caseReference);
      localStorage.setItem('debtor_data', JSON.stringify(response.data));

      // Navigate to cases view
      navigate('/debtor-portal/cases');
    } catch (err: any) {
      console.error('Login failed:', err);
      setError(err.response?.data?.detail || 'Invalid credentials. Please check your case reference and token.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ py: 8 }}>
      <Paper sx={{ p: 4 }}>
        <Box mb={3} textAlign="center">
          <Typography variant="h4" component="h1" gutterBottom>
            Debtor Portal
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Access your enforcement cases
          </Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <form onSubmit={handleLogin}>
          <TextField
            fullWidth
            label="Case Reference"
            value={caseReference}
            onChange={(e) => setCaseReference(e.target.value)}
            required
            sx={{ mb: 2 }}
            placeholder="e.g., ES-20241219-ABC12345"
          />

          <TextField
            fullWidth
            label="Access Token"
            type="password"
            value={debtorToken}
            onChange={(e) => setDebtorToken(e.target.value)}
            required
            sx={{ mb: 3 }}
            placeholder="Enter your access token"
            helperText="This token was provided in your enforcement notice or letter"
          />

          <Button
            type="submit"
            fullWidth
            variant="contained"
            size="large"
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Access Cases'}
          </Button>
        </form>

        <Box mt={3} textAlign="center">
          <Typography variant="caption" color="text.secondary">
            Need help? Contact the enforcement office using the details on your notice.
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default DebtorPortalLogin;



