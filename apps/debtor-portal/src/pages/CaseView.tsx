/**
 * Case View Page for Debtor Portal
 * 
 * Displays case details (read-only skeleton).
 * All strings are translated via i18n.
 */

import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  CircularProgress,
  Alert,
  Grid,
  Card,
  CardContent
} from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import { debtorPortalAPI } from '../services/api'

const CaseView: React.FC = () => {
  const { t, i18n } = useTranslation()
  const { caseId } = useParams<{ caseId: string }>()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [caseData, setCaseData] = useState<any>(null)
  const [transactions, setTransactions] = useState<any[]>([])

  useEffect(() => {
    const loadCase = async () => {
      setLoading(true)
      setError('')
      
      try {
        // Check if token exists
        const token = sessionStorage.getItem('debtor_portal_token')
        if (!token) {
          navigate('/login')
          return
        }
        
        // Call Enforcement API to get case details
        const caseData = await debtorPortalAPI.getCase(caseId!)
        setCaseData(caseData)
        
        // Load transaction history
        try {
          const transactionsData = await debtorPortalAPI.getCaseTransactions(caseId!)
          setTransactions(transactionsData || [])
        } catch (txErr) {
          // Transactions might not be implemented yet, ignore error
          console.warn('Failed to load transactions:', txErr)
        }
      } catch (err: any) {
        console.error('Failed to load case:', err)
        if (err.response?.status === 401) {
          // Token expired or invalid, redirect to login
          sessionStorage.removeItem('debtor_portal_token')
          navigate('/login')
        } else {
          setError(err.response?.data?.detail || t('case.error'))
        }
      } finally {
        setLoading(false)
      }
    }
    
    if (caseId) {
      loadCase()
    }
  }, [caseId, t, i18n.language, navigate])

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ mt: 4, textAlign: 'center' }}>
        <CircularProgress />
        <Typography sx={{ mt: 2 }}>{t('case.loading')}</Typography>
      </Container>
    )
  }

  if (error || !caseData) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="error">{error || t('case.notFound')}</Alert>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/login')}
          sx={{ mt: 2 }}
        >
          {t('common.back')}
        </Button>
      </Container>
    )
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={() => navigate('/login')}
        sx={{ mb: 2 }}
      >
        {t('common.back')}
      </Button>
      
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {t('case.title')}
        </Typography>
        
        <Grid container spacing={3} sx={{ mt: 2 }}>
          <Grid item xs={12} sm={6}>
            <Card>
              <CardContent>
                <Typography variant="subtitle2" color="textSecondary">
                  {t('case.reference')}
                </Typography>
                <Typography variant="h6">
                  {caseData.case_reference}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <Card>
              <CardContent>
                <Typography variant="subtitle2" color="textSecondary">
                  {t('case.status')}
                </Typography>
                <Typography variant="h6">
                  {caseData.status}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <Card>
              <CardContent>
                <Typography variant="subtitle2" color="textSecondary">
                  {t('case.amount')}
                </Typography>
                <Typography variant="h6">
                  £{caseData.original_amount.toFixed(2)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <Card>
              <CardContent>
                <Typography variant="subtitle2" color="textSecondary">
                  {t('case.balance')}
                </Typography>
                <Typography variant="h6" color="primary">
                  £{caseData.current_balance.toFixed(2)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          {caseData.fees_charged !== undefined && (
            <Grid item xs={12} sm={6}>
              <Card>
                <CardContent>
                  <Typography variant="subtitle2" color="textSecondary">
                    {t('case.fees')}
                  </Typography>
                  <Typography variant="h6">
                    £{caseData.fees_charged.toFixed(2)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          )}
          
          {caseData.payments_received !== undefined && (
            <Grid item xs={12} sm={6}>
              <Card>
                <CardContent>
                  <Typography variant="subtitle2" color="textSecondary">
                    {t('case.payments')}
                  </Typography>
                  <Typography variant="h6" color="success.main">
                    £{caseData.payments_received.toFixed(2)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
        
        {/* Payment History Section */}
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" gutterBottom>
            {t('case.paymentHistory')}
          </Typography>
          
          {transactions.length === 0 ? (
            <Alert severity="info" sx={{ mt: 2 }}>
              {t('case.noPayments')}
            </Alert>
          ) : (
            <Box sx={{ mt: 2 }}>
              {transactions.map((tx: any, index: number) => (
                <Card key={index} sx={{ mb: 2 }}>
                  <CardContent>
                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={3}>
                        <Typography variant="subtitle2" color="textSecondary">
                          {t('case.date')}
                        </Typography>
                        <Typography variant="body1">
                          {new Date(tx.date || tx.created_at).toLocaleDateString(i18n.language)}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} sm={3}>
                        <Typography variant="subtitle2" color="textSecondary">
                          {t('case.type')}
                        </Typography>
                        <Typography variant="body1">
                          {tx.type || 'Payment'}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} sm={3}>
                        <Typography variant="subtitle2" color="textSecondary">
                          {t('case.amount')}
                        </Typography>
                        <Typography variant="body1" fontWeight="bold">
                          £{tx.amount.toFixed(2)}
                        </Typography>
                      </Grid>
                      {tx.description && (
                        <Grid item xs={12} sm={3}>
                          <Typography variant="subtitle2" color="textSecondary">
                            {t('case.description')}
                          </Typography>
                          <Typography variant="body2">
                            {tx.description}
                          </Typography>
                        </Grid>
                      )}
                    </Grid>
                  </CardContent>
                </Card>
              ))}
            </Box>
          )}
        </Box>
      </Paper>
    </Container>
  )
}

export default CaseView

