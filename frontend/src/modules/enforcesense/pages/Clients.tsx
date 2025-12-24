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
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  IconButton,
  Tooltip,
  CircularProgress,
  Grid
} from '@mui/material';
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
  Search as SearchIcon,
  Visibility as ViewIcon,
  Business as BusinessIcon,
  Link as LinkIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { enforcesenseAPI } from '../../../services/enforcesenseAPI';
import TablePagination from '@mui/material/TablePagination';

interface Client {
  id: string;
  customer_id?: string; // Link to main CRM Customer
  name: string;
  company_name?: string;
  email?: string;
  phone?: string;
  created_at: string;
}

const Clients: React.FC = () => {
  const navigate = useNavigate();
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [totalCount, setTotalCount] = useState(0);
  
  const [newClient, setNewClient] = useState({
    name: '',
    company_name: '',
    email: '',
    phone: '',
    address: '',
    postcode: ''
  });

  useEffect(() => {
    loadClients();
  }, [page, rowsPerPage]);

  const loadClients = async () => {
    try {
      setLoading(true);
      setError(null);
      const params: any = {
        skip: page * rowsPerPage,
        limit: rowsPerPage
      };
      if (searchQuery) {
        params.search = searchQuery;
      }
      const response = await enforcesenseAPI.listClients(params);
      setClients(response.data || []);
      // Estimate total count
      if (response.data && response.data.length === rowsPerPage) {
        setTotalCount((page + 1) * rowsPerPage + 1);
      } else {
        setTotalCount(page * rowsPerPage + (response.data?.length || 0));
      }
    } catch (err: any) {
      console.error('Failed to load clients:', err);
      setError(err.response?.data?.detail || 'Failed to load clients');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateClient = async () => {
    // Validation
    if (!newClient.name.trim()) {
      setError('Name is required');
      return;
    }

    // Validate email format if provided
    if (newClient.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(newClient.email)) {
      setError('Please enter a valid email address');
      return;
    }

    try {
      setError(null);
      await enforcesenseAPI.createClient(newClient);
      setCreateDialogOpen(false);
      setNewClient({
        name: '',
        company_name: '',
        email: '',
        phone: '',
        address: '',
        postcode: ''
      });
      loadClients();
    } catch (err: any) {
      console.error('Failed to create client:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to create client';
      setError(errorMessage);
    }
  };

  const handleSearch = () => {
    setPage(0);
    loadClients();
  };

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      <Box mb={3} display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h4" component="h1">
          Enforcement Clients
        </Typography>
        <Box>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
            sx={{ mr: 1 }}
          >
            New Client
          </Button>
          <IconButton onClick={loadClients}>
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
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder="Search clients..."
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
          <Grid item xs={12} md={2}>
            <Button variant="outlined" fullWidth onClick={handleSearch}>
              Search
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Clients Table */}
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
                <TableCell>Company</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Phone</TableCell>
                <TableCell>CRM Link</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {clients.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <Typography color="text.secondary" sx={{ py: 4 }}>
                      No clients found
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                clients.map((client) => (
                  <TableRow key={client.id} hover>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        <BusinessIcon color="action" fontSize="small" />
                        <Typography variant="body2" fontWeight="bold">
                          {client.name}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{client.company_name || 'N/A'}</TableCell>
                    <TableCell>{client.email || 'N/A'}</TableCell>
                    <TableCell>{client.phone || 'N/A'}</TableCell>
                    <TableCell>
                      {client.customer_id ? (
                        <Tooltip title="Linked to CRM Customer">
                          <Chip 
                            icon={<LinkIcon />} 
                            label="Linked" 
                            size="small" 
                            color="success" 
                            variant="outlined"
                          />
                        </Tooltip>
                      ) : (
                        <Tooltip title="Not linked to CRM">
                          <Chip 
                            label="Not Linked" 
                            size="small" 
                            color="default" 
                            variant="outlined"
                          />
                        </Tooltip>
                      )}
                    </TableCell>
                    <TableCell>
                      {new Date(client.created_at).toLocaleDateString('en-GB')}
                    </TableCell>
                    <TableCell>
                      <Tooltip title="View Details">
                        <IconButton
                          size="small"
                          onClick={() => navigate(`/enforcesense/clients/${client.id}`)}
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

      {/* Create Client Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Client</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              label="Name *"
              value={newClient.name}
              onChange={(e) => setNewClient({ ...newClient, name: e.target.value })}
              sx={{ mb: 2 }}
              required
            />
            <TextField
              fullWidth
              label="Company Name"
              value={newClient.company_name}
              onChange={(e) => setNewClient({ ...newClient, company_name: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Email"
              type="email"
              value={newClient.email}
              onChange={(e) => setNewClient({ ...newClient, email: e.target.value })}
              error={newClient.email !== '' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(newClient.email)}
              helperText={newClient.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(newClient.email) ? 'Invalid email format' : ''}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Phone"
              value={newClient.phone}
              onChange={(e) => setNewClient({ ...newClient, phone: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Address"
              multiline
              rows={2}
              value={newClient.address}
              onChange={(e) => setNewClient({ ...newClient, address: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Postcode"
              value={newClient.postcode}
              onChange={(e) => setNewClient({ ...newClient, postcode: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleCreateClient}
            disabled={!newClient.name.trim()}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Clients;

