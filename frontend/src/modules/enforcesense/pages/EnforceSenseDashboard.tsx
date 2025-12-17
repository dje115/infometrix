/**
 * EnforceSense Dashboard
 * 
 * Placeholder dashboard for the EnforceSense debt recovery module.
 */

import React from 'react';
import { Container, Box, Typography, Paper, Alert } from '@mui/material';
import { Gavel as GavelIcon } from '@mui/icons-material';

const EnforceSenseDashboard: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <GavelIcon sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
          <Typography variant="h4" component="h1">
            EnforceSense Dashboard
          </Typography>
        </Box>

        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body1" gutterBottom>
            <strong>EnforceSense Module - Coming Soon</strong>
          </Typography>
          <Typography variant="body2">
            The EnforceSense module is currently under development. This module will provide
            debt recovery and enforcement capabilities integrated with the Infometrix platform.
          </Typography>
        </Alert>

        <Box sx={{ mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            Planned Features
          </Typography>
          <Typography variant="body2" component="ul" sx={{ pl: 2 }}>
            <li>Case management for debt recovery</li>
            <li>Client and debtor management</li>
            <li>Integration with CRM customers</li>
            <li>Reporting and analytics</li>
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default EnforceSenseDashboard;

