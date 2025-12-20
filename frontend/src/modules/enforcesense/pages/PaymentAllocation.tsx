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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Save as SaveIcon
} from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';
import { enforcesenseAPI } from '../../../services/enforcesenseAPI';

interface AllocationLine {
  target_type: string;
  target_id?: string;
  amount: string;
  order: number;
}

const PaymentAllocation: React.FC = () => {
  const navigate = useNavigate();
  const { paymentEntryId } = useParams<{ paymentEntryId: string }>();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [paymentEntry, setPaymentEntry] = useState<any>(null);
  const [existingAllocation, setExistingAllocation] = useState<any>(null);
  const [allocationLines, setAllocationLines] = useState<AllocationLine[]>([]);
  const [addLineDialogOpen, setAddLineDialogOpen] = useState(false);
  const [newLine, setNewLine] = useState<AllocationLine>({
    target_type: 'PRINCIPAL',
    amount: '',
    order: 1
  });

  useEffect(() => {
    if (paymentEntryId) {
      loadPaymentData();
    }
  }, [paymentEntryId]);

  const loadPaymentData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get payment entry from ledger
      const ledgerResponse = await enforcesenseAPI.getCaseLedger(
        paymentEntryId.split('-')[0], // Extract case ID if needed
        { entry_types: ['DEBTOR_PAYMENT'] }
      );
      
      const payment = ledgerResponse.data.find((e: any) => e.id === paymentEntryId);
      if (payment) {
        setPaymentEntry(payment);
      }
      
      // Check for existing allocation
      try {
        const allocationResponse = await enforcesenseAPI.getPaymentAllocation(paymentEntryId);
        if (allocationResponse.data) {
          setExistingAllocation(allocationResponse.data);
          setAllocationLines(allocationResponse.data.allocation_lines || []);
        } else {
          // Initialize with default allocation to principal
          setAllocationLines([{
            target_type: 'PRINCIPAL',
            amount: payment?.amount?.toString() || '',
            order: 1
          }]);
        }
      } catch (err) {
        // No existing allocation, initialize default
        if (payment) {
          setAllocationLines([{
            target_type: 'PRINCIPAL',
            amount: payment.amount.toString(),
            order: 1
          }]);
        }
      }
    } catch (err: any) {
      console.error('Failed to load payment data:', err);
      setError(err.response?.data?.detail || 'Failed to load payment data');
    } finally {
      setLoading(false);
    }
  };

  const handleAddLine = () => {
    if (!newLine.amount || parseFloat(newLine.amount) <= 0) {
      setError('Please enter a valid amount');
      return;
    }

    const order = allocationLines.length > 0 
      ? Math.max(...allocationLines.map(l => l.order)) + 1 
      : 1;

    setAllocationLines([
      ...allocationLines,
      { ...newLine, order }
    ]);
    
    setNewLine({
      target_type: 'PRINCIPAL',
      amount: '',
      order: 1
    });
    setAddLineDialogOpen(false);
  };

  const handleRemoveLine = (index: number) => {
    setAllocationLines(allocationLines.filter((_, i) => i !== index));
  };

  const handleSave = async () => {
    if (allocationLines.length === 0) {
      setError('Please add at least one allocation line');
      return;
    }

    const totalAllocated = allocationLines.reduce(
      (sum, line) => sum + parseFloat(line.amount || '0'),
      0
    );

    if (Math.abs(totalAllocated - (paymentEntry?.amount || 0)) > 0.01) {
      setError(`Total allocated (${totalAllocated.toFixed(2)}) must equal payment amount (${paymentEntry?.amount || 0})`);
      return;
    }

    try {
      setSaving(true);
      setError(null);

      const allocationData = {
        allocation_lines: allocationLines.map(line => ({
          target_type: line.target_type,
          target_id: line.target_id || null,
          amount: parseFloat(line.amount),
          order: line.order
        })),
        allocation_method: 'MANUAL'
      };

      await enforcesenseAPI.allocatePayment(paymentEntryId!, allocationData);
      
      navigate(`/enforcesense/cases/${paymentEntry?.case_id}`);
    } catch (err: any) {
      console.error('Failed to allocate payment:', err);
      setError(err.response?.data?.detail || 'Failed to allocate payment');
    } finally {
      setSaving(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: 'GBP'
    }).format(amount);
  };

  const getTotalAllocated = () => {
    return allocationLines.reduce(
      (sum, line) => sum + parseFloat(line.amount || '0'),
      0
    );
  };

  const getRemaining = () => {
    return (paymentEntry?.amount || 0) - getTotalAllocated();
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (existingAllocation) {
    return (
      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Box mb={3} display="flex" alignItems="center" gap={2}>
          <IconButton onClick={() => navigate(`/enforcesense/cases/${paymentEntry?.case_id}`)}>
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h4" component="h1">
            Payment Allocation
          </Typography>
        </Box>

        <Alert severity="info" sx={{ mb: 2 }}>
          This payment has already been allocated. Viewing existing allocation.
        </Alert>

        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Allocation Details
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Target Type</TableCell>
                  <TableCell>Target ID</TableCell>
                  <TableCell align="right">Amount</TableCell>
                  <TableCell>Order</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {existingAllocation.allocation_lines.map((line: any, index: number) => (
                  <TableRow key={index}>
                    <TableCell>
                      <Chip label={line.target_type} size="small" />
                    </TableCell>
                    <TableCell>{line.target_id || 'N/A'}</TableCell>
                    <TableCell align="right">{formatCurrency(line.amount)}</TableCell>
                    <TableCell>{line.order}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <Box mt={2}>
            <Typography variant="body2" color="text.secondary">
              Total Allocated: {formatCurrency(existingAllocation.total_allocated)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Allocation Method: {existingAllocation.allocation_method}
            </Typography>
          </Box>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      <Box mb={3} display="flex" alignItems="center" gap={2}>
        <IconButton onClick={() => navigate(`/enforcesense/cases/${paymentEntry?.case_id}`)}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h4" component="h1">
          Allocate Payment
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
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Allocation Lines</Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setAddLineDialogOpen(true)}
              >
                Add Line
              </Button>
            </Box>

            {paymentEntry && (
              <Card sx={{ mb: 3, bgcolor: 'primary.light' }}>
                <CardContent>
                  <Typography variant="body2" color="text.secondary">
                    Payment Amount
                  </Typography>
                  <Typography variant="h5">
                    {formatCurrency(paymentEntry.amount)}
                  </Typography>
                </CardContent>
              </Card>
            )}

            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Target Type</TableCell>
                    <TableCell>Target ID</TableCell>
                    <TableCell align="right">Amount</TableCell>
                    <TableCell>Order</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {allocationLines.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} align="center">
                        <Typography color="text.secondary" sx={{ py: 2 }}>
                          No allocation lines. Add a line to get started.
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    allocationLines.map((line, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Chip label={line.target_type} size="small" />
                        </TableCell>
                        <TableCell>{line.target_id || 'N/A'}</TableCell>
                        <TableCell align="right">
                          {formatCurrency(parseFloat(line.amount || '0'))}
                        </TableCell>
                        <TableCell>{line.order}</TableCell>
                        <TableCell>
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleRemoveLine(index)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>

            <Box mt={3} p={2} bgcolor="grey.100" borderRadius={1}>
              <Box display="flex" justifyContent="space-between" mb={1}>
                <Typography variant="body1" fontWeight="bold">
                  Total Allocated:
                </Typography>
                <Typography variant="body1" fontWeight="bold">
                  {formatCurrency(getTotalAllocated())}
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

            <Box mt={3} display="flex" gap={2} justifyContent="flex-end">
              <Button
                variant="outlined"
                onClick={() => navigate(`/enforcesense/cases/${paymentEntry?.case_id}`)}
                disabled={saving}
              >
                Cancel
              </Button>
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={handleSave}
                disabled={saving || getRemaining() !== 0 || allocationLines.length === 0}
              >
                {saving ? <CircularProgress size={20} /> : 'Save Allocation'}
              </Button>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Allocation Help
              </Typography>
              <Typography variant="body2" paragraph>
                Allocate the payment across different targets:
              </Typography>
              <Typography variant="body2" component="div">
                <strong>PRINCIPAL:</strong> Principal debt amount
                <br />
                <strong>INTEREST:</strong> Interest accrued
                <br />
                <strong>ENFORCEMENT_FEE:</strong> Enforcement fees
                <br />
                <strong>CLIENT_FEE:</strong> Client fees
              </Typography>
              <Alert severity="warning" sx={{ mt: 2 }}>
                Total allocated must equal the payment amount exactly.
              </Alert>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Add Line Dialog */}
      <Dialog open={addLineDialogOpen} onClose={() => setAddLineDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Allocation Line</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Target Type *</InputLabel>
              <Select
                value={newLine.target_type}
                label="Target Type *"
                onChange={(e) => setNewLine({ ...newLine, target_type: e.target.value })}
              >
                <MenuItem value="PRINCIPAL">Principal</MenuItem>
                <MenuItem value="INTEREST">Interest</MenuItem>
                <MenuItem value="ENFORCEMENT_FEE">Enforcement Fee</MenuItem>
                <MenuItem value="CLIENT_FEE">Client Fee</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Target ID"
              value={newLine.target_id || ''}
              onChange={(e) => setNewLine({ ...newLine, target_id: e.target.value })}
              sx={{ mb: 2 }}
              helperText="Optional: Specific debt or fee rule ID"
            />

            <TextField
              fullWidth
              label="Amount *"
              type="number"
              value={newLine.amount}
              onChange={(e) => setNewLine({ ...newLine, amount: e.target.value })}
              required
              inputProps={{ min: 0, step: 0.01 }}
              helperText={`Remaining: ${formatCurrency(getRemaining() - parseFloat(newLine.amount || '0'))}`}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddLineDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleAddLine}>
            Add Line
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default PaymentAllocation;

