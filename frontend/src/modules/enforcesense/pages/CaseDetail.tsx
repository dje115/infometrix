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
  TableRow
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Edit as EditIcon,
  Add as AddIcon,
  AutoFixHigh as AutoFixHighIcon,
  CheckCircle as CheckCircleIcon
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

const CaseDetail: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [caseData, setCaseData] = useState<Case | null>(null);
  const [notes, setNotes] = useState<CaseNote[]>([]);
  const [newNote, setNewNote] = useState('');
  const [noteDialogOpen, setNoteDialogOpen] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [triggerAI, setTriggerAI] = useState(true);

  useEffect(() => {
    if (id) {
      loadCase();
      loadNotes();
    }
  }, [id]);

  const loadCase = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await enforcesenseAPI.getCase(id!);
      setCaseData(response.data);
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

  const handleAddNote = async () => {
    if (!newNote.trim()) return;

    try {
      await enforcesenseAPI.addCaseNote(id!, newNote, triggerAI);
      setNewNote('');
      setNoteDialogOpen(false);
      loadNotes();
      loadCase(); // Refresh case data
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
    <Container maxWidth="lg" sx={{ py: 3 }}>
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
        />
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Case Information */}
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
                <Typography variant="body1">
                  {caseData.client_reference || 'N/A'}
                </Typography>
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

          {/* Notes Section */}
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
                            {new Date(note.created_at).toLocaleString()}
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
        </Grid>

        {/* Financial Summary */}
        <Grid item xs={12} md={4}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Financial Summary
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">Original Amount:</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {formatCurrency(caseData.original_amount)}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">Fees Charged:</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {formatCurrency(caseData.fees_charged)}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">Payments Received:</Typography>
                  <Typography variant="body2" fontWeight="bold" color="success.main">
                    {formatCurrency(caseData.payments_received)}
                  </Typography>
                </Box>
                <Divider sx={{ my: 1 }} />
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body1" fontWeight="bold">
                    Current Balance:
                  </Typography>
                  <Typography variant="body1" fontWeight="bold" color="error.main">
                    {formatCurrency(caseData.current_balance)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          {/* Debtor Information */}
          {caseData.debtor && (
            <Card>
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
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>

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
          <Button
            variant="contained"
            onClick={handleAddNote}
            disabled={!newNote.trim()}
          >
            Add Note
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default CaseDetail;

