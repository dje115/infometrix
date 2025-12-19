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

const CaseView: React.FC = () => {
  const { t, i18n } = useTranslation()
  const { caseId } = useParams<{ caseId: string }>()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [caseData, setCaseData] = useState<any>(null)

  useEffect(() => {
    const loadCase = async () => {
      setLoading(true)
      setError('')
      
      try {
        // TODO: Call Enforcement API to get case details
        // const token = sessionStorage.getItem('debtor_portal_token')
        // const response = await axios.get(`http://localhost:8001/api/v1/portal/cases/${caseId}`, {
        //   headers: { 'X-Debtor-Token': token, 'Accept-Language': i18n.language }
        // })
        // setCaseData(response.data)
        
        // Placeholder for now
        setCaseData({
          id: caseId,
          case_reference: 'CASE-001',
          status: 'active',
          original_amount: 1000.00,
          current_balance: 850.00
        })
      } catch (err) {
        setError(t('case.error'))
      } finally {
        setLoading(false)
      }
    }
    
    if (caseId) {
      loadCase()
    }
  }, [caseId, t, i18n.language])

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
                <Typography variant="h6">
                  £{caseData.current_balance.toFixed(2)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  )
}

export default CaseView

