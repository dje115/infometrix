/**
 * EnforceSense Reports Page
 * 
 * Placeholder page for EnforceSense reporting and analytics.
 */

import React from 'react';
import { Container, Box, Typography, Paper, Alert } from '@mui/material';
import { Assessment as AssessmentIcon } from '@mui/icons-material';

const Reports: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <AssessmentIcon sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
          <Typography variant="h4" component="h1">
            Reports
          </Typography>
        </Box>

        <Alert severity="info">
          <Typography variant="body1" gutterBottom>
            <strong>Reports - Coming Soon</strong>
          </Typography>
          <Typography variant="body2">
            This page will provide reporting and analytics for debt recovery operations,
            including case statistics, recovery rates, and performance metrics.
          </Typography>
        </Alert>
      </Paper>
    </Container>
  );
};

export default Reports;

