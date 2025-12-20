# Party-Level Flags Specification

**Version:** 1.0  
**Status:** MANDATORY - Implementation Guide  
**Last Updated:** 2025-12-19

## Overview

This document defines the comprehensive set of flags that should be stored at the Party (Debtor) level so they apply across all debts/cases. Flags are organized into three layers for clean organization and enforcement.

## Three-Layer Architecture

### Layer 1: PartyProfile (Stable Facts)
**Purpose**: Store stable facts and preferences that don't change frequently

**Contains**:
- Preferred language and interpreter requirements
- Preferred contact method
- Representation (advisor/solicitor)
- Identity confidence
- Address verification status
- Known aliases

### Layer 2: PartyFlags (Boolean/Enum Signals)
**Purpose**: Store boolean/enum signals that indicate status or risk

**Contains**:
- Vulnerability indicators (structured categories)
- Safety risk flags
- Contact restrictions (no call, no visits)
- Dispute status
- Fraud concerns
- Financial behavior patterns
- Address uncertainty
- Deceased/dissolved status

### Layer 3: PartyRestrictions (Enforced Rules)
**Purpose**: Store enforced rules that control system behavior

**Contains**:
- Contact frequency limits
- Channel blocks (no calls, no SMS, etc.)
- Compliance approval requirements

## Complete Flag List

### Identity and Matching

| Flag | Type | Location | Values |
|------|------|----------|--------|
| Identity confidence | Enum | PartyProfile | LOW, MED, HIGH |
| Known aliases | Array | PartyProfile | JSON array of previous names |
| Do-not-merge | Boolean | PartyProfile | Prevents bad dedupe merges |
| Address verified | Boolean | PartyProfile | true/false |
| Address verification date | DateTime | PartyProfile | When address was verified |

### Vulnerability and Safeguarding

| Flag | Type | Location | Values |
|------|------|----------|--------|
| Vulnerability category | Enum | PartyFlags | NONE, MENTAL_HEALTH, PHYSICAL_HEALTH, DISABILITY, BEREAVEMENT, LANGUAGE_BARRIER, FINANCIAL_HARDSHIP, DOMESTIC_ABUSE_RISK, ELDERLY, PREGNANCY, CARE_LEAVER, OTHER |
| Vulnerability review date | DateTime | PartyFlags | Next review date |
| Safeguarding required | Boolean | PartyFlags | true/false |
| Safeguarding review date | DateTime | PartyFlags | Next review date |
| Preferred contact method | Enum | PartyProfile | LETTER, EMAIL, PHONE, SMS, PORTAL |
| No call flag | Boolean | PartyFlags | true/false |
| Interpreter required | Boolean | PartyProfile | true/false |
| Preferred language | String | PartyProfile | ISO 639-1 code (e.g., "en", "ro", "cs") |

### Debt Advice / Formal Protection

| Flag | Type | Location | Values |
|------|------|----------|--------|
| Debt advice engaged | Enum | PartySupportProfile | NONE, ADVICE_SOUGHT, ADVISOR_ENGAGED, FORMAL_SOLUTION_PENDING, FORMAL_SOLUTION_ACTIVE |
| Advisor organization | Enum/String | PartySupportProfile | StepChange, CAB, National Debtline, Other |
| Evidence level | Enum | PartySupportProfile | SELF_REPORTED, ADVISOR_CONFIRMED, DOCUMENTED |
| Breathing Space status | Enum | PartySupportProfile | NONE, REQUESTED, ACTIVE, ENDED |
| Insolvency status | Enum | PartySupportProfile | NONE, IVA, DRO, BANKRUPTCY, ADMINISTRATION, LIQUIDATION |
| Insolvency start date | DateTime | PartySupportProfile | When insolvency started |
| Insolvency end date | DateTime | PartySupportProfile | When insolvency ended |
| Insolvency reference | String | PartySupportProfile | Reference number if known |

### Contact and Conduct Risk

| Flag | Type | Location | Values |
|------|------|----------|--------|
| No doorstep visits | Boolean | PartyFlags | true/false |
| No doorstep visits reason | Enum | PartyFlags | SAFETY, VULNERABILITY, DISPUTE, OTHER |
| Aggression / safety risk | Enum | PartyFlags | NONE, CAUTION, HIGH_RISK |
| Safety risk notes required | Boolean | PartyFlags | true/false |
| Safety risk last incident date | DateTime | PartyFlags | Date of last incident |
| Harassment sensitivity | Boolean | PartyFlags | Enforce reduced frequency and scripted comms |

### Legal/Dispute State

| Flag | Type | Location | Values |
|------|------|----------|--------|
| Dispute raised | Enum | PartyFlags | NONE, INFORMAL, FORMAL |
| Representation active | Boolean | PartyFlags | Has solicitor/advisor representing |
| Representation type | Enum | PartyProfile | NONE, SOLICITOR, ADVISOR, FAMILY_MEMBER, OTHER |
| Representation contact | JSON | PartyProfile | Name and contact details |
| Data restriction | Boolean | PartyFlags | Do not disclose to third parties |
| SAR in progress | Boolean | PartyFlags | SAR in progress (GDPR workflow) |

### Financial Behavior Patterns

| Flag | Type | Location | Values |
|------|------|----------|--------|
| Payment plan in place | Boolean | PartyFlags | true/false |
| Affordability review date | DateTime | PartyFlags | Next review date |
| Payment reliability score | Enum | PartyFlags (derived) | GOOD, MIXED, POOR |
| Multiple active debts | Boolean | PartyFlags (derived) | true/false |

### Fraud / Integrity Signals

| Flag | Type | Location | Values |
|------|------|----------|--------|
| Suspected fraud | Boolean | PartyFlags | true/false |
| Impersonation risk | Boolean | PartyFlags | true/false |
| Known scam reports | Boolean | PartyFlags | Debtor claims to have been targeted |

### Operational Constraints

| Flag | Type | Location | Values |
|------|------|----------|--------|
| Address uncertainty | Enum | PartyFlags | VERIFIED, NOT_VERIFIED, GONE_AWAY, TRACE_REQUIRED |
| Deceased | Boolean | PartyFlags | For individuals |
| Dissolved | Boolean | PartyFlags | For companies |
| Deceased/dissolved evidence level | Enum | PartyFlags | SELF_REPORTED, DOCUMENTED, OFFICIAL |

### Enforced Rules (PartyRestrictions)

| Flag | Type | Location | Values |
|------|------|----------|--------|
| Contact frequency limit | Enum | PartyRestrictions | NONE, REDUCED, MINIMAL, NONE_ALLOWED |
| Contact frequency limit reason | String | PartyRestrictions | Why limit is in place |
| Channel blocks | Array | PartyRestrictions | ["CALL", "SMS", "EMAIL", "LETTER", "VISIT"] |
| Require compliance approval | Boolean | PartyRestrictions | true/false |
| Compliance approval required for | Array | PartyRestrictions | ["VISITS", "LEGAL_ACTION", "ENFORCEMENT", "ALL"] |
| Restriction effective from | DateTime | PartyRestrictions | When restriction starts |
| Restriction effective to | DateTime | PartyRestrictions | When restriction ends (optional) |
| Restriction reason | Text | PartyRestrictions | Why restriction is in place |
| Restriction authorized by | FK | PartyRestrictions | User who authorized |

## Minimum "Must-Have" Set (Phase 1)

If implementing incrementally, prioritize these 8 essential flags:

### 1. Preferred language + interpreter required
- **Location**: PartyProfile
- **Fields**: `preferred_language`, `interpreter_required`

### 2. Preferred contact method + "no call"
- **Location**: PartyProfile + PartyFlags
- **Fields**: `preferred_contact_method`, `no_call`

### 3. Vulnerability indicator (category + review date)
- **Location**: PartyFlags
- **Fields**: `vulnerability_category`, `vulnerability_review_date`

### 4. Debt advice engaged + evidence level
- **Location**: PartySupportProfile
- **Fields**: `support_status`, `evidence_level`

### 5. Breathing Space / insolvency status
- **Location**: PartySupportProfile
- **Fields**: `breathing_space_status`, `insolvency_status`, `insolvency_start_date`, `insolvency_end_date`

### 6. Dispute raised
- **Location**: PartyFlags
- **Fields**: `dispute_status`

### 7. Safety risk + no-visit flag
- **Location**: PartyFlags
- **Fields**: `safety_risk`, `no_doorstep_visits`

### 8. Identity confidence + address verified
- **Location**: PartyProfile
- **Fields**: `identity_confidence`, `address_verified`

## Compliance Notes

**CRITICAL**: Detailed sensitive information should NOT be stored in free text fields in the main models.

**Use ComplianceNote model for**:
- Detailed vulnerability notes
- Safety incident details
- Dispute details
- Fraud investigation notes
- Compliance review notes
- Data protection notes

**ComplianceNote features**:
- Restricted permissions (compliance team only)
- Full audit trail (created_by, reviewed_by, reviewed_at)
- Categorization for searchability
- Evidence attachments
- Review workflow (review_required, review_date)

## Implementation Priority

### Phase 1: Essential Flags (8 flags)
Implement the minimum "must-have" set listed above.

### Phase 2: Contact and Conduct
- No doorstep visits
- Safety risk details
- Harassment sensitivity

### Phase 3: Legal and Dispute
- Representation details
- Data restrictions
- SAR tracking

### Phase 4: Financial Patterns
- Payment plan tracking
- Payment reliability scoring
- Multiple debts flag

### Phase 5: Fraud and Integrity
- Fraud indicators
- Impersonation risk
- Scam reports

### Phase 6: Operational Constraints
- Address uncertainty
- Deceased/dissolved status
- Trace requirements

### Phase 7: Restrictions and Rules
- Contact frequency limits
- Channel blocks
- Compliance approval requirements

## UI/UX Considerations

### Banner Display
Show prominent banners on case/debt screens when flags are active:
- "Vulnerability: Mental Health (review due: [date])"
- "Debt advice engaged: StepChange (confirmed)"
- "Safety risk: HIGH - No visits allowed"
- "Dispute: Formal - Refer to compliance"

### Quick Actions
Provide quick actions (permissioned):
- "Place hold on all open cases"
- "Place hold on this case only"
- "Request advisor confirmation"
- "Set review date"
- "Update vulnerability status"

### Compliance Notes Access
- Restricted to compliance team
- Show count badge: "3 compliance notes"
- Require permission to view details
- Full audit trail visible

## Automation Rules

### When Vulnerability Category Changes
1. Create CaseSupportImpact for all open cases
2. Apply policy:
   - Soft hold (stop outbound calls/visits)
   - Route to Compliance review
   - Restrict certain enforcement actions

### When Safety Risk = HIGH_RISK
1. Automatically set `no_doorstep_visits = true`
2. Block visit actions in UI
3. Require compliance approval for any visits
4. Show warning banner on all cases

### When Dispute Status = FORMAL
1. Set `require_compliance_approval = true`
2. Block enforcement actions
3. Show dispute banner
4. Route to compliance team

### When Debt Advice = ADVISOR_ENGAGED
1. Create CaseSupportImpact for all open cases
2. Apply contact frequency limits
3. Show debt advice banner
4. Enable quick actions for hold/restrictions

## Data Model Relationships

```
Party (1) ──< (1) PartyProfile
Party (1) ──< (1) PartyFlags
Party (1) ──< (1) PartyRestrictions
Party (1) ──< (1) PartySupportProfile
Party (1) ──< (*) ComplianceNote
Party (1) ──< (*) CaseSupportImpact
```

## Security and Permissions

### View Permissions
- **All users**: Can see PartyProfile, PartyFlags (summary)
- **Compliance team**: Can see all flags and ComplianceNotes
- **Regular users**: Cannot see detailed ComplianceNotes

### Edit Permissions
- **All users**: Can update PartyProfile (preferences)
- **Compliance team**: Can update all flags
- **Regular users**: Can update basic flags (with approval for sensitive ones)
- **Compliance team only**: Can create/edit ComplianceNotes

### Audit Trail
- All flag changes logged
- ComplianceNote access logged
- Restriction changes require authorization
- Review workflow tracked



