import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  Alert,
  CircularProgress,
  Divider,
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
  Chip
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Edit as EditIcon,
  Business as BusinessIcon,
  Folder as FolderIcon,
  OpenInNew as OpenInNewIcon
} from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';
import { enforcesenseAPI } from '../../../services/enforcesenseAPI';

interface Client {
  id: string;
  customer_id?: string; // Link to main CRM Customer
  name: string;
  company_name?: string;
  company_registration_number?: string;
  email?: string;
  phone?: string;
  address?: string;
  postcode?: string;
  reference_prefix?: string;
  default_case_type?: string;
  created_at: string;
  updated_at: string;
}

interface Case {
  id: string;
  case_reference: string;
  status: string;
  original_amount: number;
  current_balance: number;
  debtor?: {
    legal_name: string;
  };
  created_at: string;
}

const ClientDetail: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [client, setClient] = useState<Client | null>(null);
  const [cases, setCases] = useState<Case[]>([]);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editData, setEditData] = useState<any>({});

  useEffect(() => {
    if (id) {
      loadClient();
      loadCases();
    }
  }, [id]);

  const loadClient = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await enforcesenseAPI.getClient(id!);
      setClient(response.data);
      setEditData(response.data);
    } catch (err: any) {
      console.error('Failed to load client:', err);
      setError(err.response?.data?.detail || 'Failed to load client');
    } finally {
      setLoading(false);
    }
  };

  const loadCases = async () => {
    try {
      const response = await enforcesenseAPI.listCases({ client_id: id, limit: 100 });
      setCases(response.data || []);
    } catch (err) {
      console.error('Failed to load cases:', err);
    }
  };

  const handleUpdateClient = async () => {
    try {
      await enforcesenseAPI.updateClient(id!, editData);
      setEditDialogOpen(false);
      loadClient();
    } catch (err: any) {
      console.error('Failed to update client:', err);
      setError(err.response?.data?.detail || 'Failed to update client');
    }
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
      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error && !client) {
    return (
      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  if (!client) {
    return (
      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Alert severity="warning">Client not found</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      <Box mb={3} display="flex" alignItems="center" gap={2}>
        <IconButton onClick={() => navigate('/enforcesense/clients')}>
          <ArrowBackIcon />
        </IconButton>
        <Box flex={1}>
          <Typography variant="h4" component="h1">
            {client.name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Created {new Date(client.created_at).toLocaleDateString('en-GB')}
            {client.customer_id && (
              <> • Linked to CRM Customer</>
            )}
          </Typography>
        </Box>
        {client.customer_id && (
          <Button
            variant="contained"
            color="primary"
            startIcon={<OpenInNewIcon />}
            onClick={() => navigate(`/customers/${client.customer_id}`)}
            sx={{ mr: 1 }}
          >
            View in CRM
          </Button>
        )}
        <Button
          variant="outlined"
          startIcon={<EditIcon />}
          onClick={() => setEditDialogOpen(true)}
        >
          Edit Settings
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {client.customer_id ? (
        <Alert severity="info" sx={{ mb: 2 }}>
          <strong>Note:</strong> This client is linked to a CRM Customer. Client data (name, contacts, sales) is managed in the main CRM. 
          This page shows enforcement-specific settings and features only.
        </Alert>
      ) : (
        <Alert severity="warning" sx={{ mb: 2 }}>
          <strong>Not linked to CRM:</strong> This enforcement client is not linked to a CRM Customer. 
          To manage client data (name, contacts, sales), link this client to a Customer in the main CRM.
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Client Information
            </Typography>
            {client.customer_id && (
              <Box sx={{ mb: 2, p: 1.5, bgcolor: 'info.light', borderRadius: 1 }}>
                <Typography variant="body2" color="info.dark">
                  <strong>Linked to CRM Customer:</strong> Basic client information (name, company, contacts) is managed in the main CRM. 
                  Click "View in CRM" above to manage client data, contacts, and sales activities.
                </Typography>
              </Box>
            )}
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="body2" color="text.secondary">
                  Name
                </Typography>
                <Typography variant="body1" fontWeight="bold">
                  {client.name}
                </Typography>
              </Grid>
              {client.company_name && (
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    Company Name
                  </Typography>
                  <Typography variant="body1">{client.company_name}</Typography>
                </Grid>
              )}
              {client.company_registration_number && (
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    Company Registration Number
                  </Typography>
                  <Typography variant="body1">{client.company_registration_number}</Typography>
                </Grid>
              )}
              <Grid item xs={12} md={6}>
                <Typography variant="body2" color="text.secondary">
                  Email
                </Typography>
                <Typography variant="body1">{client.email || 'N/A'}</Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="body2" color="text.secondary">
                  Phone
                </Typography>
                <Typography variant="body1">{client.phone || 'N/A'}</Typography>
              </Grid>
              {client.address && (
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">
                    Address
                  </Typography>
                  <Typography variant="body1">
                    {client.address}
                    {client.postcode && `, ${client.postcode}`}
                  </Typography>
                </Grid>
              )}
            </Grid>
          </Paper>

          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Cases
            </Typography>
            {cases.length === 0 ? (
              <Typography color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>
                No cases found for this client
              </Typography>
            ) : (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Case Reference</TableCell>
                      <TableCell>Debtor</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell align="right">Original Amount</TableCell>
                      <TableCell align="right">Current Balance</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {cases.map((caseItem) => (
                      <TableRow key={caseItem.id} hover>
                        <TableCell>
                          <Typography variant="body2" fontWeight="bold">
                            {caseItem.case_reference}
                          </Typography>
                        </TableCell>
                        <TableCell>{caseItem.debtor?.legal_name || 'N/A'}</TableCell>
                        <TableCell>
                          <Chip
                            label={caseItem.status}
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
                          <Button
                            size="small"
                            onClick={() => navigate(`/enforcesense/cases/${caseItem.id}`)}
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
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Stats
              </Typography>
              <Box>
                <Box display="flex" justifyContent="space-between" mb={2}>
                  <Typography variant="body2">Total Cases:</Typography>
                  <Typography variant="body1" fontWeight="bold">
                    {cases.length}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" mb={2}>
                  <Typography variant="body2">Active Cases:</Typography>
                  <Typography variant="body1" fontWeight="bold">
                    {cases.filter(c => c.status === 'active').length}
                  </Typography>
                </Box>
                <Divider sx={{ my: 2 }} />
                <Button
                  fullWidth
                  variant="contained"
                  startIcon={<FolderIcon />}
                  onClick={() => navigate('/enforcesense/cases', { state: { clientId: id } })}
                >
                  View All Cases
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Edit Client</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              label="Name *"
              value={editData.name || ''}
              onChange={(e) => setEditData({ ...editData, name: e.target.value })}
              sx={{ mb: 2 }}
              required
            />
            <TextField
              fullWidth
              label="Company Name"
              value={editData.company_name || ''}
              onChange={(e) => setEditData({ ...editData, company_name: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Email"
              type="email"
              value={editData.email || ''}
              onChange={(e) => setEditData({ ...editData, email: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Phone"
              value={editData.phone || ''}
              onChange={(e) => setEditData({ ...editData, phone: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Address"
              multiline
              rows={2}
              value={editData.address || ''}
              onChange={(e) => setEditData({ ...editData, address: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Postcode"
              value={editData.postcode || ''}
              onChange={(e) => setEditData({ ...editData, postcode: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleUpdateClient}>
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ClientDetail;

