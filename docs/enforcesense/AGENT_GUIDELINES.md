# AI Agent Development Guidelines

> ⚠️ **IMPORTANT**: If you haven't read [AGENTS_START_HERE.md](AGENTS_START_HERE.md) yet, **STOP** and read it first!

This document provides guidelines for AI agents working on the EnforceSense project to ensure consistency, collaboration, and proper task management.

## 🤖 For All AI Agents

### Mandatory Rules

1. **ALWAYS check and update the TODO list** before and after any work
2. **Use the `todo_write` tool** to manage task status
3. **Keep `docs/DEVELOPMENT_TODO.md` synchronized** with tool-based TODOs
4. **Only work on ONE task at a time** (mark others as pending)
5. **Update immediately** when task status changes

## 📋 TODO List Management

### Before Starting Work

```typescript
// 1. Check existing TODOs
// Review docs/DEVELOPMENT_TODO.md

// 2. Mark task as in_progress
todo_write({
  merge: true,
  todos: [{ 
    id: 'dev-1', 
    status: 'in_progress',
    content: 'Database setup - Run Prisma migrations, verify schema, seed initial data'
  }]
})

// 3. Update markdown file
// Change [ ] to [🚧] in docs/DEVELOPMENT_TODO.md
```

### During Work

- If you discover a new requirement → Add it as a new task
- If you encounter a blocker → Add notes or create a blocker task
- If task scope changes → Update the task description

### After Completing Work

```typescript
// 1. Mark task as completed
todo_write({
  merge: true,
  todos: [{ 
    id: 'dev-1', 
    status: 'completed'
  }]
})

// 2. Update markdown file
// Change [🚧] to [x] in docs/DEVELOPMENT_TODO.md
// Add completion date: [x] (2025-12-11)

// 3. Add any follow-up tasks discovered
if (followUpTasks.length > 0) {
  todo_write({
    merge: true,
    todos: followUpTasks.map(task => ({
      id: `dev-${nextId++}`,
      status: 'pending',
      content: task
    }))
  })
}
```

## 🔄 Task Status Workflow

```
pending → in_progress → completed
   ↓           ↓
cancelled   blocked (add notes)
```

### Status Definitions

- **pending**: Task is defined but not started
- **in_progress**: Currently being worked on (only ONE per agent)
- **completed**: Task is finished and verified
- **cancelled**: Task is no longer needed

## 📝 Code Standards

### File Organization

- Follow existing project structure
- Use TypeScript for all new code
- Follow NestJS conventions for APIs
- Follow React conventions for frontends

### Naming Conventions

- **Files**: kebab-case (e.g., `user-service.ts`)
- **Classes**: PascalCase (e.g., `UserService`)
- **Functions/Variables**: camelCase (e.g., `getUserById`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_RETRY_COUNT`)

### Documentation

**MANDATORY Documentation Requirements:**

1. **API Documentation (Swagger/OpenAPI)**:
   - All controllers MUST have `@ApiTags()` decorator
   - All endpoints MUST have `@ApiOperation()` with summary
   - All endpoints MUST have `@ApiResponse()` for all status codes
   - All DTOs MUST have `@ApiProperty()` on all properties
   - All authenticated endpoints MUST have `@ApiBearerAuth()`
   - See [API Documentation Guidelines](API_DOCUMENTATION.md) for complete standards

2. **Code Documentation (JSDoc)**:
   - All public functions/methods MUST have JSDoc comments
   - All classes MUST have JSDoc comments
   - Document parameters, return values, and exceptions
   - Include examples for complex operations
   - See [Code Documentation Standards](CODE_DOCUMENTATION.md) for complete standards

3. **Inline Documentation**:
   - Document complex business logic
   - Document security considerations
   - Document performance optimizations
   - Document multi-tenant isolation logic

4. **Documentation Updates**:
   - Update README if adding major features
   - Update relevant docs in `/docs` folder
   - Keep Swagger documentation synchronized with code

## 🔒 Security Guidelines

- **Never commit secrets** (API keys, passwords, tokens)
- **Validate all inputs** (use DTOs in NestJS)
- **Use parameterized queries** (Prisma handles this)
- **Implement proper authentication** before adding features
- **Follow principle of least privilege** for permissions

## 🧪 Testing Requirements

- Write unit tests for services
- Write integration tests for API endpoints
- Test error cases, not just happy paths
- Update tests when modifying code

## 📦 Dependency Management

- Use `pnpm` (not npm or yarn)
- Add dependencies to correct workspace
- Update `pnpm-lock.yaml` by running `pnpm install`
- Check for security vulnerabilities: `pnpm audit`

## 🐳 Docker-First Development (MANDATORY)

**⚠️ CRITICAL: This project uses Docker-ONLY development. Local development is NOT supported.**

### Mandatory Rules

1. **NEVER run services locally** - Always use Docker
2. **ALWAYS rebuild containers** after code changes
3. **ALWAYS test via Docker** - Access services on `localhost` ports
4. **ALWAYS commit before testing** - Rebuild requires committed code (or use volume mounts)

### Development Workflow

```bash
# 1. Make code changes
# Edit files in your editor

# 2. Commit changes (or use volume mounts for live reload)
git add .
git commit -m "feat: Add new feature"

# 3. Rebuild and restart service
docker-compose -f infra/docker/docker-compose.yml -p enforcesense up -d --build <service-name>

# 4. Test in browser
# Access: http://localhost:<port>

# 5. Check logs if needed
docker-compose -f infra/docker/docker-compose.yml -p enforcesense logs -f <service-name>
```

### Rebuilding Services

**After ANY code change, rebuild the affected service:**

- **API changes**: Rebuild the specific API container
  ```bash
  docker-compose -f infra/docker/docker-compose.yml -p enforcesense up -d --build api-platform
  ```

- **Frontend changes**: Rebuild the specific frontend container
  ```bash
  docker-compose -f infra/docker/docker-compose.yml -p enforcesense up -d --build web-platform
  ```

- **Shared package changes**: Rebuild all services that use it
  ```bash
  docker-compose -f infra/docker/docker-compose.yml -p enforcesense up -d --build
  ```

### Testing Checklist

Before considering work complete:
- [ ] Code committed to git (or using volume mounts)
- [ ] Docker container rebuilt
- [ ] Service starts without errors (check logs)
- [ ] Feature tested via browser at `localhost:<port>`
- [ ] No errors in Docker logs

## 🔄 Version Management

- **Never manually update version** - use `pnpm release` script
- Version is managed in:
  - `package.json` (root)
  - `packages/config/src/version.ts`
- Both must stay in sync

## 📚 Documentation Updates

When adding features, update:

1. **API Documentation**: 
   - Add Swagger/OpenAPI decorators to all endpoints
   - Document all DTOs with `@ApiProperty()`
   - Document all response types
   - See [API Documentation Guidelines](API_DOCUMENTATION.md)
2. **Code Documentation**:
   - Add JSDoc comments to all public functions/classes
   - Document complex business logic
   - See [Code Documentation Standards](CODE_DOCUMENTATION.md)
3. **README.md**: Update if adding major features
4. **DEVELOPMENT_TODO.md**: Mark tasks complete
5. **Relevant docs**: Update architecture/implementation docs

## 🚫 What NOT to Do

- ❌ Don't work on multiple tasks simultaneously
- ❌ Don't skip TODO list updates
- ❌ Don't commit without updating related docs
- ❌ Don't modify version numbers manually
- ❌ Don't commit secrets or credentials
- ❌ Don't break existing functionality without discussion
- ❌ Don't create duplicate tasks

## ✅ Best Practices

- ✅ Check TODO list first
- ✅ Mark task in_progress before starting
- ✅ Commit frequently with clear messages
- ✅ Update docs as you code
- ✅ Test your changes
- ✅ Mark task completed when done
- ✅ Add follow-up tasks if discovered

## 🔍 Code Review Checklist

Before considering work complete:

- [ ] Task marked as completed in TODO list
- [ ] Code follows project conventions
- [ ] Tests written and passing
- [ ] **API Documentation**: All endpoints have Swagger decorators
- [ ] **Code Documentation**: All public functions have JSDoc comments
- [ ] **Swagger UI**: Documentation accessible and displays correctly
- [ ] No secrets committed
- [ ] Docker builds successfully
- [ ] Version numbers unchanged (unless intentional release)

## 📞 Collaboration

### Working with Multiple Agents

1. **Check TODO list** for tasks marked `in_progress`
2. **Avoid conflicts** - don't start tasks others are working on
3. **Communicate via commits** - use clear commit messages
4. **Update TODO immediately** when status changes
5. **Pull latest changes** before starting new work

### Conflict Resolution

If two agents work on the same task:

1. Check git history for recent commits
2. Review TODO list for current status
3. Coordinate via commit messages or documentation
4. Merge changes carefully
5. Update TODO list to reflect resolution

## 🎯 Priority Guidelines

Work in this order:

1. **Phase 1 (Foundation)** - Database, Auth, Users
2. **Phase 2 (Core Logic)** - Cases, Debtors, Payments
3. **Phase 3 (APIs)** - Endpoint implementation
4. **Phase 4 (Frontend)** - UI development
5. **Phase 5 (Security)** - Hardening
6. **Phase 6 (Infrastructure)** - Integration
7. **Phase 7 (Testing)** - Test coverage
8. **Phase 8 (Reporting)** - Analytics
9. **Phase 9 (Deployment)** - CI/CD

## 📖 Additional Resources

- [Development TODO List](DEVELOPMENT_TODO.md) - Current task list
- [Implementation Plan](IMPLEMENTATION_PLAN.md) - Architecture details
- [Setup Guide](SETUP_GUIDE.md) - Environment setup
- [Version Management](VERSION_MANAGEMENT.md) - Version control
- [API Documentation Guidelines](API_DOCUMENTATION.md) - **REQUIRED** - Swagger/OpenAPI standards
- [Code Documentation Standards](CODE_DOCUMENTATION.md) - **REQUIRED** - JSDoc and inline documentation standards

---

**Remember**: The TODO list is the single source of truth for what needs to be done. Keep it updated!

