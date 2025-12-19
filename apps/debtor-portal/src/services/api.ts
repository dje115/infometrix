/**
 * API client for Debtor Portal
 * 
 * Communicates with Enforcement API.
 */

import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_ENFORCEMENT_API_URL || 'http://localhost:8001'

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}`,  // Enforcement API doesn't use /api/v1 prefix
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// Add token to requests if available
apiClient.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('debtor_portal_token')
  if (token) {
    config.headers['X-Debtor-Token'] = token
  }
  
  // Add language preference
  const language = localStorage.getItem('debtor_portal_language') || 'en'
  config.headers['Accept-Language'] = language
  
  return config
})

export const debtorPortalAPI = {
  // Create portal session
  createSession: async (caseReference: string, locale: string = 'en') => {
    const response = await apiClient.post('/portal/sessions', {
      case_reference: caseReference,
      locale: locale
    })
    return response.data
  },
  
  // Get case details
  getCase: async (caseId: string) => {
    const response = await apiClient.get(`/portal/cases/${caseId}`)
    return response.data
  },
  
  // Get case transactions
  getCaseTransactions: async (caseId: string) => {
    const response = await apiClient.get(`/portal/cases/${caseId}/transactions`)
    return response.data
  },
}

export default apiClient

