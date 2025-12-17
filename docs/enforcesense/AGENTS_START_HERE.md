# 🤖 AI Agents - START HERE

**If you are an AI agent working on this project, READ THIS FIRST.**

## 📋 Quick Start Checklist

1. ✅ **Read this document** (you're here!)
2. ✅ **Read [AGENT_GUIDELINES.md](AGENT_GUIDELINES.md)** - Mandatory rules and workflows
3. ✅ **Check [DEVELOPMENT_TODO.md](DEVELOPMENT_TODO.md)** - Current task list
4. ✅ **Review [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)** - Architecture overview

## 🐳 CRITICAL: Docker-First Development

**⚠️ IMPORTANT: ALL DEVELOPMENT AND TESTING MUST BE DONE IN DOCKER**

- ❌ **DO NOT** run `pnpm dev` locally
- ❌ **DO NOT** run `npm start` locally  
- ❌ **DO NOT** test applications outside Docker
- ✅ **ALWAYS** rebuild Docker containers to test changes
- ✅ **ALWAYS** test via Docker Compose
- ✅ **ALWAYS** access services via `127.0.0.2` ports (6300-6314)

### Development Workflow

1. **Make code changes** in your editor
2. **Commit changes** to git
3. **Rebuild Docker containers**: `docker-compose -f infra/docker/docker-compose.yml -p enforcesense up -d --build <service-name>`
4. **Test in browser**: Access via `http://localhost:<port>`
5. **Check logs**: `docker-compose -f infra/docker/docker-compose.yml -p enforcesense logs <service-name>`

### Why Docker-Only?

- Ensures consistent environment across all developers
- Matches production deployment environment
- Includes all dependencies and services (PostgreSQL, Redis, etc.)
- Prevents local environment configuration issues

## 🎯 Your First Steps

### Step 1: Understand the Project
- **Project**: EnforceSense - Debt enforcement management platform
- **Architecture**: Multi-API monorepo (5 APIs + 4 frontends)
- **Tech Stack**: NestJS (backend), React + Vite (frontend), PostgreSQL, Redis, MinIO
- **Current Version**: 0.0.2
- **Development**: Docker-only (no local development)

### Operational context (read before building features)
- [UK Debt Collection & Enforcement — End-to-End Operating Process](UK_DEBT_ENFORCEMENT_END_TO_END.md)
- [CRM, Sales & Client Management Module (Spec)](CRM_SALES_CLIENT_MANAGEMENT.md)

### Step 2: Check Current Status
```bash
# Check TODO list for current tasks
# File: docs/DEVELOPMENT_TODO.md

# Check what's in progress
# Use: todo_write tool to see current state
```

### Step 3: Before Starting Any Work

**MANDATORY:**
1. Read [AGENT_GUIDELINES.md](AGENT_GUIDELINES.md) completely
2. Check [DEVELOPMENT_TODO.md](DEVELOPMENT_TODO.md) for existing tasks
3. Verify no other agent is working on your chosen task
4. Mark task as `in_progress` using `todo_write` tool
5. Update markdown TODO list: `[ ]` → `[🚧]`

### Step 4: During Work
- Follow code standards from AGENT_GUIDELINES.md
- Update TODO list if you discover new requirements
- Commit frequently with clear messages
- Keep documentation updated

### Step 5: After Completing Work
1. Mark task as `completed` using `todo_write` tool
2. Update markdown TODO list: `[🚧]` → `[x]`
3. Add completion date
4. Commit both code and TODO updates together

## 📚 Essential Documents (Read in Order)

### 1. [AGENT_GUIDELINES.md](AGENT_GUIDELINES.md) ⭐ **REQUIRED**
**Read this FIRST before doing anything!**
- Mandatory rules for all agents
- TODO list management workflow
- Code standards
- Security guidelines
- Collaboration rules

### 2. [DEVELOPMENT_TODO.md](DEVELOPMENT_TODO.md) ⭐ **REQUIRED**
**Check this before starting any task!**
- Current task list with status
- What needs to be done
- What's in progress
- What's completed

### 3. [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)
**Understand the architecture:**
- Multi-API architecture
- Security requirements
- Deployment strategy
- Development guidelines

### 4. [SETUP_GUIDE.md](SETUP_GUIDE.md)
**If you need to set up the environment:**
- Prerequisites
- Installation steps
- Docker setup
- Environment configuration

### 5. [VERSION_MANAGEMENT.md](VERSION_MANAGEMENT.md)
**If working with versions:**
- Version numbering system
- How to update versions
- GitHub release process

## 🚨 Critical Rules (Don't Skip!)

1. **ALWAYS update TODO list** before and after work
2. **ONLY ONE task in_progress** per agent at a time
3. **Use `todo_write` tool** for status changes
4. **Keep markdown synchronized** with tool-based TODOs
5. **Never commit secrets** or credentials
6. **Follow code standards** from AGENT_GUIDELINES.md

## 📌 Reference Repo: CCS Quote Tool v2 (Reference-Only — DO NOT MODIFY)

CCS Quote Tool v2 is a separate CRM system where we use AI to:
- research/enrich **companies** (e.g., Companies House),
- improve what call-center operators type into notes (AI cleanup/rewrites).

This can be a **useful reference** for EnforceSense, especially where **debtors are companies** and we want AI-driven research/enrichment patterns. You are allowed to improve prompts/code **in EnforceSense** as needed, but:

**Hard rule:**
- You may **reference/read** CCS Quote Tool v2, but you must **NOT change** its code or prompts.
- Do not commit to it, do not refactor it, and do not “quick fix” anything in that repo/folder.

**Where to find it:**
- **Preferred local path (Windows)**: `C:\Users\david\Documents\CCS quote tool\CCS Quote Tool v2`
- **GitHub (reference only)**: [`dje115/ccs-quote-tool-v2`](https://github.com/dje115/ccs-quote-tool-v2)

**If the local folder is not present:**
- You may clone it locally for reference **only** into `..\ccs-quote-tool-v2` (adjacent to this repo).
- Do **not** add it as a git submodule or dependency.
- Do **not** import runtime code from it into EnforceSense.

Example:

```bash
git clone https://github.com/dje115/ccs-quote-tool-v2 ..\ccs-quote-tool-v2
```

## 🔄 Task Workflow (Copy This)

```typescript
// 1. BEFORE STARTING
// Read: AGENT_GUIDELINES.md
// Check: DEVELOPMENT_TODO.md
// Verify: No conflicts with other agents

// 2. MARK TASK IN PROGRESS
todo_write({
  merge: true,
  todos: [{ 
    id: 'dev-1', 
    status: 'in_progress' 
  }]
})

// 3. UPDATE MARKDOWN
// Change [ ] to [🚧] in DEVELOPMENT_TODO.md

// 4. DO THE WORK
// Follow guidelines, update docs, test code

// 5. MARK COMPLETED
todo_write({
  merge: true,
  todos: [{ 
    id: 'dev-1', 
    status: 'completed' 
  }]
})

// 6. UPDATE MARKDOWN
// Change [🚧] to [x] in DEVELOPMENT_TODO.md
// Add completion date

// 7. COMMIT
// Commit code + TODO updates together
```

## 📖 Additional Resources

- [Docker Setup Guide](DOCKER_SETUP.md) - Docker configuration
- [Development Services](DEV_SERVICES.md) - Port mappings and services
- [Environment Variables](ENV_EXAMPLE_CONTENT.md) - Environment config

## ❓ Common Questions

**Q: Which task should I work on?**  
A: Check DEVELOPMENT_TODO.md, start with Phase 1 tasks, pick one marked `[ ]` (pending).

**Q: Can I work on multiple tasks?**  
A: No. Only ONE task should be `in_progress` per agent at a time.

**Q: How do I update the TODO list?**  
A: Use `todo_write` tool AND update the markdown file. Both must stay in sync.

**Q: What if I discover a new requirement?**  
A: Add it as a new task to DEVELOPMENT_TODO.md and use `todo_write` to track it.

**Q: Can I skip reading AGENT_GUIDELINES.md?**  
A: **NO.** It contains mandatory rules you must follow.

## 🎯 Current Development Phase

**Phase 1: Foundation** (Priority 1)
- Database setup
- Authentication system
- User management

Start here if you're beginning development!

---

**Remember**: 
- ✅ Read AGENT_GUIDELINES.md first
- ✅ Check TODO list before starting
- ✅ Update TODO list immediately
- ✅ Follow all rules and standards

**Last Updated**: 2025-12-11


