/**
 * EnforceSense Cases Page
 * 
 * Placeholder page for managing debt recovery cases.
 */

import React from 'react';
import { Container, Box, Typography, Paper, Alert } from '@mui/material';
import { Folder as FolderIcon } from '@mui/icons-material';

const Cases: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <FolderIcon sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
          <Typography variant="h4" component="h1">
            Cases
          </Typography>
        </Box>

        <Alert severity="info">
          <Typography variant="body1" gutterBottom>
            <strong>Cases Management - Coming Soon</strong>
          </Typography>
          <Typography variant="body2">
            This page will display and manage debt recovery cases, linking clients from CRM
            to debtors and tracking case progress.
          </Typography>
        </Alert>
      </Paper>
    </Container>
  );
};

export default Cases;

