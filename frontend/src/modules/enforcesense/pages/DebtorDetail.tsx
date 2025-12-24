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
  Tabs,
  Tab,
  List
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Edit as EditIcon,
  Person as PersonIcon,
  Business as BusinessIcon,
  Folder as FolderIcon,
  LocationOn as LocationIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';
import { enforcesenseAPI } from '../../../services/enforcesenseAPI';

interface Debtor {
  id: string;
  entity_type: string;
  legal_name: string;
  first_name?: string;
  last_name?: string;
  date_of_birth?: string;
  national_identifier?: string;
  company_registration_number?: string;
  email?: string;
  phone?: string;
  address_history: any[];
  language_preference: string;
  is_vulnerable: boolean;
  vulnerability_notes?: string;
  risk_flags: string[];
  created_at: string;
  updated_at: string;
}

interface Case {
  id: string;
  case_reference: string;
  status: string;
  original_amount: number;
  current_balance: number;
  client?: {
    name: string;
  };
  created_at: string;
}

const DebtorDetail: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [debtor, setDebtor] = useState<Debtor | null>(null);
  const [cases, setCases] = useState<Case[]>([]);
  const [tabValue, setTabValue] = useState(0);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editData, setEditData] = useState<any>({});
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [loadingAuditLogs, setLoadingAuditLogs] = useState(false);
  const [addressDialogOpen, setAddressDialogOpen] = useState(false);
  const [editingAddress, setEditingAddress] = useState<any | null>(null);
  const [addressForm, setAddressForm] = useState({
    address: '',
    postcode: '',
    is_current: false,
    from_date: '',
    to_date: '',
    notes: ''
  });
  const [vulnerabilityDialogOpen, setVulnerabilityDialogOpen] = useState(false);
  const [vulnerabilityForm, setVulnerabilityForm] = useState({
    is_vulnerable: false,
    vulnerability_notes: ''
  });

  useEffect(() => {
    if (id) {
      loadDebtor();
      loadCases();
    }
  }, [id]);

  useEffect(() => {
    if (id && tabValue === 3) {
      loadAuditLogs();
    }
  }, [id, tabValue]);

  const loadAuditLogs = async () => {
    if (!id) return;
    try {
      setLoadingAuditLogs(true);
      const response = await enforcesenseAPI.getDebtorAuditLogs(id);
      setAuditLogs(response.data || []);
    } catch (err: any) {
      console.error('Failed to load audit logs:', err);
    } finally {
      setLoadingAuditLogs(false);
    }
  };

  const loadDebtor = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await enforcesenseAPI.getDebtor(id!);
      setDebtor(response.data);
      setEditData(response.data);
    } catch (err: any) {
      console.error('Failed to load debtor:', err);
      setError(err.response?.data?.detail || 'Failed to load debtor');
    } finally {
      setLoading(false);
    }
  };

  const loadCases = async () => {
    try {
      const response = await enforcesenseAPI.listCases({ debtor_id: id, limit: 100 });
      setCases(response.data || []);
    } catch (err) {
      console.error('Failed to load cases:', err);
    }
  };

  const handleUpdateDebtor = async () => {
    try {
      await enforcesenseAPI.updateDebtor(id!, editData);
      setEditDialogOpen(false);
      loadDebtor();
    } catch (err: any) {
      console.error('Failed to update debtor:', err);
      setError(err.response?.data?.detail || 'Failed to update debtor');
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

  if (error && !debtor) {
    return (
      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  if (!debtor) {
    return (
      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Alert severity="warning">Debtor not found</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      <Box mb={3} display="flex" alignItems="center" gap={2}>
        <IconButton onClick={() => navigate('/enforcesense/debtors')}>
          <ArrowBackIcon />
        </IconButton>
        <Box flex={1}>
          <Typography variant="h4" component="h1">
            {debtor.legal_name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {debtor.entity_type} • Created {new Date(debtor.created_at).toLocaleDateString('en-GB')}
          </Typography>
        </Box>
        <Chip
          label={debtor.entity_type}
          color={debtor.entity_type === 'PERSON' ? 'primary' : 'secondary'}
        />
        {debtor.is_vulnerable && (
          <Chip label="Vulnerable" color="warning" />
        )}
        <Button
          variant="outlined"
          startIcon={<EditIcon />}
          onClick={() => setEditDialogOpen(true)}
        >
          Edit
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab icon={<InfoIcon />} iconPosition="start" label="Information" />
          <Tab icon={<FolderIcon />} iconPosition="start" label={`Cases (${cases.length})`} />
          <Tab icon={<LocationIcon />} iconPosition="start" label="Address History" />
          <Tab icon={<InfoIcon />} iconPosition="start" label="Audit Trail" />
        </Tabs>
      </Paper>

      {tabValue === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Personal Information
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    Legal Name
                  </Typography>
                  <Typography variant="body1" fontWeight="bold">
                    {debtor.legal_name}
                  </Typography>
                </Grid>
                {debtor.first_name && (
                  <Grid item xs={12} md={6}>
                    <Typography variant="body2" color="text.secondary">
                      First Name
                    </Typography>
                    <Typography variant="body1">{debtor.first_name}</Typography>
                  </Grid>
                )}
                {debtor.last_name && (
                  <Grid item xs={12} md={6}>
                    <Typography variant="body2" color="text.secondary">
                      Last Name
                    </Typography>
                    <Typography variant="body1">{debtor.last_name}</Typography>
                  </Grid>
                )}
                {debtor.date_of_birth && (
                  <Grid item xs={12} md={6}>
                    <Typography variant="body2" color="text.secondary">
                      Date of Birth
                    </Typography>
                    <Typography variant="body1">
                      {new Date(debtor.date_of_birth).toLocaleDateString('en-GB')}
                    </Typography>
                  </Grid>
                )}
                {debtor.national_identifier && (
                  <Grid item xs={12} md={6}>
                    <Typography variant="body2" color="text.secondary">
                      National Identifier
                    </Typography>
                    <Typography variant="body1">{debtor.national_identifier}</Typography>
                  </Grid>
                )}
                {debtor.company_registration_number && (
                  <Grid item xs={12} md={6}>
                    <Typography variant="body2" color="text.secondary">
                      Company Registration Number
                    </Typography>
                    <Typography variant="body1">{debtor.company_registration_number}</Typography>
                  </Grid>
                )}
              </Grid>

              <Divider sx={{ my: 3 }} />

              <Typography variant="h6" gutterBottom>
                Contact Information
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    Email
                  </Typography>
                  <Typography variant="body1">{debtor.email || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    Phone
                  </Typography>
                  <Typography variant="body1">{debtor.phone || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">
                    Language Preference
                  </Typography>
                  <Typography variant="body1">{debtor.language_preference || 'en'}</Typography>
                </Grid>
              </Grid>

              {debtor.is_vulnerable && (
                <>
                  <Divider sx={{ my: 3 }} />
                  <Typography variant="h6" gutterBottom>
                    Vulnerability Information
                  </Typography>
                  {debtor.vulnerability_notes && (
                    <Typography variant="body1">{debtor.vulnerability_notes}</Typography>
                  )}
                </>
              )}

              {debtor.risk_flags && debtor.risk_flags.length > 0 && (
                <>
                  <Divider sx={{ my: 3 }} />
                  <Typography variant="h6" gutterBottom>
                    Risk Flags
                  </Typography>
                  <Box display="flex" gap={1} flexWrap="wrap">
                    {debtor.risk_flags.map((flag, idx) => (
                      <Chip key={idx} label={flag} color="warning" size="small" />
                    ))}
                  </Box>
                </>
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
                    onClick={() => navigate('/enforcesense/cases', { state: { debtorId: id } })}
                  >
                    View All Cases
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {tabValue === 1 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Linked Cases
          </Typography>
          {cases.length === 0 ? (
            <Typography color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>
              No cases found for this debtor
            </Typography>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Case Reference</TableCell>
                    <TableCell>Client</TableCell>
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
                      <TableCell>{caseItem.client?.name || 'N/A'}</TableCell>
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
      )}

      {tabValue === 2 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Address History
          </Typography>
          {debtor.address_history && debtor.address_history.length > 0 ? (
            <List>
              {debtor.address_history.map((address: any, index: number) => (
                <Card key={index} sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="body1" fontWeight="bold">
                      {address.line1 || 'N/A'}
                    </Typography>
                    {address.line2 && (
                      <Typography variant="body2">{address.line2}</Typography>
                    )}
                    <Typography variant="body2">
                      {address.city || ''} {address.postcode || ''}
                    </Typography>
                    {address.country && (
                      <Typography variant="body2" color="text.secondary">
                        {address.country}
                      </Typography>
                    )}
                    {address.valid_from && (
                      <Typography variant="caption" color="text.secondary">
                        Valid from: {new Date(address.valid_from).toLocaleDateString('en-GB')}
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              ))}
            </List>
          ) : (
            <Typography color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>
              No address history recorded
            </Typography>
          )}
        </Paper>
      )}

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Edit Debtor</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              label="Legal Name *"
              value={editData.legal_name || ''}
              onChange={(e) => setEditData({ ...editData, legal_name: e.target.value })}
              sx={{ mb: 2 }}
              required
            />
            {debtor.entity_type === 'PERSON' && (
              <>
                <TextField
                  fullWidth
                  label="First Name"
                  value={editData.first_name || ''}
                  onChange={(e) => setEditData({ ...editData, first_name: e.target.value })}
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  label="Last Name"
                  value={editData.last_name || ''}
                  onChange={(e) => setEditData({ ...editData, last_name: e.target.value })}
                  sx={{ mb: 2 }}
                />
              </>
            )}
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
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleUpdateDebtor}>
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default DebtorDetail;

