import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  Grid
} from '@mui/material';
import {
  Logout as LogoutIcon,
  Visibility as ViewIcon,
  AccountBalance as AccountBalanceIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Case {
  id: string;
  case_reference: string;
  client_reference?: string;
  case_type: string;
  status: string;
  original_amount: number;
  current_balance: number;
  payments_received: number;
  opened_date?: string;
  legal_basis?: string;
}

interface DebtorData {
  debtor: {
    legal_name: string;
    entity_type: string;
  };
  cases: Case[];
}

const DebtorPortalCases: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<DebtorData | null>(null);

  useEffect(() => {
    loadCases();
  }, []);

  const loadCases = async () => {
    try {
      setLoading(true);
      setError(null);

      const caseReference = localStorage.getItem('debtor_case_reference');
      const token = localStorage.getItem('debtor_token');

      if (!caseReference || !token) {
        navigate('/debtor-portal/login');
        return;
      }

      const response = await axios.get(
        `${API_BASE_URL}/api/v1/debtor-portal/cases`,
        {
          params: { case_reference: caseReference },
          headers: {
            'X-Debtor-Token': token
          }
        }
      );

      setData(response.data);
    } catch (err: any) {
      console.error('Failed to load cases:', err);
      if (err.response?.status === 401) {
        // Token expired or invalid
        localStorage.removeItem('debtor_token');
        localStorage.removeItem('debtor_case_reference');
        localStorage.removeItem('debtor_data');
        navigate('/debtor-portal/login');
      } else {
        setError(err.response?.data?.detail || 'Failed to load cases');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('debtor_token');
    localStorage.removeItem('debtor_case_reference');
    localStorage.removeItem('debtor_data');
    navigate('/debtor-portal/login');
  };

  const handleViewCase = (caseId: string) => {
    navigate(`/debtor-portal/cases/${caseId}`);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: 'GBP'
    }).format(amount);
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning'> = {
      draft: 'default',
      active: 'primary',
      on_hold: 'warning',
      settled: 'success',
      closed: 'info',
      cancelled: 'error'
    };
    return colors[status] || 'default';
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error && !data) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box mb={3} display="flex" justifyContent="space-between" alignItems="center">
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Your Enforcement Cases
          </Typography>
          {data && (
            <Typography variant="body2" color="text.secondary">
              {data.debtor.legal_name}
            </Typography>
          )}
        </Box>
        <Button
          startIcon={<LogoutIcon />}
          onClick={handleLogout}
          variant="outlined"
        >
          Logout
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {data && (
        <>
          {/* Summary Card */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Box textAlign="center">
                    <Typography variant="body2" color="text.secondary">
                      Total Cases
                    </Typography>
                    <Typography variant="h5">{data.cases.length}</Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Box textAlign="center">
                    <Typography variant="body2" color="text.secondary">
                      Total Balance
                    </Typography>
                    <Typography variant="h5" color="error.main">
                      {formatCurrency(
                        data.cases.reduce((sum, c) => sum + c.current_balance, 0)
                      )}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Box textAlign="center">
                    <Typography variant="body2" color="text.secondary">
                      Payments Made
                    </Typography>
                    <Typography variant="h5" color="success.main">
                      {formatCurrency(
                        data.cases.reduce((sum, c) => sum + c.payments_received, 0)
                      )}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Cases Table */}
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Case Reference</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Original Amount</TableCell>
                  <TableCell align="right">Current Balance</TableCell>
                  <TableCell align="right">Payments</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {data.cases.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      <Typography color="text.secondary" sx={{ py: 4 }}>
                        No cases found
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  data.cases.map((caseItem) => (
                    <TableRow key={caseItem.id} hover>
                      <TableCell>
                        <Typography variant="body2" fontWeight="bold">
                          {caseItem.case_reference}
                        </Typography>
                        {caseItem.client_reference && (
                          <Typography variant="caption" color="text.secondary">
                            Client Ref: {caseItem.client_reference}
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        {caseItem.case_type.split('_').map(word => 
                          word.charAt(0).toUpperCase() + word.slice(1)
                        ).join(' ')}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={caseItem.status.charAt(0).toUpperCase() + caseItem.status.slice(1).replace('_', ' ')}
                          color={getStatusColor(caseItem.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="right">
                        {formatCurrency(caseItem.original_amount)}
                      </TableCell>
                      <TableCell align="right">
                        <Typography
                          variant="body2"
                          fontWeight="bold"
                          color={caseItem.current_balance > 0 ? 'error.main' : 'success.main'}
                        >
                          {formatCurrency(caseItem.current_balance)}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        {formatCurrency(caseItem.payments_received)}
                      </TableCell>
                      <TableCell>
                        <Button
                          size="small"
                          startIcon={<ViewIcon />}
                          onClick={() => handleViewCase(caseItem.id)}
                        >
                          View
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </>
      )}
    </Container>
  );
};

export default DebtorPortalCases;

