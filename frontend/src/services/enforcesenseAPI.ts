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
  getDashboard: (config?: any) => enforcementApiClient.get('/enforcesense/dashboard', config),

  // Debtors
  listDebtors: (params?: any, config?: any) => enforcementApiClient.get('/enforcesense/debtors', { params, ...config }),
  getDebtor: (id: string, config?: any) => enforcementApiClient.get(`/enforcesense/debtors/${id}`, config),
  createDebtor: (data: any, config?: any) => enforcementApiClient.post('/enforcesense/debtors', data, config),
  updateDebtor: (id: string, data: any, config?: any) => enforcementApiClient.put(`/enforcesense/debtors/${id}`, data, config),
  deleteDebtor: (id: string, config?: any) => enforcementApiClient.delete(`/enforcesense/debtors/${id}`, config),
  getDebtorAuditLogs: (id: string, params?: any, config?: any) => enforcementApiClient.get(`/enforcesense/debtors/${id}/audit`, { params, ...config }),
  addDebtorAddress: (debtorId: string, data: any, config?: any) => enforcementApiClient.post(`/enforcesense/debtors/${debtorId}/addresses`, data, config),
  updateDebtorAddress: (debtorId: string, addressId: string, data: any, config?: any) => enforcementApiClient.put(`/enforcesense/debtors/${debtorId}/addresses/${addressId}`, data, config),
  deleteDebtorAddress: (debtorId: string, addressId: string, config?: any) => enforcementApiClient.delete(`/enforcesense/debtors/${debtorId}/addresses/${addressId}`, config),
  updateDebtorVulnerability: (debtorId: string, data: any, config?: any) => enforcementApiClient.put(`/enforcesense/debtors/${debtorId}/vulnerability`, data, config),

  // Clients
  listClients: (params?: any, config?: any) => enforcementApiClient.get('/enforcesense/clients', { params, ...config }),
  getClient: (id: string, config?: any) => enforcementApiClient.get(`/enforcesense/clients/${id}`, config),
  createClient: (data: any, config?: any) => enforcementApiClient.post('/enforcesense/clients', data, config),
  updateClient: (id: string, data: any, config?: any) => enforcementApiClient.put(`/enforcesense/clients/${id}`, data, config),

  // Cases
  listCases: (params?: any, config?: any) => enforcementApiClient.get('/enforcesense/cases', { params, ...config }),
  getCase: (id: string, config?: any) => enforcementApiClient.get(`/enforcesense/cases/${id}`, config),
  createCase: (data: any, config?: any) => enforcementApiClient.post('/enforcesense/cases', data, config),
  updateCase: (id: string, data: any, config?: any) => enforcementApiClient.put(`/enforcesense/cases/${id}`, data, config),
  getCaseStatusHistory: (id: string, params?: any, config?: any) => enforcementApiClient.get(`/enforcesense/cases/${id}/status-history`, { params, ...config }),
  bulkUpdateCaseStatus: (data: any, config?: any) => enforcementApiClient.post('/enforcesense/cases/bulk-update-status', data, config),
  bulkAssignCases: (data: any, config?: any) => enforcementApiClient.post('/enforcesense/cases/bulk-assign', data, config),

  // Case Notes (with AI improvement)
  addCaseNote: (caseId: string, note: string, triggerAI: boolean = true, config?: any) =>
    enforcementApiClient.post(`/enforcesense/cases/${caseId}/notes`, { note, trigger_ai: triggerAI }, config),
  getCaseNotes: (caseId: string, config?: any) => enforcementApiClient.get(`/enforcesense/cases/${caseId}/notes`, config),
  improveNote: (caseId: string, noteId: string, config?: any) =>
    enforcementApiClient.post(`/enforcesense/cases/${caseId}/notes/${noteId}/improve`, {}, config),

  // Case Transactions / Ledger
  getCaseLedger: (caseId: string, params?: any, config?: any) =>
    enforcementApiClient.get(`/enforcesense/cases/${caseId}/ledger`, { params, ...config }),
  getCaseBalance: (caseId: string, config?: any) =>
    enforcementApiClient.get(`/enforcesense/cases/${caseId}/balance`, config),
  recordPrincipalCharge: (caseId: string, data: any, config?: any) =>
    enforcementApiClient.post(`/enforcesense/cases/${caseId}/principal-charge`, data, config),
  recordFee: (caseId: string, data: any, config?: any) =>
    enforcementApiClient.post(`/enforcesense/cases/${caseId}/fee`, data, config),
  recordInterest: (caseId: string, data: any, config?: any) =>
    enforcementApiClient.post(`/enforcesense/cases/${caseId}/interest`, data, config),
  recordCost: (caseId: string, data: any, config?: any) =>
    enforcementApiClient.post(`/enforcesense/cases/${caseId}/cost`, data, config),

  // Payment Processing
  recordPayment: (caseId: string, data: any, config?: any) =>
    enforcementApiClient.post(`/enforcesense/cases/${caseId}/payments`, data, config),
  allocatePayment: (paymentEntryId: string, data: any, config?: any) =>
    enforcementApiClient.post(`/enforcesense/payments/${paymentEntryId}/allocate`, data, config),
  getPaymentAllocation: (paymentEntryId: string, config?: any) =>
    enforcementApiClient.get(`/enforcesense/payments/${paymentEntryId}/allocation`, config),
  getCasePayments: (caseId: string, params?: any, config?: any) =>
    enforcementApiClient.get(`/enforcesense/cases/${caseId}/payments`, { params, ...config }),
  processRefund: (caseId: string, data: any, config?: any) =>
    enforcementApiClient.post(`/enforcesense/cases/${caseId}/refunds`, data, config),

  // Arrangements
  createArrangement: (caseId: string, data: any, config?: any) =>
    enforcementApiClient.post(`/enforcesense/cases/${caseId}/arrangements`, data, config),
  getCaseArrangements: (caseId: string, params?: any, config?: any) =>
    enforcementApiClient.get(`/enforcesense/cases/${caseId}/arrangements`, { params, ...config }),
  getArrangement: (arrangementId: string, config?: any) =>
    enforcementApiClient.get(`/enforcesense/arrangements/${arrangementId}`, config),
  updateArrangementSchedule: (arrangementId: string, data: any, config?: any) =>
    enforcementApiClient.put(`/enforcesense/arrangements/${arrangementId}/schedule`, data, config),
  updateArrangementStatus: (arrangementId: string, data: any, config?: any) =>
    enforcementApiClient.put(`/enforcesense/arrangements/${arrangementId}/status`, data, config),
};

