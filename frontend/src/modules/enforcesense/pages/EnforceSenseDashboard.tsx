import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button
} from '@mui/material';
import {
  Gavel as GavelIcon,
  People as PeopleIcon,
  Business as BusinessIcon,
  Folder as FolderIcon,
  TrendingUp as TrendingUpIcon,
  AccountBalance as AccountBalanceIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { enforcesenseAPI } from '../../../services/enforcesenseAPI';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface DashboardStats {
  total_debtors: number;
  total_clients: number;
  cases_by_status: Record<string, number>;
  total_original_amount: number;
  total_fees_charged: number;
  total_payments_received: number;
  total_current_balance: number;
}

const EnforceSenseDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<DashboardStats | null>(null);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await enforcesenseAPI.getDashboard();
      setStats(response.data);
    } catch (err: any) {
      console.error('Failed to load dashboard:', err);
      setError(err.response?.data?.detail || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

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

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      <Box mb={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          EnforceSense Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Overview of your enforcement operations
        </Typography>
      </Box>

      {stats && (
        <>
          {/* Statistics Cards */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Box>
                      <Typography color="text.secondary" gutterBottom>
                        Total Debtors
                      </Typography>
                      <Typography variant="h4">{stats.total_debtors}</Typography>
                    </Box>
                    <PeopleIcon color="primary" sx={{ fontSize: 40 }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Box>
                      <Typography color="text.secondary" gutterBottom>
                        Total Clients
                      </Typography>
                      <Typography variant="h4">{stats.total_clients}</Typography>
                    </Box>
                    <BusinessIcon color="primary" sx={{ fontSize: 40 }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Box>
                      <Typography color="text.secondary" gutterBottom>
                        Total Balance
                      </Typography>
                      <Typography variant="h4">
                        {formatCurrency(stats.total_current_balance)}
                      </Typography>
                    </Box>
                    <AccountBalanceIcon color="primary" sx={{ fontSize: 40 }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Box>
                      <Typography color="text.secondary" gutterBottom>
                        Payments Received
                      </Typography>
                      <Typography variant="h4">
                        {formatCurrency(stats.total_payments_received)}
                      </Typography>
                    </Box>
                    <TrendingUpIcon color="success" sx={{ fontSize: 40 }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Cases by Status - Chart and Table */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Cases by Status
                  </Typography>
                  {Object.keys(stats.cases_by_status).length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={Object.entries(stats.cases_by_status).map(([status, count]) => ({
                            name: status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' '),
                            value: count
                          }))}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {Object.entries(stats.cases_by_status).map(([status], index) => {
                            const colors = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82CA9D'];
                            return <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />;
                          })}
                        </Pie>
                        <Tooltip />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  ) : (
                    <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Typography color="text.secondary">No cases data available</Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Financial Overview
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart
                      data={[
                        {
                          name: 'Original',
                          amount: stats.total_original_amount
                        },
                        {
                          name: 'Fees',
                          amount: stats.total_fees_charged
                        },
                        {
                          name: 'Payments',
                          amount: stats.total_payments_received
                        },
                        {
                          name: 'Balance',
                          amount: stats.total_current_balance
                        }
                      ]}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis tickFormatter={(value) => `£${(value / 1000).toFixed(0)}k`} />
                      <Tooltip formatter={(value: number) => formatCurrency(value)} />
                      <Bar dataKey="amount" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Detailed Financial Summary */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Cases by Status (Table)
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Status</TableCell>
                          <TableCell align="right">Count</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {Object.entries(stats.cases_by_status).map(([status, count]) => (
                          <TableRow key={status}>
                            <TableCell>
                              <Chip
                                label={status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ')}
                                color={getStatusColor(status)}
                                size="small"
                              />
                            </TableCell>
                            <TableCell align="right">{count}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Financial Summary
                  </Typography>
                  <Box sx={{ mt: 2 }}>
                    <Box display="flex" justifyContent="space-between" mb={2}>
                      <Typography>Original Amount:</Typography>
                      <Typography fontWeight="bold">
                        {formatCurrency(stats.total_original_amount)}
                      </Typography>
                    </Box>
                    <Box display="flex" justifyContent="space-between" mb={2}>
                      <Typography>Fees Charged:</Typography>
                      <Typography fontWeight="bold">
                        {formatCurrency(stats.total_fees_charged)}
                      </Typography>
                    </Box>
                    <Box display="flex" justifyContent="space-between" mb={2}>
                      <Typography>Payments Received:</Typography>
                      <Typography fontWeight="bold" color="success.main">
                        {formatCurrency(stats.total_payments_received)}
                      </Typography>
                    </Box>
                    <Box display="flex" justifyContent="space-between" mb={2}>
                      <Typography>Current Balance:</Typography>
                      <Typography fontWeight="bold" color="primary.main">
                        {formatCurrency(stats.total_current_balance)}
                      </Typography>
                    </Box>
                    <Box display="flex" justifyContent="space-between" mb={2} pt={2} borderTop={1} borderColor="divider">
                      <Typography variant="subtitle2" fontWeight="bold">
                        Collection Rate:
                      </Typography>
                      <Typography variant="subtitle2" fontWeight="bold" color="success.main">
                        {stats.total_original_amount > 0
                          ? ((stats.total_payments_received / stats.total_original_amount) * 100).toFixed(1)
                          : 0}%
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Quick Actions */}
          <Box sx={{ mt: 4 }}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="contained"
                  startIcon={<FolderIcon />}
                  onClick={() => navigate('/enforcesense/cases')}
                >
                  View All Cases
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<PeopleIcon />}
                  onClick={() => navigate('/enforcesense/debtors')}
                >
                  Manage Debtors
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<BusinessIcon />}
                  onClick={() => navigate('/enforcesense/clients')}
                >
                  Manage Clients
                </Button>
              </Box>
            </Paper>
          </Box>
        </>
      )}
    </Container>
  );
};

export default EnforceSenseDashboard;



