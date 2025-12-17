# EnforceSense AI Integration Specification
**Version:** 1.0 (Initial)  
**Owner:** EnforceSense Platform Team  
**Scope:** AI capabilities, architecture, data model, APIs, UX, security, auditing, and rollout plan.

---

## 1. Goals

EnforceSense will integrate AI to:
- **Improve internal efficiency** (contact centre, case managers, field agents)
- **Improve client reporting and insight** (creditors/authorities)
- **Improve debtor experience** (clarity, multilingual, reduced confusion)
- **Improve compliance and risk controls** (tone checks, SAR assistance, audit narrative help)
- **Maintain strict governance**: auditable, non-blocking, tenant-scoped, prompt-versioned, and provider-pluggable

AI is an **assistive tool**, not an autonomous decision-maker. AI outputs must be explainable, reviewable, reversible, and logged.

---

## 2. Guiding Principles

1. **Non-blocking by default**: AI tasks run asynchronously using Celery-style background workers (Node + BullMQ/Redis)
2. **Prompt governance**: All prompts stored in AI prompt database, versioned with rollback capability
3. **Provider abstraction**: Support OpenAI and Microsoft/Azure OpenAI/Copilot-style APIs via unified interface
4. **Tenant isolation**: Data never crosses tenants. Provider keys may be global or per-tenant
5. **Least privilege**: Debtor-facing AI is more constrained than internal AI
6. **Immutable record**: Original notes/transcripts remain unchanged; AI produces derived artifacts
7. **Safety and compliance**: PII handling, encryption at rest for keys, audit logging for AI usage

---

## 3. AI Capability Map (Where AI Helps)

### 3.1 Internal Staff & Contact Centre

**A. Note Cleanup & Normalisation**
- **Problem**: Notes are rushed, inconsistent, emotional, badly formatted. Hard to read later. Risky for SARs, audits, and court disclosure.
- **AI Solution**: "Note Normalisation & Risk Sanitisation"
  - When an agent saves a note:
    - Raw note is stored unchanged (legal record)
    - AI runs asynchronously (worker) to produce:
      - Cleaned version
      - Neutral tone
      - Structured summary
      - Risk flags (language that could be problematic)
- **Example outputs**:
  - Cleaned note
  - Bullet-point summary
  - Risk flags (language that could be problematic)
- **Important**: Original note is never overwritten

**B. Call Summarisation (Voice → Text → Structured)**
- If telephony integration is added (or call transcripts uploaded):
  - AI can:
    - Summarise the call
    - Extract: promises made, payment intent, vulnerability indicators
    - Suggest: next actions, case status change
  - This becomes:
    - A structured case event
    - A searchable history
    - A compliance-safe summary

**C. Case Handover Summaries**
- When:
  - A case moves between agents
  - A manager reviews
  - A SAR is prepared
- AI can generate:
  - "Case so far" summary
  - Timeline highlights
  - Outstanding risks
- **Operational win**: No one has to read 50 notes anymore

**D. Field Agent Notes & Visit Outcomes**
- Field agents often write: "No answer. Looked occupied. Dog barking. Will revisit."
- AI can:
  - Standardise outcomes
  - Suggest correct visit result codes
  - Generate professional wording
  - Detect inconsistencies (e.g. GPS says visited, note says no access)

**E. Email Drafting**
- Draft internal/client communications with approved tone and templates

### 3.2 Client Value (Creditor / Authority)

**A. Client-Facing Case Summaries**
- Instead of dumping raw data, AI can generate:
  - Plain-English progress summaries
  - Weekly/monthly narrative reports
- **Example**: "This case is currently on arrangement. Three payments received on time. Risk of default is low."
- **Value**: Reduces client admin, makes service feel premium

**B. Instruction File / Import Error Explanation**
- When clients upload CSVs:
  - AI can explain why rows failed
  - Suggest corrections
  - Identify common data quality issues
- **Example**: "25% of rows failed due to missing postcode formatting. Recommend standardising before next upload."

**C. Performance Reporting Narrative**
- Weekly/monthly "executive summary" of KPIs

**D. Predictive Outcomes (Later Phase)**
- Over time, AI can identify which cases are likely to:
  - Pay quickly
  - Default
  - Escalate
- Clients get better forecasting and strategy

### 3.3 Debtor Experience (Constrained, Ethical)

**A. Plain-English Explanations**
- Debtors often don't understand: fees, enforcement stages, why something is happening
- AI can:
  - Explain their case in simple language
  - In their preferred language
  - Without threatening tone
- **Example**: "This fee was added because a visit was required after no response to earlier letters."
- **Reduces**: Complaints, calls, escalation

**B. Payment & Arrangement Guidance**
- AI can:
  - Explain payment options
  - Help debtors choose realistic arrangements
  - Warn gently if a plan is likely to fail
- **Important rule**: AI never decides. It explains options and consequences.

**C. Vulnerability Detection (Assistive, Not Decisive)**
- From: debtor-written text, contact centre notes, call transcripts
- AI can:
  - Flag possible vulnerability indicators
  - Prompt staff to review
- **⚠️ Critical**: AI does not label someone vulnerable on its own – it assists humans

**D. Multilingual Support**
- Generate multilingual explanations
- Translate debtor messages
- Maintain consistent tone across languages

### 3.4 Compliance, Risk & Legal Safety

**A. SAR Preparation & Summarisation**
- AI can:
  - Summarise large SAR packs
  - Highlight sensitive areas
  - Check for internal-only notes accidentally included
- Still human-reviewed, but much faster

**B. Risky Language Detection**
- AI scans: notes, messages, letters
- Flags:
  - Aggressive tone
  - Non-compliant wording
  - Emotional language that could look bad in court
- **Huge for risk management**

**C. Audit Trail Explanations**
- When auditors ask: "Why was this action taken?"
- AI can:
  - Reconstruct a narrative
  - Based on case history
  - Without altering facts

### 3.5 Platform & Management Intelligence

**A. Staff Performance Insights**
- AI can detect:
  - Which agents resolve cases fastest
  - Who escalates more
  - Training needs (e.g. frequent note rework)

**B. Process Optimisation**
- Across all tenants (anonymised):
  - Which workflows work best
  - Where cases stall
  - What improves recovery rates

**C. Prompt-Level Experimentation**
- Because prompts are versioned:
  - You can A/B test:
    - Note cleanup prompts
    - Debtor explanation styles
    - Client summary tone
- **This is rare and very powerful**

---

## 4. Architecture Overview

### 4.1 Components

**AI Orchestrator (in backend core)**
- Routes tasks to providers
- Loads prompt templates/versions
- Applies policy (role-based constraints)
- Logs usage and stores results

**AI Provider Adapter Layer**
- `OpenAIAdapter`
- `AzureOpenAIAdapter` (Copilot-style)
- Future adapters: Anthropic, local LLM, etc.

**Prompt Registry**
- DB-backed prompt templates + versions
- Provider/model/params configuration

**Background Workers**
- Consume AI jobs from Redis queues
- Produce results; notify via WebSockets / job status endpoints

**AI Results Store**
- Persist AI outputs tied to cases/notes/import jobs/SARs

### 4.2 Deployment

**Phase 1**: AI Orchestrator runs within `api-admin` (and optionally shared by other APIs). Workers run in a dedicated `worker` container.

**Later**: Extract a dedicated `ai-service` + `ai-worker` microservice.

### 4.3 How This Fits Existing Architecture

| Your Design Choice | Why it Matters |
|-------------------|----------------|
| Background workers | AI is slow → async |
| AI prompt database | Control, rollback, audit |
| Provider abstraction | Swap OpenAI ↔ Azure |
| Audit logging | AI usage traceability |
| Multi-API | Debtor AI ≠ Admin AI |
| Multilingual system | AI scales translations |
| Separate AI service (future) | Easy extraction |

---

## 5. Security, Privacy, and Data Handling

### 5.1 Key Management
- API keys stored encrypted at rest (DB encryption using KMS-like env key)
- Keys never returned to frontend
- Keys can be:
  - **Global** (platform-wide default provider)
  - **Per-tenant** (tenant-specific provider keys)

### 5.2 Data Minimisation
- Send only necessary fields to AI
- Use redaction when possible (e.g. remove full DOB, reduce addresses)
- For debtor-facing outputs, avoid exposing internal notes or staff names

### 5.3 Logging Rules
- Never log prompts with embedded secrets
- Log request metadata but avoid full PII
- Store AI inputs/outputs in DB with controlled access

### 5.4 Permissions
- AI admin functions restricted to `AGENCY_ADMIN` and `COMPLIANCE_OFFICER` (and platform roles where applicable)
- Debtor AI features are strictly scoped and rate-limited

---

## 6. Data Model (Prisma Schema Extensions)

### 6.1 Provider Configuration

```prisma
model GlobalAiProviderConfig {
  id          String   @id @default(uuid())
  providerName String  // 'openai', 'azure-openai'
  encryptedApiKey String // Encrypted at rest
  endpointUrl String?  // For Azure
  defaultModel String
  isActive    Boolean  @default(true)
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  @@unique([providerName])
}

// Reuse existing TenantIntegrationConfig for per-tenant keys
// Add providerName: 'openai', 'azure-openai', 'google-maps', 'companies-house', 'experian', etc.
```

### 6.2 Prompt Governance

```prisma
model PromptTemplate {
  id          String   @id @default(uuid())
  tenantId    String?  // Null = global template
  name        String   // Unique within tenant or global namespace
  description String?
  category    String   // 'notes', 'case-summary', 'debtor-help', 'imports', 'sar', 'risk'
  isActive    Boolean  @default(true)
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  versions    PromptVersion[]

  @@unique([tenantId, name])
}

model PromptVersion {
  id              String   @id @default(uuid())
  promptTemplateId String
  versionNumber   Int      // Incrementing
  providerName    String   // 'openai', 'azure-openai'
  model           String
  parametersJson  Json     // { temperature, maxTokens, jsonMode, etc. }
  promptText      String
  outputSchemaJson Json?   // Optional: JSON schema for structured outputs
  languageMode    String   // 'neutral', 'debtor_simple', 'client_formal', etc.
  createdByUserId String?
  createdAt       DateTime @default(now())
  isCurrent       Boolean  @default(false)

  template        PromptTemplate @relation(fields: [promptTemplateId], references: [id])
  tasks           AiTask[]

  @@unique([promptTemplateId, versionNumber])
  @@index([promptTemplateId, isCurrent])
}
```

**Rules:**
- Only ONE version is current per template
- Rollback = mark older version current

### 6.3 AI Tasks and Results

```prisma
model AiTask {
  id                String   @id @default(uuid())
  tenantId          String
  requestedByUserId String?
  apiSurface        String   // 'admin', 'client', 'debtor', 'agent', 'platform'
  taskType          String   // 'NOTE_CLEANUP', 'CASE_SUMMARY', 'IMPORT_ERROR_EXPLAIN', 'DEBTOR_EXPLAIN', 'SAR_SUMMARY', 'RISK_SCAN', etc.
  promptTemplateName String
  promptVersionId   String?
  providerName      String?
  model             String?
  status            String   // 'QUEUED', 'RUNNING', 'SUCCEEDED', 'FAILED', 'CANCELLED'
  inputRefType      String   // 'caseId', 'noteId', 'importJobId', 'sarId', etc.
  inputRefId        String
  languageCode      String?  // 'en', 'ro', etc.
  correlationId     String?  // Job ID from queue
  startedAt         DateTime?
  finishedAt        DateTime?
  errorMessage      String?

  promptVersion     PromptVersion? @relation(fields: [promptVersionId], references: [id])
  result            AiResult?

  createdAt         DateTime @default(now())
  updatedAt         DateTime @updatedAt

  @@index([tenantId, status])
  @@index([inputRefType, inputRefId])
  @@index([correlationId])
}

model AiResult {
  id            String   @id @default(uuid())
  tenantId      String
  aiTaskId      String   @unique
  outputType    String   // 'TEXT', 'JSON', 'MARKDOWN'
  outputText    String?  // Nullable if JSON
  outputJson    Json?    // Nullable if TEXT
  safetyFlagsJson Json?  // { toneRisk, complianceWarnings, etc. }
  createdAt     DateTime @default(now())

  task          AiTask   @relation(fields: [aiTaskId], references: [id], onDelete: Cascade)

  @@index([tenantId])
}
```

### 6.4 AI Audit Logging

Every AI task must produce an `AuditLog` entry:
- `action`: `AI_TASK_REQUESTED`, `AI_TASK_COMPLETED`, `AI_TASK_FAILED`
- `metadata`: `{ taskType, promptTemplate, promptVersion, provider, model, refType, refId }`

---

## 7. Queueing and Workers (Celery-style)

### 7.1 Queues

Use Redis-backed Bull/BullMQ queues:
- `ai-tasks` (general)
- Optionally split later:
  - `ai-notes`
  - `ai-sar`
  - `ai-imports`
  - `ai-debtor`

### 7.2 Job Lifecycle

1. API receives request → validates scope and permissions
2. Resolve tenant/provider configuration
3. Resolve prompt template + current version
4. Create `AiTask` row = `QUEUED`
5. Enqueue job with `aiTaskId`
6. Worker sets `RUNNING`, calls provider
7. Store `AiResult`, set `SUCCEEDED`/`FAILED`
8. Notify:
   - WebSocket event to tenant/user room
   - Job status endpoint is updated for polling
9. Audit log entries for request and completion

### 7.3 Non-blocking UI Patterns

- UI triggers action → receives `taskId`
- UI shows progress:
  - Poll `GET /ai/tasks/:id`
  - Or subscribe to WebSocket events

---

## 8. API Surface and Endpoints

### 8.1 Admin API (Primary)

**AI Settings**
- `GET /admin/ai/providers` - List configured providers
- `POST /admin/ai/providers` - Create/update provider config
- `GET /admin/ai/integrations` - Per-tenant provider credentials list
- `POST /admin/ai/integrations` - Set/update per-tenant keys

**Prompts**
- `GET /admin/ai/prompts` - List templates
- `POST /admin/ai/prompts` - Create template
- `GET /admin/ai/prompts/:templateId/versions` - List versions
- `POST /admin/ai/prompts/:templateId/versions` - Create new version
- `POST /admin/ai/prompts/:templateId/versions/:versionId/make-current` - Rollback/switch

**Tasks**
- `POST /admin/ai/tasks` - Request AI task
- `GET /admin/ai/tasks/:id` - Task status + result pointer
- `GET /admin/ai/tasks/:id/result` - Fetch result

**Convenience Endpoints**
- `POST /admin/ai/notes/:noteId/cleanup` - Trigger note cleanup
- `POST /admin/ai/cases/:caseId/summary` - Generate case handover summary
- `POST /admin/ai/imports/:importJobId/explain-errors` - Explain import errors

### 8.2 Client API (Constrained)

- `POST /client/ai/tasks` - Allowed types: case summary, report narrative, import explanation
- `GET /client/ai/tasks/:id` - Task status

### 8.3 Debtor API (Highly Constrained)

- `POST /debtor/ai/explain` - Allowed only for debtor-safe explanation
- Rate-limited and template-locked (no free prompt entry)
- Always language-aware and policy-checked

### 8.4 Agent API (Constrained)

- `POST /agent/ai/note-cleanup` - Clean up agent note
- `POST /agent/ai/visit-outcome` - Standardise visit outcome

---

## 9. WebSocket Events

Send WebSocket events to:
- `tenant:{tenantId}`
- Optionally `user:{userId}`

**Event names:**
- `ai.task.queued`
- `ai.task.progress`
- `ai.task.completed`
- `ai.task.failed`

**Payload:**
```json
{
  "taskId": "uuid",
  "taskType": "NOTE_CLEANUP",
  "refType": "noteId",
  "refId": "uuid",
  "status": "SUCCEEDED",
  "timestamp": "2025-01-01T00:00:00Z"
}
```

---

## 10. Admin UI Requirements

### 10.1 AI Settings Area

Add to `web-admin`:
- **Settings → AI Providers**
  - Choose provider: OpenAI / Azure OpenAI
  - Configure keys (masked)
  - Validate connection (non-destructive test)
- **Settings → Tenant Integrations**
  - Per-tenant key management for AI + other providers (Google Maps, Companies House, Experian)
  - Store encrypted, never displayed fully (masking)

### 10.2 Prompt Manager

- List prompt templates by category
- View versions, compare diffs (basic text compare)
- Create new version, set current, rollback
- Choose provider/model/params per version
- Show "where used" (task types or modules)

### 10.3 AI Task Viewer

- View recent AI tasks by status
- Filter by type, user, tenant, date
- Drill into result and flags

### 10.4 Integration Points

**Note Detail Page:**
- Show "AI Cleaned Version" tab (if available)
- Button: "Clean Note with AI" (triggers async task)

**Case Detail Page:**
- Button: "Generate Handover Summary" (triggers async task)
- Show summary when available

**Import Job Page:**
- Button: "Explain Errors with AI" (triggers async task)
- Show explanation when available

---

## 11. Debtor UX Requirements (Safety Constraints)

Debtor AI features must:
- Use only approved templates (no custom prompts)
- Use "debtor_simple" tone mode
- Avoid legal advice; provide general information and direct to support
- Never disclose internal notes or staff commentary
- Be multilingual via `languageCode` using i18n and/or AI generation in target language
- Rate-limited (e.g. max 10 requests per debtor per day)

---

## 12. Prompt Templates (Initial Set)

Create initial prompt templates (global) with versioned prompts:

### Notes

**`NOTE_CLEANUP_V1`**
- **Input**: `rawNote`, `context` (case status), `language`
- **Output**: `cleanedNote`, `bulletSummary`, `riskFlags`
- **Example prompt**:
```
You are a professional debt collection note normaliser. Clean the following note while preserving all factual information. Remove emotional language, standardise formatting, and flag any language that could be problematic in legal proceedings.

Raw note: {rawNote}
Case context: {context}

Output as JSON:
{
  "cleanedNote": "...",
  "bulletSummary": ["...", "..."],
  "riskFlags": ["..."]
}
```

### Case Management

**`CASE_HANDOVER_SUMMARY_V1`**
- **Input**: Last N notes/events, status timeline
- **Output**: Concise summary + next actions

### Imports

**`IMPORT_ERROR_EXPLAIN_V1`**
- **Input**: Validation errors + row samples
- **Output**: Human-readable explanation + suggested fixes

### Debtor

**`DEBTOR_CASE_EXPLAIN_V1`**
- **Input**: Fee breakdown, stage, next steps
- **Output**: Simple explanation in target language
- **Tone**: Neutral, helpful, non-threatening

### Compliance

**`RISK_LANGUAGE_SCAN_V1`**
- **Input**: Note/message text
- **Output**: Risk flags + safer wording suggestions

### SAR

**`SAR_PACK_SUMMARY_V1`**
- **Input**: List of entities included (not full data unless necessary)
- **Output**: Neutral summary and highlights

**All prompts must be stored in Prompt DB and versioned. No hardcoding in code except template names.**

---

## 13. Provider Support (OpenAI + Azure)

### 13.1 Provider Selection

Order of resolution:
1. Tenant-specific provider config if set and active
2. Global provider config if set and active
3. If none configured → return clear error prompting setup

### 13.2 Request Format

AI Orchestrator builds a provider-independent request:
- Prompt text
- Input variables
- Model & parameters
- Optional output schema

Adapters translate this into provider-specific calls.

### 13.3 Provider Adapter Interface

```typescript
interface AiProviderAdapter {
  generate(prompt: string, options: {
    model: string;
    temperature?: number;
    maxTokens?: number;
    jsonMode?: boolean;
    outputSchema?: JsonSchema;
  }): Promise<{
    text: string;
    json?: any;
    usage?: { promptTokens: number; completionTokens: number };
  }>;
}
```

---

## 14. Observability and Governance

### 14.1 Metrics

- AI tasks per minute, latency, failure rate per provider/model
- Cost estimation hooks (later)
- Per-tenant usage tracking

### 14.2 Alerts

- Spikes in failures
- Provider outages
- Unusual usage patterns

### 14.3 Audit

- Who requested AI
- What prompt version
- What output stored
- What entity was involved
- All stored in `AuditLog` table

---

## 15. Rollout Plan (Practical)

### Stage 1 (MVP AI) - Foundation

**Backend:**
- [ ] Implement AI Provider Config (global)
- [ ] Implement Prompt DB + versioning + rollback
- [ ] Implement AI queue + worker + task/result storage
- [ ] Implement provider adapters (OpenAI, Azure)
- [ ] Implement AI Orchestrator service
- [ ] Implement `NOTE_CLEANUP` and `CASE_HANDOVER_SUMMARY` task types
- [ ] Add audit logging for AI tasks

**Frontend:**
- [ ] Add Admin UI for provider keys (basic)
- [ ] Add Prompt Manager (basic)
- [ ] Add AI Task Viewer
- [ ] Integrate note cleanup into note detail page
- [ ] Integrate case summary into case detail page

**Testing:**
- [ ] Unit tests for adapters
- [ ] Integration tests for queue/worker
- [ ] E2E tests for note cleanup flow

### Stage 2 - Client & Risk Features

- [ ] Add client import error explanation
- [ ] Add client reporting narrative
- [ ] Add risk scan for notes/messages
- [ ] Add debtor explanation (heavily constrained)
- [ ] Add multilingual support for debtor AI

### Stage 3 - Advanced Features

- [ ] Extract AI into microservice (`ai-service` + `ai-worker`)
- [ ] Add advanced analytics
- [ ] Add A/B testing for prompts
- [ ] Add cost controls and budgeting
- [ ] Add predictive outcomes (case-level)

---

## 16. Non-Functional Requirements

- All AI interactions are asynchronous unless explicitly allowed for small tasks (< 2s)
- All AI results are stored with template/version/provider/model
- All AI outputs must be visible only to authorised roles
- Tenant-scoped storage and RBAC mandatory
- Keys encrypted at rest; never in logs
- Rate limiting per tenant/user for AI requests
- Timeout handling (default 30s, configurable per task type)

---

## 17. Golden Rules for AI in EnforceSense

1. **AI assists, never decides** (especially for debtors & compliance)
2. **Original data is immutable** (AI produces derived artifacts)
3. **AI output is tagged** with prompt + version
4. **Human override is always possible**
5. **Different AI policies per API**:
   - Debtor AI = very constrained
   - Admin AI = powerful but logged
6. **All AI usage is audited**
7. **Prompts are versioned and rollback-able**
8. **Provider abstraction allows switching without code changes**

---

## 18. Mandatory Enforcement Rules for AI Development Agent

When implementing any AI feature, the AI dev agent MUST:

1. ✅ Store prompts in Prompt DB and use template+version resolution
2. ✅ Run heavy AI tasks via queue/worker (non-blocking)
3. ✅ Log AI usage to AuditLog with prompt version and entity reference
4. ✅ Store results in AiResult; never overwrite original user-entered records
5. ✅ Apply tenant isolation and least privilege per API surface
6. ✅ Ensure debtor-facing AI is template-locked, rate-limited, and safe
7. ✅ Encrypt provider keys at rest
8. ✅ Handle errors gracefully (provider failures, timeouts, invalid responses)
9. ✅ Add appropriate RBAC checks for AI endpoints
10. ✅ Include audit logging for all AI operations

---

## 19. Future Considerations

- **Local LLM support** (e.g. Ollama, self-hosted models)
- **Cost optimization** (model selection based on task complexity)
- **A/B testing framework** for prompt versions
- **AI-powered case routing** (intelligent assignment)
- **Voice-to-text integration** for call transcripts
- **Image analysis** (e.g. document verification, field visit photos)
- **Predictive analytics** (recovery probability, default risk)

---

## 20. References

- Background Workers Specification: See `docs/IMPLEMENTATION_PLAN.md` section 5.4
- Multi-tenant Architecture: See `docs/IMPLEMENTATION_PLAN.md` section 2
- Audit Logging: See existing `AuditLog` model in Prisma schema
- Queue System: BullMQ/Redis (see implementation plan)

---

**Document Status**: Ready for implementation  
**Last Updated**: 2025-01-13  
**Next Review**: After Stage 1 completion


