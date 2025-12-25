import axios from 'axios';

// Enforcement API client (separate from Platform API)
// Enforcement API runs on port 8001 and doesn't use /api/v1 prefix
// In development with Vite proxy, use relative path to leverage proxy
// In production or when VITE_ENFORCEMENT_API_URL is set, use the explicit URL
const ENFORCEMENT_API_BASE_URL = import.meta.env.VITE_ENFORCEMENT_API_URL || (import.meta.env.DEV ? '/enforcesense' : 'http://localhost:8001');

const enforcementApiClient = axios.create({
  baseURL: ENFORCEMENT_API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,  // IMPORTANT: Required for HttpOnly cookies
});

// Add response interceptor for error handling
enforcementApiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const enforcesenseAPI = {
  // Dashboard
  getDashboard: () => enforcementApiClient.get('/enforcesense/dashboard'),

  // Debtors
  listDebtors: (params?: any) => enforcementApiClient.get('/enforcesense/debtors', { params }),
  getDebtor: (id: string) => enforcementApiClient.get(`/enforcesense/debtors/${id}`),
  createDebtor: (data: any) => enforcementApiClient.post('/enforcesense/debtors', data),
  updateDebtor: (id: string, data: any) => enforcementApiClient.put(`/enforcesense/debtors/${id}`, data),
  deleteDebtor: (id: string) => enforcementApiClient.delete(`/enforcesense/debtors/${id}`),
  getDebtorAuditLogs: (id: string, params?: any) => enforcementApiClient.get(`/enforcesense/debtors/${id}/audit`, { params }),
  addDebtorAddress: (debtorId: string, data: any) => enforcementApiClient.post(`/enforcesense/debtors/${debtorId}/addresses`, data),
  updateDebtorAddress: (debtorId: string, addressId: string, data: any) => enforcementApiClient.put(`/enforcesense/debtors/${debtorId}/addresses/${addressId}`, data),
  deleteDebtorAddress: (debtorId: string, addressId: string) => enforcementApiClient.delete(`/enforcesense/debtors/${debtorId}/addresses/${addressId}`),
  updateDebtorVulnerability: (debtorId: string, data: any) => enforcementApiClient.put(`/enforcesense/debtors/${debtorId}/vulnerability`, data),

  // Clients
  listClients: (params?: any) => enforcementApiClient.get('/enforcesense/clients', { params }),
  getClient: (id: string) => enforcementApiClient.get(`/enforcesense/clients/${id}`),
  createClient: (data: any) => enforcementApiClient.post('/enforcesense/clients', data),
  updateClient: (id: string, data: any) => enforcementApiClient.put(`/enforcesense/clients/${id}`, data),

  // Cases
  listCases: (params?: any) => enforcementApiClient.get('/enforcesense/cases', { params }),
  getCase: (id: string) => enforcementApiClient.get(`/enforcesense/cases/${id}`),
  createCase: (data: any) => enforcementApiClient.post('/enforcesense/cases', data),
  updateCase: (id: string, data: any) => enforcementApiClient.put(`/enforcesense/cases/${id}`, data),
  getCaseStatusHistory: (id: string, params?: any) => enforcementApiClient.get(`/enforcesense/cases/${id}/status-history`, { params }),
  bulkUpdateCaseStatus: (data: any) => enforcementApiClient.post('/enforcesense/cases/bulk-update-status', data),
  bulkAssignCases: (data: any) => enforcementApiClient.post('/enforcesense/cases/bulk-assign', data),

  // Case Notes (with AI improvement)
  addCaseNote: (caseId: string, note: string, triggerAI: boolean = true) =>
    enforcementApiClient.post(`/enforcesense/cases/${caseId}/notes`, { note, trigger_ai: triggerAI }),
  getCaseNotes: (caseId: string) => enforcementApiClient.get(`/enforcesense/cases/${caseId}/notes`),
  improveNote: (caseId: string, noteId: string) =>
    enforcementApiClient.post(`/enforcesense/cases/${caseId}/notes/${noteId}/improve`),

  // Case Transactions / Ledger
  getCaseLedger: (caseId: string, params?: any) =>
    enforcementApiClient.get(`/enforcesense/cases/${caseId}/ledger`, { params }),
  getCaseBalance: (caseId: string) =>
    enforcementApiClient.get(`/enforcesense/cases/${caseId}/balance`),
  recordPrincipalCharge: (caseId: string, data: any) =>
    enforcementApiClient.post(`/enforcesense/cases/${caseId}/principal-charge`, data),
  recordFee: (caseId: string, data: any) =>
    enforcementApiClient.post(`/enforcesense/cases/${caseId}/fee`, data),
  recordInterest: (caseId: string, data: any) =>
    enforcementApiClient.post(`/enforcesense/cases/${caseId}/interest`, data),
  recordCost: (caseId: string, data: any) =>
    enforcementApiClient.post(`/enforcesense/cases/${caseId}/cost`, data),

  // Payment Processing
  recordPayment: (caseId: string, data: any) =>
    enforcementApiClient.post(`/enforcesense/cases/${caseId}/payments`, data),
  allocatePayment: (paymentEntryId: string, data: any) =>
    enforcementApiClient.post(`/enforcesense/payments/${paymentEntryId}/allocate`, data),
  getPaymentAllocation: (paymentEntryId: string) =>
    enforcementApiClient.get(`/enforcesense/payments/${paymentEntryId}/allocation`),
  getCasePayments: (caseId: string, params?: any) =>
    enforcementApiClient.get(`/enforcesense/cases/${caseId}/payments`, { params }),
  processRefund: (caseId: string, data: any) =>
    enforcementApiClient.post(`/enforcesense/cases/${caseId}/refunds`, data),

  // Arrangements
  createArrangement: (caseId: string, data: any) =>
    enforcementApiClient.post(`/enforcesense/cases/${caseId}/arrangements`, data),
  getCaseArrangements: (caseId: string, params?: any) =>
    enforcementApiClient.get(`/enforcesense/cases/${caseId}/arrangements`, { params }),
  getArrangement: (arrangementId: string) =>
    enforcementApiClient.get(`/enforcesense/arrangements/${arrangementId}`),
  updateArrangementSchedule: (arrangementId: string, data: any) =>
    enforcementApiClient.put(`/enforcesense/arrangements/${arrangementId}/schedule`, data),
  updateArrangementStatus: (arrangementId: string, data: any) =>
    enforcementApiClient.put(`/enforcesense/arrangements/${arrangementId}/status`, data),
};

