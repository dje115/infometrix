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
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  IconButton,
  Tooltip,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  Skeleton,
  TableSortLabel
} from '@mui/material';
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
  Search as SearchIcon,
  Visibility as ViewIcon,
  Edit as EditIcon,
  ArrowUpward as ArrowUpwardIcon,
  ArrowDownward as ArrowDownwardIcon,
  FileDownload as FileDownloadIcon
} from '@mui/icons-material';
import TablePagination from '@mui/material/TablePagination';
import { useNavigate } from 'react-router-dom';
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
  current_balance: number;
  debtor?: {
    legal_name: string;
    entity_type: string;
  };
  client?: {
    name: string;
  };
  created_at: string;
}

const Cases: React.FC = () => {
  const navigate = useNavigate();
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterCaseType, setFilterCaseType] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [searchQuery, setSearchQuery] = useState('');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [totalCount, setTotalCount] = useState(0);
  const [debtors, setDebtors] = useState<any[]>([]);
  const [clients, setClients] = useState<any[]>([]);
  const [newCase, setNewCase] = useState({
    debtor_id: '',
    client_id: '',
    case_type: 'county_court_judgment',
    status: 'draft',
    original_amount: 0,
    legal_basis: '',
    client_reference: ''
  });

  useEffect(() => {
    loadCases();
    loadDebtors();
    loadClients();
  }, [filterStatus, filterCaseType, sortBy, sortOrder, page, rowsPerPage]);

  // Debounced search - reload cases when search query changes (after delay)
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchQuery !== undefined) {
        setPage(0); // Reset to first page when searching
        loadCases();
      }
    }, 500); // 500ms debounce

    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchQuery]);

  const loadCases = async () => {
    try {
      setLoading(true);
      setError(null);
      const params: any = {
        skip: page * rowsPerPage,
        limit: rowsPerPage
      };
      if (filterStatus !== 'all') {
        params.status = filterStatus;
      }
      if (filterCaseType !== 'all') {
        params.case_type = filterCaseType;
      }
      if (searchQuery) {
        params.search = searchQuery;
      }
      if (sortBy) {
        params.sort_by = sortBy;
        params.sort_order = sortOrder;
      }
      const response = await enforcesenseAPI.listCases(params);
      setCases(response.data || []);
      // Get total count from response headers
      const totalCountHeader = response.headers?.['x-total-count'] || response.headers?.['X-Total-Count'];
      if (totalCountHeader) {
        setTotalCount(parseInt(totalCountHeader, 10));
      } else {
        // Fallback: estimate based on returned data
        if (response.data && response.data.length === rowsPerPage) {
          setTotalCount((page + 1) * rowsPerPage + 1);
        } else {
          setTotalCount(page * rowsPerPage + (response.data?.length || 0));
        }
      }
    } catch (err: any) {
      console.error('Failed to load cases:', err);
      setError(err.response?.data?.detail || 'Failed to load cases');
    } finally {
      setLoading(false);
    }
  };

  const loadDebtors = async () => {
    try {
      const response = await enforcesenseAPI.listDebtors({ limit: 1000 });
      setDebtors(response.data || []);
    } catch (err) {
      console.error('Failed to load debtors:', err);
    }
  };

  const loadClients = async () => {
    try {
      const response = await enforcesenseAPI.listClients({ limit: 1000 });
      setClients(response.data || []);
    } catch (err) {
      console.error('Failed to load clients:', err);
    }
  };

  const handleExport = () => {
    // Export cases to CSV
    const headers = ['Case Reference', 'Client Reference', 'Debtor', 'Client', 'Type', 'Status', 'Original Amount', 'Current Balance', 'Created'];
    const rows = cases.map(caseItem => [
      caseItem.case_reference,
      caseItem.client_reference || '',
      caseItem.debtor?.legal_name || 'N/A',
      caseItem.client?.name || 'N/A',
      caseItem.case_type.replace('_', ' '),
      caseItem.status,
      caseItem.original_amount.toFixed(2),
      caseItem.current_balance.toFixed(2),
      new Date(caseItem.created_at).toLocaleDateString('en-GB')
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `cases_export_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleCreateCase = async () => {
    // Validation
    if (!newCase.debtor_id) {
      setError('Please select a debtor');
      return;
    }
    if (!newCase.client_id) {
      setError('Please select a client');
      return;
    }
    if (!newCase.case_type) {
      setError('Please select a case type');
      return;
    }
    if (newCase.original_amount <= 0) {
      setError('Original amount must be greater than 0');
      return;
    }

    try {
      setError(null);
      await enforcesenseAPI.createCase(newCase);
      setCreateDialogOpen(false);
      setNewCase({
        debtor_id: '',
        client_id: '',
        case_type: 'county_court_judgment',
        status: 'draft',
        original_amount: 0,
        legal_basis: '',
        client_reference: ''
      });
      loadCases();
      // Show success message (you could use a snackbar here)
    } catch (err: any) {
      console.error('Failed to create case:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to create case';
      setError(errorMessage);
    }
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

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: 'GBP'
    }).format(amount);
  };

  const formatCaseType = (type: string) => {
    return type.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
  };

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      <Box mb={3} display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h4" component="h1">
          Enforcement Cases
        </Typography>
        <Box>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
            sx={{ mr: 1 }}
          >
            New Case
          </Button>
          <IconButton onClick={loadCases}>
            <RefreshIcon />
          </IconButton>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              placeholder="Search by case reference, client reference, or debtor name..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  setPage(0);
                  loadCases();
                }
              }}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
              }}
              helperText="Search by case reference, client reference, debtor name, or client name"
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={filterStatus}
                label="Status"
                onChange={(e) => {
                  setFilterStatus(e.target.value);
                  setPage(0); // Reset to first page when filtering
                }}
              >
                <MenuItem value="all">All Statuses</MenuItem>
                <MenuItem value="draft">Draft</MenuItem>
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="on_hold">On Hold</MenuItem>
                <MenuItem value="settled">Settled</MenuItem>
                <MenuItem value="closed">Closed</MenuItem>
                <MenuItem value="cancelled">Cancelled</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <Button 
              variant="outlined" 
              fullWidth 
              onClick={() => {
                setPage(0);
                loadCases();
              }}
              startIcon={<SearchIcon />}
            >
              Search
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Cases Table */}
      {loading ? (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell><Skeleton variant="text" width={150} /></TableCell>
                <TableCell><Skeleton variant="text" width={120} /></TableCell>
                <TableCell><Skeleton variant="text" width={100} /></TableCell>
                <TableCell><Skeleton variant="text" width={80} /></TableCell>
                <TableCell><Skeleton variant="text" width={100} /></TableCell>
                <TableCell align="right"><Skeleton variant="text" width={100} /></TableCell>
                <TableCell align="right"><Skeleton variant="text" width={100} /></TableCell>
                <TableCell><Skeleton variant="text" width={80} /></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {[...Array(5)].map((_, idx) => (
                <TableRow key={idx}>
                  <TableCell><Skeleton variant="text" /></TableCell>
                  <TableCell><Skeleton variant="text" /></TableCell>
                  <TableCell><Skeleton variant="text" /></TableCell>
                  <TableCell><Skeleton variant="text" width={60} /></TableCell>
                  <TableCell><Skeleton variant="rectangular" width={80} height={24} /></TableCell>
                  <TableCell align="right"><Skeleton variant="text" width={80} /></TableCell>
                  <TableCell align="right"><Skeleton variant="text" width={80} /></TableCell>
                  <TableCell><Skeleton variant="circular" width={32} height={32} /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Case Reference</TableCell>
                <TableCell>Debtor</TableCell>
                <TableCell>Client</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Original Amount</TableCell>
                <TableCell align="right">Current Balance</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {cases.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    <Typography color="text.secondary" sx={{ py: 4 }}>
                      No cases found
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                cases.map((caseItem) => (
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
                      {caseItem.debtor?.legal_name || 'Unknown'}
                    </TableCell>
                    <TableCell>
                      {caseItem.client?.name || 'Unknown'}
                    </TableCell>
                    <TableCell>{formatCaseType(caseItem.case_type)}</TableCell>
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
                    <TableCell>
                      <Tooltip title="View Details">
                        <IconButton
                          size="small"
                          onClick={() => navigate(`/enforcesense/cases/${caseItem.id}`)}
                        >
                          <ViewIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
          <TablePagination
            component="div"
            count={totalCount}
            page={page}
            onPageChange={(_, newPage) => setPage(newPage)}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={(e) => {
              setRowsPerPage(parseInt(e.target.value, 10));
              setPage(0);
            }}
            rowsPerPageOptions={[10, 25, 50, 100]}
          />
        </TableContainer>
      )}

      {/* Create Case Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Case</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Debtor *</InputLabel>
              <Select
                value={newCase.debtor_id}
                label="Debtor *"
                onChange={(e) => setNewCase({ ...newCase, debtor_id: e.target.value })}
              >
                {debtors.map((debtor) => (
                  <MenuItem key={debtor.id} value={debtor.id}>
                    {debtor.legal_name} ({debtor.entity_type})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Client *</InputLabel>
              <Select
                value={newCase.client_id}
                label="Client *"
                onChange={(e) => setNewCase({ ...newCase, client_id: e.target.value })}
              >
                {clients.map((client) => (
                  <MenuItem key={client.id} value={client.id}>
                    {client.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Case Type *</InputLabel>
              <Select
                value={newCase.case_type}
                label="Case Type *"
                onChange={(e) => setNewCase({ ...newCase, case_type: e.target.value })}
              >
                <MenuItem value="county_court_judgment">County Court Judgment</MenuItem>
                <MenuItem value="high_court_writ">High Court Writ</MenuItem>
                <MenuItem value="magistrates_court">Magistrates Court</MenuItem>
                <MenuItem value="council_tax">Council Tax</MenuItem>
                <MenuItem value="business_rates">Business Rates</MenuItem>
                <MenuItem value="parking_fine">Parking Fine</MenuItem>
                <MenuItem value="other">Other</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Client Reference"
              value={newCase.client_reference}
              onChange={(e) => setNewCase({ ...newCase, client_reference: e.target.value })}
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Original Amount *"
              type="number"
              value={newCase.original_amount}
              onChange={(e) => setNewCase({ ...newCase, original_amount: parseFloat(e.target.value) || 0 })}
              inputProps={{ min: 0.01, step: 0.01 }}
              required
              error={newCase.original_amount <= 0}
              helperText={newCase.original_amount <= 0 ? 'Amount must be greater than 0' : 'Enter the original debt amount'}
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Legal Basis"
              multiline
              rows={3}
              value={newCase.legal_basis}
              onChange={(e) => setNewCase({ ...newCase, legal_basis: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleCreateCase}
            disabled={!newCase.debtor_id || !newCase.client_id || newCase.original_amount <= 0}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Cases;



