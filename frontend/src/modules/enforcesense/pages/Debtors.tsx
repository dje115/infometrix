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
  CardContent
} from '@mui/material';
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
  Search as SearchIcon,
  Visibility as ViewIcon,
  Edit as EditIcon,
  Person as PersonIcon,
  Business as BusinessIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { enforcesenseAPI } from '../../../services/enforcesenseAPI';
import TablePagination from '@mui/material/TablePagination';

interface Debtor {
  id: string;
  entity_type: string;
  legal_name: string;
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  is_vulnerable: boolean;
  created_at: string;
}

const Debtors: React.FC = () => {
  const navigate = useNavigate();
  const [debtors, setDebtors] = useState<Debtor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterEntityType, setFilterEntityType] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [totalCount, setTotalCount] = useState(0);
  
  const [newDebtor, setNewDebtor] = useState({
    entity_type: 'PERSON',
    legal_name: '',
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    date_of_birth: '',
    national_identifier: '',
    company_registration_number: '',
    is_vulnerable: false
  });

  useEffect(() => {
    loadDebtors();
  }, [filterEntityType, page, rowsPerPage]);

  const loadDebtors = async () => {
    try {
      setLoading(true);
      setError(null);
      const params: any = {
        skip: page * rowsPerPage,
        limit: rowsPerPage
      };
      if (filterEntityType !== 'all') {
        params.entity_type = filterEntityType;
      }
      if (searchQuery) {
        params.search = searchQuery;
      }
      const response = await enforcesenseAPI.listDebtors(params);
      setDebtors(response.data || []);
      // Estimate total count
      if (response.data && response.data.length === rowsPerPage) {
        setTotalCount((page + 1) * rowsPerPage + 1);
      } else {
        setTotalCount(page * rowsPerPage + (response.data?.length || 0));
      }
    } catch (err: any) {
      console.error('Failed to load debtors:', err);
      setError(err.response?.data?.detail || 'Failed to load debtors');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDebtor = async () => {
    // Validation
    if (!newDebtor.legal_name.trim()) {
      setError('Legal name is required');
      return;
    }

    // Validate email format if provided
    if (newDebtor.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(newDebtor.email)) {
      setError('Please enter a valid email address');
      return;
    }

    try {
      setError(null);
      await enforcesenseAPI.createDebtor(newDebtor);
      setCreateDialogOpen(false);
      setNewDebtor({
        entity_type: 'PERSON',
        legal_name: '',
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        date_of_birth: '',
        national_identifier: '',
        company_registration_number: '',
        is_vulnerable: false
      });
      loadDebtors();
    } catch (err: any) {
      console.error('Failed to create debtor:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to create debtor';
      setError(errorMessage);
    }
  };

  const handleSearch = () => {
    setPage(0);
    loadDebtors();
  };

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      <Box mb={3} display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h4" component="h1">
          Debtors
        </Typography>
        <Box>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
            sx={{ mr: 1 }}
          >
            New Debtor
          </Button>
          <IconButton onClick={loadDebtors}>
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
              placeholder="Search debtors..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleSearch();
                }
              }}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
              }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Entity Type</InputLabel>
              <Select
                value={filterEntityType}
                label="Entity Type"
                onChange={(e) => {
                  setFilterEntityType(e.target.value);
                  setPage(0);
                }}
              >
                <MenuItem value="all">All Types</MenuItem>
                <MenuItem value="PERSON">Person</MenuItem>
                <MenuItem value="COMPANY">Company</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <Button variant="outlined" fullWidth onClick={handleSearch}>
              Search
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Debtors Table */}
      {loading ? (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Phone</TableCell>
                <TableCell>Vulnerable</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {debtors.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <Typography color="text.secondary" sx={{ py: 4 }}>
                      No debtors found
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                debtors.map((debtor) => (
                  <TableRow key={debtor.id} hover>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        {debtor.entity_type === 'PERSON' ? (
                          <PersonIcon color="action" fontSize="small" />
                        ) : (
                          <BusinessIcon color="action" fontSize="small" />
                        )}
                        <Typography variant="body2" fontWeight="bold">
                          {debtor.legal_name}
                        </Typography>
                      </Box>
                      {debtor.first_name && debtor.last_name && (
                        <Typography variant="caption" color="text.secondary">
                          {debtor.first_name} {debtor.last_name}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={debtor.entity_type}
                        size="small"
                        color={debtor.entity_type === 'PERSON' ? 'primary' : 'secondary'}
                      />
                    </TableCell>
                    <TableCell>{debtor.email || 'N/A'}</TableCell>
                    <TableCell>{debtor.phone || 'N/A'}</TableCell>
                    <TableCell>
                      {debtor.is_vulnerable ? (
                        <Chip label="Yes" color="warning" size="small" />
                      ) : (
                        <Chip label="No" size="small" />
                      )}
                    </TableCell>
                    <TableCell>
                      {new Date(debtor.created_at).toLocaleDateString('en-GB')}
                    </TableCell>
                    <TableCell>
                      <Tooltip title="View Details">
                        <IconButton
                          size="small"
                          onClick={() => navigate(`/enforcesense/debtors/${debtor.id}`)}
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

      {/* Create Debtor Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Debtor</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Entity Type *</InputLabel>
              <Select
                value={newDebtor.entity_type}
                label="Entity Type *"
                onChange={(e) => setNewDebtor({ ...newDebtor, entity_type: e.target.value })}
              >
                <MenuItem value="PERSON">Person</MenuItem>
                <MenuItem value="COMPANY">Company</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Legal Name *"
              value={newDebtor.legal_name}
              onChange={(e) => setNewDebtor({ ...newDebtor, legal_name: e.target.value })}
              sx={{ mb: 2 }}
              required
            />

            {newDebtor.entity_type === 'PERSON' ? (
              <>
                <TextField
                  fullWidth
                  label="First Name"
                  value={newDebtor.first_name}
                  onChange={(e) => setNewDebtor({ ...newDebtor, first_name: e.target.value })}
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  label="Last Name"
                  value={newDebtor.last_name}
                  onChange={(e) => setNewDebtor({ ...newDebtor, last_name: e.target.value })}
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  label="Date of Birth"
                  type="date"
                  value={newDebtor.date_of_birth}
                  onChange={(e) => setNewDebtor({ ...newDebtor, date_of_birth: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  label="National Identifier"
                  value={newDebtor.national_identifier}
                  onChange={(e) => setNewDebtor({ ...newDebtor, national_identifier: e.target.value })}
                  sx={{ mb: 2 }}
                  helperText="NI number, passport number, etc."
                />
              </>
            ) : (
              <TextField
                fullWidth
                label="Company Registration Number"
                value={newDebtor.company_registration_number}
                onChange={(e) => setNewDebtor({ ...newDebtor, company_registration_number: e.target.value })}
                sx={{ mb: 2 }}
              />
            )}

            <TextField
              fullWidth
              label="Email"
              type="email"
              value={newDebtor.email}
              onChange={(e) => setNewDebtor({ ...newDebtor, email: e.target.value })}
              error={newDebtor.email !== '' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(newDebtor.email)}
              helperText={newDebtor.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(newDebtor.email) ? 'Invalid email format' : ''}
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Phone"
              value={newDebtor.phone}
              onChange={(e) => setNewDebtor({ ...newDebtor, phone: e.target.value })}
              sx={{ mb: 2 }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleCreateDebtor}
            disabled={!newDebtor.legal_name.trim()}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Debtors;

