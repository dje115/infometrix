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
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
  CalendarToday as CalendarIcon
} from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';
import { enforcesenseAPI } from '../../../services/enforcesenseAPI';

interface ScheduleItem {
  due_date: string;
  amount: string;
  order: number;
}

const CreateArrangement: React.FC = () => {
  const navigate = useNavigate();
  const { caseId } = useParams<{ caseId: string }>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [caseData, setCaseData] = useState<any>(null);
  const [balance, setBalance] = useState<any>(null);
  
  const [arrangementData, setArrangementData] = useState({
    total_amount: '',
    start_date: new Date().toISOString().split('T')[0],
    description: ''
  });
  
  const [scheduleItems, setScheduleItems] = useState<ScheduleItem[]>([]);
  const [addItemDialogOpen, setAddItemDialogOpen] = useState(false);
  const [newItem, setNewItem] = useState<ScheduleItem>({
    due_date: '',
    amount: '',
    order: 1
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

  const handleAddScheduleItem = () => {
    if (!newItem.due_date || !newItem.amount || parseFloat(newItem.amount) <= 0) {
      setError('Please enter a valid due date and amount');
      return;
    }

    const order = scheduleItems.length > 0 
      ? Math.max(...scheduleItems.map(item => item.order)) + 1 
      : 1;

    setScheduleItems([
      ...scheduleItems,
      { ...newItem, order }
    ].sort((a, b) => {
      // Sort by due date
      return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
    }).map((item, index) => ({ ...item, order: index + 1 })));
    
    setNewItem({
      due_date: '',
      amount: '',
      order: 1
    });
    setAddItemDialogOpen(false);
  };

  const handleRemoveItem = (index: number) => {
    const newItems = scheduleItems.filter((_, i) => i !== index);
    setScheduleItems(newItems.map((item, idx) => ({ ...item, order: idx + 1 })));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!arrangementData.total_amount || parseFloat(arrangementData.total_amount) <= 0) {
      setError('Please enter a valid total amount');
      return;
    }

    if (scheduleItems.length === 0) {
      setError('Please add at least one payment schedule item');
      return;
    }

    const totalScheduleAmount = scheduleItems.reduce(
      (sum, item) => sum + parseFloat(item.amount || '0'),
      0
    );

    if (Math.abs(totalScheduleAmount - parseFloat(arrangementData.total_amount)) > 0.01) {
      setError(`Schedule total (${totalScheduleAmount.toFixed(2)}) must equal arrangement total (${arrangementData.total_amount})`);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      await enforcesenseAPI.createArrangement(caseId!, {
        total_amount: parseFloat(arrangementData.total_amount),
        schedule: scheduleItems.map(item => ({
          due_date: item.due_date,
          amount: parseFloat(item.amount),
          order: item.order
        })),
        start_date: arrangementData.start_date,
        description: arrangementData.description || undefined
      });
      
      navigate(`/enforcesense/cases/${caseId}`);
    } catch (err: any) {
      console.error('Failed to create arrangement:', err);
      setError(err.response?.data?.detail || 'Failed to create arrangement');
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

  const getTotalScheduleAmount = () => {
    return scheduleItems.reduce(
      (sum, item) => sum + parseFloat(item.amount || '0'),
      0
    );
  };

  const getRemaining = () => {
    return parseFloat(arrangementData.total_amount || '0') - getTotalScheduleAmount();
  };

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      <Box mb={3} display="flex" alignItems="center" gap={2}>
        <IconButton onClick={() => navigate(`/enforcesense/cases/${caseId}`)}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h4" component="h1">
          Create Payment Arrangement
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <form onSubmit={handleSubmit}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Arrangement Details
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Total Amount *"
                    type="number"
                    value={arrangementData.total_amount}
                    onChange={(e) => setArrangementData({ ...arrangementData, total_amount: e.target.value })}
                    required
                    inputProps={{ min: 0, step: 0.01 }}
                    helperText="Total amount to be paid over the arrangement period"
                  />
                </Grid>

                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Start Date *"
                    type="date"
                    value={arrangementData.start_date}
                    onChange={(e) => setArrangementData({ ...arrangementData, start_date: e.target.value })}
                    required
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Description"
                    multiline
                    rows={3}
                    value={arrangementData.description}
                    onChange={(e) => setArrangementData({ ...arrangementData, description: e.target.value })}
                    helperText="Optional description or notes about this arrangement"
                  />
                </Grid>
              </Grid>
            </Paper>

            <Paper sx={{ p: 3 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">Payment Schedule</Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setAddItemDialogOpen(true)}
                >
                  Add Payment
                </Button>
              </Box>

              {scheduleItems.length === 0 ? (
                <Alert severity="info">
                  No payment schedule items. Add items to create the payment plan.
                </Alert>
              ) : (
                <>
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Due Date</TableCell>
                          <TableCell align="right">Amount</TableCell>
                          <TableCell>Order</TableCell>
                          <TableCell>Actions</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {scheduleItems.map((item, index) => (
                          <TableRow key={index}>
                            <TableCell>
                              {new Date(item.due_date).toLocaleDateString('en-GB')}
                            </TableCell>
                            <TableCell align="right">
                              {formatCurrency(parseFloat(item.amount || '0'))}
                            </TableCell>
                            <TableCell>{item.order}</TableCell>
                            <TableCell>
                              <IconButton
                                size="small"
                                color="error"
                                onClick={() => handleRemoveItem(index)}
                              >
                                <DeleteIcon />
                              </IconButton>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>

                  <Box mt={3} p={2} bgcolor="grey.100" borderRadius={1}>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body1" fontWeight="bold">
                        Schedule Total:
                      </Typography>
                      <Typography variant="body1" fontWeight="bold">
                        {formatCurrency(getTotalScheduleAmount())}
                      </Typography>
                    </Box>
                    <Box display="flex" justifyContent="space-between">
                      <Typography variant="body2" color="text.secondary">
                        Remaining:
                      </Typography>
                      <Typography
                        variant="body2"
                        color={getRemaining() === 0 ? 'success.main' : 'error.main'}
                        fontWeight="bold"
                      >
                        {formatCurrency(getRemaining())}
                      </Typography>
                    </Box>
                  </Box>
                </>
              )}
            </Paper>

            <Box mt={3} display="flex" gap={2} justifyContent="flex-end">
              <Button
                variant="outlined"
                onClick={() => navigate(`/enforcesense/cases/${caseId}`)}
                disabled={loading}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="contained"
                startIcon={<SaveIcon />}
                disabled={loading || scheduleItems.length === 0 || getRemaining() !== 0}
              >
                {loading ? <CircularProgress size={20} /> : 'Create Arrangement'}
              </Button>
            </Box>
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
      </form>

      {/* Add Schedule Item Dialog */}
      <Dialog open={addItemDialogOpen} onClose={() => setAddItemDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Payment Schedule Item</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              label="Due Date *"
              type="date"
              value={newItem.due_date}
              onChange={(e) => setNewItem({ ...newItem, due_date: e.target.value })}
              required
              InputLabelProps={{ shrink: true }}
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Amount *"
              type="number"
              value={newItem.amount}
              onChange={(e) => setNewItem({ ...newItem, amount: e.target.value })}
              required
              inputProps={{ min: 0, step: 0.01 }}
              helperText={`Remaining: ${formatCurrency(getRemaining() - parseFloat(newItem.amount || '0'))}`}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddItemDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleAddScheduleItem}>
            Add Payment
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default CreateArrangement;

