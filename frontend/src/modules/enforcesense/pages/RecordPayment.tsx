import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Divider,
  IconButton
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Save as SaveIcon,
  Cancel as CancelIcon
} from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';
import { enforcesenseAPI } from '../../../services/enforcesenseAPI';

const RecordPayment: React.FC = () => {
  const navigate = useNavigate();
  const { caseId } = useParams<{ caseId: string }>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [caseData, setCaseData] = useState<any>(null);
  const [balance, setBalance] = useState<any>(null);
  
  const [paymentData, setPaymentData] = useState({
    amount: '',
    payment_method: 'bank_transfer',
    payment_reference: '',
    description: ''
  });

  useEffect(() => {
    if (caseId) {
      loadCase();
      loadBalance();
    }
  }, [caseId]);

  const loadCase = async () => {
    try {
      const response = await enforcesenseAPI.getCase(caseId!);
      setCaseData(response.data);
    } catch (err: any) {
      console.error('Failed to load case:', err);
      setError(err.response?.data?.detail || 'Failed to load case');
    }
  };

  const loadBalance = async () => {
    try {
      const response = await enforcesenseAPI.getCaseBalance(caseId!);
      setBalance(response.data);
    } catch (err) {
      console.error('Failed to load balance:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!paymentData.amount || parseFloat(paymentData.amount) <= 0) {
      setError('Please enter a valid payment amount');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      await enforcesenseAPI.recordPayment(caseId!, {
        amount: parseFloat(paymentData.amount),
        payment_method: paymentData.payment_method,
        payment_reference: paymentData.payment_reference || undefined,
        description: paymentData.description || undefined
      });
      
      navigate(`/enforcesense/cases/${caseId}`);
    } catch (err: any) {
      console.error('Failed to record payment:', err);
      setError(err.response?.data?.detail || 'Failed to record payment');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: 'GBP'
    }).format(amount);
  };

  return (
    <Container maxWidth="md" sx={{ py: 3 }}>
      <Box mb={3} display="flex" alignItems="center" gap={2}>
        <IconButton onClick={() => navigate(`/enforcesense/cases/${caseId}`)}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h4" component="h1">
          Record Payment
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Payment Details
            </Typography>
            <form onSubmit={handleSubmit}>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Payment Amount *"
                    type="number"
                    value={paymentData.amount}
                    onChange={(e) => setPaymentData({ ...paymentData, amount: e.target.value })}
                    required
                    inputProps={{ min: 0, step: 0.01 }}
                    helperText="Enter the payment amount in GBP"
                  />
                </Grid>

                <Grid item xs={12}>
                  <FormControl fullWidth required>
                    <InputLabel>Payment Method *</InputLabel>
                    <Select
                      value={paymentData.payment_method}
                      label="Payment Method *"
                      onChange={(e) => setPaymentData({ ...paymentData, payment_method: e.target.value })}
                    >
                      <MenuItem value="bank_transfer">Bank Transfer</MenuItem>
                      <MenuItem value="card">Card Payment</MenuItem>
                      <MenuItem value="cash">Cash</MenuItem>
                      <MenuItem value="cheque">Cheque</MenuItem>
                      <MenuItem value="direct_debit">Direct Debit</MenuItem>
                      <MenuItem value="standing_order">Standing Order</MenuItem>
                      <MenuItem value="other">Other</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Payment Reference"
                    value={paymentData.payment_reference}
                    onChange={(e) => setPaymentData({ ...paymentData, payment_reference: e.target.value })}
                    helperText="External payment reference (transaction ID, cheque number, etc.)"
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Description"
                    multiline
                    rows={3}
                    value={paymentData.description}
                    onChange={(e) => setPaymentData({ ...paymentData, description: e.target.value })}
                    helperText="Optional description or notes about this payment"
                  />
                </Grid>

                <Grid item xs={12}>
                  <Box display="flex" gap={2} justifyContent="flex-end">
                    <Button
                      variant="outlined"
                      startIcon={<CancelIcon />}
                      onClick={() => navigate(`/enforcesense/cases/${caseId}`)}
                      disabled={loading}
                    >
                      Cancel
                    </Button>
                    <Button
                      type="submit"
                      variant="contained"
                      startIcon={<SaveIcon />}
                      disabled={loading}
                    >
                      {loading ? <CircularProgress size={20} /> : 'Record Payment'}
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </form>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          {caseData && (
            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Case Information
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Case Reference
                </Typography>
                <Typography variant="body1" fontWeight="bold">
                  {caseData.case_reference}
                </Typography>
                <Divider sx={{ my: 2 }} />
                <Typography variant="body2" color="text.secondary">
                  Debtor
                </Typography>
                <Typography variant="body1">
                  {caseData.debtor?.legal_name || 'N/A'}
                </Typography>
              </CardContent>
            </Card>
          )}

          {balance && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Current Balance
                </Typography>
                <Typography variant="h4" color={balance.current_balance > 0 ? 'error.main' : 'success.main'}>
                  {formatCurrency(balance.current_balance)}
                </Typography>
                <Divider sx={{ my: 2 }} />
                <Box>
                  <Box display="flex" justifyContent="space-between" mb={1}>
                    <Typography variant="body2">Total Debt:</Typography>
                    <Typography variant="body2">{formatCurrency(balance.total_debt)}</Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between" mb={1}>
                    <Typography variant="body2">Fees:</Typography>
                    <Typography variant="body2">{formatCurrency(balance.total_fees)}</Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2">Payments:</Typography>
                    <Typography variant="body2" color="success.main">
                      {formatCurrency(balance.total_payments)}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Container>
  );
};

export default RecordPayment;

