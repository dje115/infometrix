/**
 * EnforceSense Module Types
 * 
 * Type definitions specific to the EnforceSense module.
 */

/**
 * Debtor (person or company that owes debt)
 */
export interface Debtor {
  id: string;
  name: string;
  type: 'person' | 'company';
  contact_info?: {
    email?: string;
    phone?: string;
    address?: string;
  };
  created_at: string;
  updated_at: string;
}

/**
 * Case (links client from CRM to debtor)
 */
export interface Case {
  id: string;
  client_id: string; // Links to CRM Customer
  debtor_id: string;
  case_number: string;
  status: CaseStatus;
  amount: number;
  currency: string;
  created_at: string;
  updated_at: string;
}

/**
 * Case status enum
 */
export enum CaseStatus {
  OPEN = 'open',
  IN_PROGRESS = 'in_progress',
  RESOLVED = 'resolved',
  CLOSED = 'closed',
}

