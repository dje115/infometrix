/**
 * API Client for Debtor Portal
 * Communicates with Enforcement API
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Store portal token in session storage
export const setPortalToken = (token: string) => {
  sessionStorage.setItem('portal_token', token);
};

export const getPortalToken = (): string | null => {
  return sessionStorage.getItem('portal_token');
};

export const clearPortalToken = () => {
  sessionStorage.removeItem('portal_token');
};

// Add token to requests if available
apiClient.interceptors.request.use((config) => {
  const token = getPortalToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface PortalSession {
  session_id: string;
  token: string;
  expires_at: string;
  case_id: string;
}

export interface CaseData {
  id: string;
  case_number: string;
  status: string;
  amount?: number;
  due_date?: string;
  description?: string;
}

export const portalAPI = {
  /**
   * Create a portal session
   */
  createSession: async (caseId: string, debtorId?: string): Promise<PortalSession> => {
    const response = await apiClient.post<PortalSession>('/portal/sessions', {
      case_id: caseId,
      debtor_id: debtorId,
    });
    
    // Store token
    setPortalToken(response.data.token);
    
    return response.data;
  },

  /**
   * Get case data for portal
   */
  getCase: async (caseId: string): Promise<CaseData> => {
    const response = await apiClient.get<CaseData>(`/portal/cases/${caseId}`);
    return response.data;
  },
};

export default apiClient;

