import { apiClient } from './api';

export const enforcesenseAPI = {
  // Dashboard
  getDashboard: () => apiClient.get('/modules/enforcesense/dashboard'),

  // Debtors
  listDebtors: (params?: any) => apiClient.get('/modules/enforcesense/debtors', { params }),
  getDebtor: (id: string) => apiClient.get(`/modules/enforcesense/debtors/${id}`),
  createDebtor: (data: any) => apiClient.post('/modules/enforcesense/debtors', data),
  updateDebtor: (id: string, data: any) => apiClient.put(`/modules/enforcesense/debtors/${id}`, data),
  deleteDebtor: (id: string) => apiClient.delete(`/modules/enforcesense/debtors/${id}`),

  // Clients
  listClients: (params?: any) => apiClient.get('/modules/enforcesense/clients', { params }),
  getClient: (id: string) => apiClient.get(`/modules/enforcesense/clients/${id}`),
  createClient: (data: any) => apiClient.post('/modules/enforcesense/clients', data),
  updateClient: (id: string, data: any) => apiClient.put(`/modules/enforcesense/clients/${id}`, data),

  // Cases
  listCases: (params?: any) => apiClient.get('/modules/enforcesense/cases', { params }),
  getCase: (id: string) => apiClient.get(`/modules/enforcesense/cases/${id}`),
  createCase: (data: any) => apiClient.post('/modules/enforcesense/cases', data),
  updateCase: (id: string, data: any) => apiClient.put(`/modules/enforcesense/cases/${id}`, data),

  // Case Notes (with AI improvement)
  addCaseNote: (caseId: string, note: string, triggerAI: boolean = true) =>
    apiClient.post(`/modules/enforcesense/cases/${caseId}/notes`, { note, trigger_ai: triggerAI }),
  getCaseNotes: (caseId: string) => apiClient.get(`/modules/enforcesense/cases/${caseId}/notes`),
  improveNote: (caseId: string, noteId: string) =>
    apiClient.post(`/modules/enforcesense/cases/${caseId}/notes/${noteId}/improve`),
};

