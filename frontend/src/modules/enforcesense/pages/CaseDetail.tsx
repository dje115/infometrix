import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Chip,
  Button,
  TextField,
  Alert,
  CircularProgress,
  Divider,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tooltip,
  Badge
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Edit as EditIcon,
  Add as AddIcon,
  AutoFixHigh as AutoFixHighIcon,
  CheckCircle as CheckCircleIcon,
  AccountBalance as AccountBalanceIcon,
  Payment as PaymentIcon,
  Receipt as ReceiptIcon,
  Notes as NotesIcon,
  Info as InfoIcon,
  Schedule as ScheduleIcon
} from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';
import { enforcesenseAPI } from '../../../services/enforcesenseAPI';

interface Case {
  id: string;
  case_reference: string;
  client_reference?: string;
  debtor_id: string;
  client_id: string;
  case_type: string;
  status: string;
  original_amount: number;
  fees_charged: number;
  payments_received: number;
  current_balance: number;
  legal_basis?: string;
  court_reference?: string;
  notes?: string;
  communications: any[];
  visits: any[];
  actions: any[];
  notices: any[];
  debtor?: {
    id: string;
    legal_name: string;
    entity_type: string;
    email?: string;
    phone?: string;
  };
  client?: {
    id: string;
    name: string;
  };
  created_at: string;
  opened_date: string;
}

interface CaseNote {
  id: string;
  note: string;
  original_note?: string;
  ai_improved_note?: string;
  ai_summary?: string;
  risk_flags?: string[];
  created_at: string;
  created_by?: string;
  ai_processing_status?: 'pending' | 'processing' | 'completed' | 'failed';
}

interface LedgerEntry {
  id: string;
  case_id: string;
  entry_type: string;
  amount: number;
  currency: string;
  description?: string;
  reference?: string;
  status: string;
  posted_at?: string;
  metadata: any;
  created_at: string;
  created_by?: string;
}

interface CaseBalance {
  total_debt: number;
  total_fees: number;
  total_payments: number;
  total_interest: number;
  total_refunds: number;
  total_adjustments: number;
  current_balance: number;
}

interface Payment {
  id: string;
  amount: number;
  payment_method: string;
  payment_reference?: string;
  description?: string;
  created_at: string;
  status: string;
}

const CaseDetail: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [caseData, setCaseData] = useState<Case | null>(null);
  const [notes, setNotes] = useState<CaseNote[]>([]);
  const [ledgerEntries, setLedgerEntries] = useState<LedgerEntry[]>([]);
  const [balance, setBalance] = useState<CaseBalance | null>(null);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [newNote, setNewNote] = useState('');
  const [noteDialogOpen, setNoteDialogOpen] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [triggerAI, setTriggerAI] = useState(true);
  const [statusDialogOpen, setStatusDialogOpen] = useState(false);
  const [newStatus, setNewStatus] = useState('');
  const [arrangements, setArrangements] = useState<any[]>([]);
  const [loadingArrangements, setLoadingArrangements] = useState(false);

  useEffect(() => {
    if (id) {
      loadCase();
      loadNotes();
      loadLedger();
      loadBalance();
      loadPayments();
      if (tabValue === 4) {
        loadArrangements();
      }
    }
  }, [id, tabValue]);

  const loadArrangements = async () => {
    try {
      setLoadingArrangements(true);
      const response = await enforcesenseAPI.getCaseArrangements(id!);
      setArrangements(response.data || []);
    } catch (err) {
      console.error('Failed to load arrangements:', err);
    } finally {
      setLoadingArrangements(false);
    }
  };

  const loadCase = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await enforcesenseAPI.getCase(id!);
      setCaseData(response.data);
      setNewStatus(response.data.status);
    } catch (err: any) {
      console.error('Failed to load case:', err);
      setError(err.response?.data?.detail || 'Failed to load case');
    } finally {
      setLoading(false);
    }
  };

  const loadNotes = async () => {
    try {
      const response = await enforcesenseAPI.getCaseNotes(id!);
      setNotes(response.data || []);
    } catch (err) {
      console.error('Failed to load notes:', err);
    }
  };

  const loadLedger = async () => {
    try {
      const response = await enforcesenseAPI.getCaseLedger(id!, { limit: 100 });
      setLedgerEntries(response.data || []);
    } catch (err) {
      console.error('Failed to load ledger:', err);
    }
  };

  const loadBalance = async () => {
    try {
      const response = await enforcesenseAPI.getCaseBalance(id!);
      setBalance(response.data);
    } catch (err) {
      console.error('Failed to load balance:', err);
    }
  };

  const loadPayments = async () => {
    try {
      const response = await enforcesenseAPI.getCasePayments(id!, { limit: 100 });
      setPayments(response.data || []);
    } catch (err) {
      console.error('Failed to load payments:', err);
    }
  };

  const handleAddNote = async () => {
    if (!newNote.trim()) return;

    try {
      await enforcesenseAPI.addCaseNote(id!, newNote, triggerAI);
      setNewNote('');
      setNoteDialogOpen(false);
      loadNotes();
      loadCase();
    } catch (err: any) {
      console.error('Failed to add note:', err);
      setError(err.response?.data?.detail || 'Failed to add note');
    }
  };

  const handleImproveNote = async (noteId: string) => {
    try {
      await enforcesenseAPI.improveNote(id!, noteId);
      loadNotes();
    } catch (err: any) {
      console.error('Failed to improve note:', err);
      setError(err.response?.data?.detail || 'Failed to improve note');
    }
  };

  const handleStatusUpdate = async () => {
    if (!newStatus || newStatus === caseData?.status) {
      setStatusDialogOpen(false);
      return;
    }

    try {
      setError(null);
      await enforcesenseAPI.updateCase(id!, { status: newStatus });
      setStatusDialogOpen(false);
      loadCase();
    } catch (err: any) {
      console.error('Failed to update status:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to update status';
      setError(errorMessage);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: 'GBP'
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-GB');
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

  const getEntryTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      DEBTOR_PAYMENT: 'Payment',
      CLIENT_PAYOUT: 'Client Payout',
      FEE_EARNED: 'Fee Earned',
      DISBURSEMENT: 'Disbursement',
      REFUND: 'Refund',
      ADJUSTMENT: 'Adjustment',
      INTEREST_ACCRUED: 'Interest',
      FEE_CHARGED: 'Principal Charge'
    };
    return labels[type] || type;
  };

  const getEntryTypeColor = (type: string) => {
    if (type === 'DEBTOR_PAYMENT' || type === 'REFUND') return 'success';
    if (type === 'FEE_EARNED' || type === 'FEE_CHARGED' || type === 'INTEREST_ACCRUED') return 'warning';
    if (type === 'ADJUSTMENT') return 'info';
    return 'default';
  };

  if (loading && !caseData) {
    return (
      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error && !caseData) {
    return (
      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  if (!caseData) {
    return (
      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Alert severity="warning">Case not found</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      <Box mb={3} display="flex" alignItems="center" gap={2}>
        <IconButton onClick={() => navigate('/enforcesense/cases')}>
          <ArrowBackIcon />
        </IconButton>
        <Box flex={1}>
          <Typography variant="h4" component="h1">
            {caseData.case_reference}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {caseData.debtor?.legal_name} • {caseData.client?.name}
          </Typography>
        </Box>
        <Chip
          label={caseData.status.charAt(0).toUpperCase() + caseData.status.slice(1).replace('_', ' ')}
          color={getStatusColor(caseData.status)}
          onClick={() => setStatusDialogOpen(true)}
          sx={{ cursor: 'pointer' }}
        />
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Financial Summary Cards */}
      {balance && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Current Balance
                </Typography>
                <Typography variant="h5" color={balance.current_balance > 0 ? 'error.main' : 'success.main'}>
                  {formatCurrency(balance.current_balance)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Total Debt
                </Typography>
                <Typography variant="h6">{formatCurrency(balance.total_debt)}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Fees Charged
                </Typography>
                <Typography variant="h6">{formatCurrency(balance.total_fees)}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Payments Received
                </Typography>
                <Typography variant="h6" color="success.main">
                  {formatCurrency(balance.total_payments)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={tabValue}
          onChange={(_, newValue) => setTabValue(newValue)}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab icon={<InfoIcon />} iconPosition="start" label="Overview" />
          <Tab
            icon={<AccountBalanceIcon />}
            iconPosition="start"
            label={
              <Badge badgeContent={ledgerEntries.length} color="primary">
                Ledger
              </Badge>
            }
          />
          <Tab
            icon={<PaymentIcon />}
            iconPosition="start"
            label={
              <Badge badgeContent={payments.length} color="primary">
                Payments
              </Badge>
            }
          />
          <Tab
            icon={<NotesIcon />}
            iconPosition="start"
            label={
              <Badge badgeContent={notes.length} color="primary">
                Notes
              </Badge>
            }
          />
          <Tab icon={<ScheduleIcon />} iconPosition="start" label="Arrangements" />
        </Tabs>
      </Paper>

      {/* Tab Content */}
      {tabValue === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3, mb: 3 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">Case Information</Typography>
                <Button startIcon={<EditIcon />} variant="outlined" size="small">
                  Edit
                </Button>
              </Box>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Case Type
                  </Typography>
                  <Typography variant="body1">
                    {caseData.case_type.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Client Reference
                  </Typography>
                  <Typography variant="body1">{caseData.client_reference || 'N/A'}</Typography>
                </Grid>
                {caseData.court_reference && (
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Court Reference
                    </Typography>
                    <Typography variant="body1">{caseData.court_reference}</Typography>
                  </Grid>
                )}
                {caseData.legal_basis && (
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">
                      Legal Basis
                    </Typography>
                    <Typography variant="body1">{caseData.legal_basis}</Typography>
                  </Grid>
                )}
              </Grid>
            </Paper>
          </Grid>

          <Grid item xs={12} md={4}>
            {caseData.debtor && (
              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Debtor Information
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {caseData.debtor.legal_name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {caseData.debtor.entity_type}
                  </Typography>
                  {caseData.debtor.email && (
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      Email: {caseData.debtor.email}
                    </Typography>
                  )}
                  {caseData.debtor.phone && (
                    <Typography variant="body2">
                      Phone: {caseData.debtor.phone}
                    </Typography>
                  )}
                  <Button
                    size="small"
                    sx={{ mt: 2 }}
                    onClick={() => navigate(`/enforcesense/debtors/${caseData.debtor?.id}`)}
                  >
                    View Debtor Details
                  </Button>
                </CardContent>
              </Card>
            )}

            {caseData.client && (
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Client Information
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {caseData.client.name}
                  </Typography>
                  <Button
                    size="small"
                    sx={{ mt: 2 }}
                    onClick={() => navigate(`/enforcesense/clients/${caseData.client?.id}`)}
                  >
                    View Client Details
                  </Button>
                </CardContent>
              </Card>
            )}
          </Grid>
        </Grid>
      )}

      {tabValue === 1 && (
        <Paper sx={{ p: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">Transaction Ledger</Typography>
            <Typography variant="body2" color="text.secondary">
              All financial movements for this case
            </Typography>
          </Box>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell>Reference</TableCell>
                  <TableCell align="right">Amount</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {ledgerEntries.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <Typography color="text.secondary" sx={{ py: 4 }}>
                        No ledger entries yet
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  ledgerEntries.map((entry) => (
                    <TableRow key={entry.id} hover>
                      <TableCell>{formatDate(entry.created_at)}</TableCell>
                      <TableCell>
                        <Chip
                          label={getEntryTypeLabel(entry.entry_type)}
                          color={getEntryTypeColor(entry.entry_type) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{entry.description || 'N/A'}</TableCell>
                      <TableCell>{entry.reference || 'N/A'}</TableCell>
                      <TableCell align="right">
                        <Typography
                          variant="body2"
                          fontWeight="bold"
                          color={
                            entry.entry_type === 'DEBTOR_PAYMENT' || entry.entry_type === 'REFUND'
                              ? 'success.main'
                              : 'text.primary'
                          }
                        >
                          {formatCurrency(entry.amount)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={entry.status}
                          size="small"
                          color={entry.status === 'CLEARED' ? 'success' : 'default'}
                        />
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}

      {tabValue === 2 && (
        <Paper sx={{ p: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">Payment History</Typography>
            <Button
              variant="contained"
              startIcon={<PaymentIcon />}
              onClick={() => navigate(`/enforcesense/cases/${id}/payments/new`)}
            >
              Record Payment
            </Button>
          </Box>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>Payment Method</TableCell>
                  <TableCell>Reference</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell align="right">Amount</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {payments.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      <Typography color="text.secondary" sx={{ py: 4 }}>
                        No payments recorded yet
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  payments.map((payment) => (
                    <TableRow key={payment.id} hover>
                      <TableCell>{formatDate(payment.created_at)}</TableCell>
                      <TableCell>{payment.payment_method}</TableCell>
                      <TableCell>{payment.payment_reference || 'N/A'}</TableCell>
                      <TableCell>{payment.description || 'N/A'}</TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" fontWeight="bold" color="success.main">
                          {formatCurrency(payment.amount)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={payment.status}
                          size="small"
                          color={payment.status === 'CLEARED' ? 'success' : 'default'}
                        />
                      </TableCell>
                      <TableCell>
                        <Button
                          size="small"
                          onClick={() => navigate(`/enforcesense/payments/${payment.id}/allocate`)}
                        >
                          Allocate
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}

      {tabValue === 3 && (
        <Paper sx={{ p: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">Notes & Communications</Typography>
            <Button
              startIcon={<AddIcon />}
              variant="contained"
              size="small"
              onClick={() => setNoteDialogOpen(true)}
            >
              Add Note
            </Button>
          </Box>

          <List>
            {notes.length === 0 ? (
              <ListItem>
                <ListItemText primary="No notes yet" secondary="Add a note to get started" />
              </ListItem>
            ) : (
              notes.map((note) => (
                <React.Fragment key={note.id}>
                  <ListItem
                    sx={{
                      flexDirection: 'column',
                      alignItems: 'flex-start',
                      bgcolor: note.ai_improved_note ? 'action.hover' : 'transparent',
                      borderRadius: 1,
                      mb: 1
                    }}
                  >
                    <Box width="100%" display="flex" justifyContent="space-between" alignItems="start" mb={1}>
                      <Box flex={1}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          {formatDate(note.created_at)}
                        </Typography>
                        {note.original_note && (
                          <Box mb={1}>
                            <Typography variant="caption" color="text.secondary">
                              Original Note:
                            </Typography>
                            <Typography variant="body2" sx={{ fontStyle: 'italic', color: 'text.secondary' }}>
                              {note.original_note}
                            </Typography>
                          </Box>
                        )}
                        <Typography variant="body1" sx={{ mt: 1 }}>
                          {note.ai_improved_note || note.note}
                        </Typography>
                        {note.ai_summary && (
                          <Box mt={1} p={1} bgcolor="primary.light" borderRadius={1}>
                            <Typography variant="caption" fontWeight="bold">
                              AI Summary:
                            </Typography>
                            <Typography variant="body2">{note.ai_summary}</Typography>
                          </Box>
                        )}
                        {note.risk_flags && note.risk_flags.length > 0 && (
                          <Box mt={1} display="flex" gap={1} flexWrap="wrap">
                            {note.risk_flags.map((flag, idx) => (
                              <Chip key={idx} label={flag} color="warning" size="small" />
                            ))}
                          </Box>
                        )}
                      </Box>
                      {!note.ai_improved_note && note.ai_processing_status !== 'processing' && (
                        <IconButton
                          size="small"
                          onClick={() => handleImproveNote(note.id)}
                          title="Improve with AI"
                        >
                          <AutoFixHighIcon />
                        </IconButton>
                      )}
                      {note.ai_processing_status === 'completed' && (
                        <CheckCircleIcon color="success" sx={{ ml: 1 }} />
                      )}
                    </Box>
                  </ListItem>
                  <Divider />
                </React.Fragment>
              ))
            )}
          </List>
        </Paper>
      )}

      {tabValue === 4 && (
        <Paper sx={{ p: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">Payment Arrangements</Typography>
            <Button
              variant="contained"
              startIcon={<ScheduleIcon />}
              onClick={() => navigate(`/enforcesense/cases/${id}/arrangements/new`)}
            >
              Create Arrangement
            </Button>
          </Box>
          <Alert severity="info" sx={{ mb: 2 }}>
            Arrangements allow debtors to pay in installments over time.
          </Alert>
          {loadingArrangements ? (
            <Box display="flex" justifyContent="center" p={4}>
              <CircularProgress />
            </Box>
          ) : arrangements.length === 0 ? (
            <Typography color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>
              No arrangements yet. Create one to get started.
            </Typography>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Total Amount</TableCell>
                    <TableCell>Start Date</TableCell>
                    <TableCell>Payments</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {arrangements.map((arrangement) => (
                    <TableRow key={arrangement.id}>
                      <TableCell>{formatCurrency(arrangement.total_amount)}</TableCell>
                      <TableCell>{new Date(arrangement.start_date).toLocaleDateString('en-GB')}</TableCell>
                      <TableCell>{arrangement.schedule?.length || 0}</TableCell>
                      <TableCell>
                        <Chip
                          label={arrangement.status}
                          size="small"
                          color={
                            arrangement.status === 'ACTIVE' ? 'success' :
                            arrangement.status === 'COMPLETED' ? 'info' :
                            arrangement.status === 'BROKEN' ? 'error' : 'default'
                          }
                        />
                      </TableCell>
                      <TableCell>
                        <Button
                          size="small"
                          onClick={() => navigate(`/enforcesense/arrangements/${arrangement.id}`)}
                        >
                          View
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Paper>
      )}

      {/* Add Note Dialog */}
      <Dialog open={noteDialogOpen} onClose={() => setNoteDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add Case Note</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={6}
            label="Note"
            value={newNote}
            onChange={(e) => setNewNote(e.target.value)}
            placeholder="Enter your note here..."
            sx={{ mt: 2 }}
          />
          <Box sx={{ mt: 2 }}>
            <Button
              variant={triggerAI ? 'contained' : 'outlined'}
              onClick={() => setTriggerAI(!triggerAI)}
              startIcon={<AutoFixHighIcon />}
            >
              {triggerAI ? 'AI Improvement Enabled' : 'Enable AI Improvement'}
            </Button>
            <Typography variant="caption" color="text.secondary" sx={{ ml: 2, display: 'inline-block' }}>
              AI will clean and improve your note while keeping the original
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNoteDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleAddNote} disabled={!newNote.trim()}>
            Add Note
          </Button>
        </DialogActions>
      </Dialog>

      {/* Status Update Dialog */}
      <Dialog open={statusDialogOpen} onClose={() => setStatusDialogOpen(false)}>
        <DialogTitle>Update Case Status</DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          )}
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Status</InputLabel>
            <Select value={newStatus} label="Status" onChange={(e) => setNewStatus(e.target.value)}>
              <MenuItem value="draft">Draft</MenuItem>
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="on_hold">On Hold</MenuItem>
              <MenuItem value="settled">Settled</MenuItem>
              <MenuItem value="closed">Closed</MenuItem>
              <MenuItem value="cancelled">Cancelled</MenuItem>
            </Select>
          </FormControl>
          {newStatus && newStatus !== caseData?.status && (
            <Alert severity="info" sx={{ mt: 2 }}>
              Changing status from <strong>{caseData?.status?.charAt(0).toUpperCase() + caseData?.status?.slice(1).replace('_', ' ')}</strong> to <strong>{newStatus.charAt(0).toUpperCase() + newStatus.slice(1).replace('_', ' ')}</strong>
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setStatusDialogOpen(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            onClick={handleStatusUpdate}
            disabled={!newStatus || newStatus === caseData?.status}
          >
            Update Status
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default CaseDetail;
