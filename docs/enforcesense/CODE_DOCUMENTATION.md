# Code Documentation Standards

This document defines the code documentation standards for the EnforceSense project, including JSDoc comments, inline documentation, and documentation requirements.

## Overview

All code in EnforceSense must be well-documented to ensure maintainability, clarity, and ease of collaboration. This document outlines the standards for:

- JSDoc comments for functions, classes, and interfaces
- Inline comments for complex logic
- Type documentation
- Business logic documentation
- Security and performance considerations

## JSDoc Standards

### Functions and Methods

Every public function or method MUST have JSDoc comments:

```typescript
/**
 * Creates a new user account in the system.
 * 
 * @param createUserDto - User creation data including email, password, and role
 * @param tenantId - The tenant ID to associate the user with
 * @returns Promise resolving to the created user object
 * @throws {ConflictException} If email already exists for the tenant
 * @throws {BadRequestException} If validation fails
 * 
 * @example
 * ```typescript
 * const user = await userService.create({
 *   email: 'user@example.com',
 *   password: 'SecurePassword123!',
 *   firstName: 'John',
 *   lastName: 'Doe',
 *   role: UserRole.CASE_MANAGER
 * }, tenantId);
 * ```
 */
async create(createUserDto: CreateUserDto, tenantId: string): Promise<User> {
  // Implementation
}
```

**Required Tags:**
- `@param` - For each parameter (name, type, description)
- `@returns` or `@return` - Return value description
- `@throws` or `@throws {ExceptionType}` - For exceptions that may be thrown

**Optional but Recommended:**
- `@example` - Code examples showing usage
- `@since` - Version when introduced
- `@deprecated` - If the function is deprecated

### Classes

Every class MUST have JSDoc comments:

```typescript
/**
 * Service for managing user accounts and authentication.
 * 
 * Handles user creation, updates, authentication, and authorization.
 * All operations are tenant-scoped for multi-tenant isolation.
 * 
 * @class UsersService
 */
@Injectable()
export class UsersService {
  // ...
}
```

**Required:**
- Class purpose and responsibility
- Important behaviors or constraints (e.g., tenant-scoping)

### Interfaces and Types

Document complex interfaces and types:

```typescript
/**
 * Configuration for paginated API responses.
 * 
 * @interface PaginationConfig
 */
export interface PaginationConfig {
  /** Current page number (1-indexed) */
  page: number;
  
  /** Number of items per page */
  limit: number;
  
  /** Total number of items available */
  total: number;
  
  /** Total number of pages */
  totalPages: number;
}
```

### Enums

Document enums with descriptions:

```typescript
/**
 * User roles within the EnforceSense platform.
 * 
 * @enum {string} UserRole
 */
export enum UserRole {
  /** Platform administrator with full system access */
  AGENCY_ADMIN = 'AGENCY_ADMIN',
  
  /** Case manager with case management permissions */
  CASE_MANAGER = 'CASE_MANAGER',
  
  /** Field agent with limited case access */
  AGENT = 'AGENT',
  
  /** Client user with read-only access to their cases */
  CLIENT_USER = 'CLIENT_USER',
  
  /** Debtor with self-service access */
  DEBTOR = 'DEBTOR',
  
  /** Compliance officer with audit and SAR access */
  COMPLIANCE_OFFICER = 'COMPLIANCE_OFFICER',
}
```

## Inline Documentation

### Complex Business Logic

Document complex business logic with inline comments:

```typescript
async calculateCaseBalance(caseId: string): Promise<Decimal> {
  // Get all transactions for the case, ordered by date
  const transactions = await this.prisma.caseTransaction.findMany({
    where: { caseId },
    orderBy: { createdAt: 'asc' },
  });

  let balance = new Decimal(0);

  // Process each transaction:
  // - Charges (PRINCIPAL, FEE, INTEREST, COST) increase balance
  // - Payments and refunds decrease balance
  for (const transaction of transactions) {
    if (this.isCharge(transaction.type)) {
      balance = balance.plus(transaction.amount);
    } else if (this.isPayment(transaction.type)) {
      balance = balance.minus(transaction.amount);
    }
  }

  return balance;
}
```

### Security Considerations

Document security-sensitive code:

```typescript
/**
 * Validates and hashes a user password.
 * 
 * SECURITY: Uses bcrypt with salt rounds of 10 to prevent rainbow table attacks.
 * Never log or return the plain password.
 * 
 * @param plainPassword - The plain text password to hash
 * @returns Promise resolving to the hashed password
 */
async hashPassword(plainPassword: string): Promise<string> {
  return bcrypt.hash(plainPassword, 10);
}
```

### Performance Optimizations

Document performance-critical code:

```typescript
/**
 * Retrieves cases with optimized query to prevent N+1 problem.
 * 
 * PERFORMANCE: Uses Prisma include to eagerly load related entities
 * (debtor, client, assignedUser) in a single query instead of
 * making separate queries for each case.
 * 
 * @param tenantId - Tenant ID to filter cases
 * @param filters - Optional filters for status, client, etc.
 * @returns Promise resolving to array of cases with related data
 */
async findCasesWithRelations(tenantId: string, filters?: CaseFilters): Promise<Case[]> {
  return this.prisma.case.findMany({
    where: { tenantId, ...filters },
    include: {
      debtor: true,
      clientOrganisation: true,
      assignedUser: {
        select: { id: true, firstName: true, lastName: true, email: true },
      },
    },
  });
}
```

### Multi-Tenant Isolation

Document tenant-scoping logic:

```typescript
/**
 * Retrieves a user by ID, ensuring tenant isolation.
 * 
 * TENANT ISOLATION: This method automatically filters by tenantId from
 * the authenticated user's JWT token. Users can only access resources
 * within their own tenant, preventing cross-tenant data access.
 * 
 * @param userId - User ID to retrieve
 * @param tenantId - Tenant ID from authenticated user (from JWT)
 * @returns Promise resolving to user if found and belongs to tenant
 * @throws {NotFoundException} If user not found or belongs to different tenant
 */
async findOne(userId: string, tenantId: string): Promise<User> {
  const user = await this.prisma.user.findFirst({
    where: { id: userId, tenantId },
  });

  if (!user) {
    throw new NotFoundException('User not found');
  }

  return user;
}
```

## Documentation Requirements by Component Type

### Services

- Document the service's responsibility and scope
- Document all public methods
- Document complex business logic
- Document tenant isolation behavior
- Document error handling

### Controllers

- Document the controller's purpose and resource it manages
- Document all endpoints (also covered by Swagger/OpenAPI)
- Document authentication/authorization requirements
- Document request/response formats

### DTOs

- Document the DTO's purpose
- Document each property (also covered by Swagger decorators)
- Document validation rules
- Document relationships to other entities

### Guards

- Document what the guard protects
- Document authentication/authorization logic
- Document error responses

### Interceptors

- Document what the interceptor does
- Document when it runs (before/after)
- Document side effects

### Pipes

- Document transformation/validation logic
- Document error handling

### Modules

- Document the module's purpose
- Document what it provides/exports
- Document dependencies

## Code Examples

### Well-Documented Service Method

```typescript
/**
 * Creates a new case and associates it with a debtor and client.
 * 
 * This method performs the following operations:
 * 1. Validates that debtor and client belong to the same tenant
 * 2. Generates a unique case reference number
 * 3. Creates the case record with initial status PENDING
 * 4. Creates initial case transaction for principal amount
 * 5. Creates audit log entry
 * 
 * @param createCaseDto - Case creation data
 * @param tenantId - Tenant ID from authenticated user
 * @returns Promise resolving to the created case with related entities
 * 
 * @throws {NotFoundException} If debtor or client not found
 * @throws {BadRequestException} If debtor/client belong to different tenant
 * @throws {ConflictException} If case reference already exists
 * 
 * @example
 * ```typescript
 * const case = await caseService.create({
 *   debtorId: 'debtor-uuid',
 *   clientOrganisationId: 'client-uuid',
 *   caseType: 'DEBT_RECOVERY',
 *   principalAmount: 1000.00
 * }, tenantId);
 * ```
 */
async create(createCaseDto: CreateCaseDto, tenantId: string): Promise<Case> {
  // Implementation with inline comments for complex steps
}
```

### Well-Documented Class

```typescript
/**
 * Service for managing debt enforcement cases.
 * 
 * Handles case lifecycle from creation to closure, including:
 * - Case creation and reference number generation
 * - Status transitions and workflow management
 * - Financial transaction recording
 * - Case assignment to agents/managers
 * - Balance calculations
 * 
 * All operations are tenant-scoped for multi-tenant isolation.
 * 
 * @class CasesService
 */
@Injectable()
export class CasesService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly auditService: AuditService,
  ) {}

  // Methods...
}
```

## Documentation Checklist

Before considering code complete:

- [ ] All public functions/methods have JSDoc comments
- [ ] All classes have JSDoc comments
- [ ] Complex interfaces/types are documented
- [ ] Complex business logic has inline comments
- [ ] Security-sensitive code is documented
- [ ] Performance optimizations are explained
- [ ] Multi-tenant isolation is documented where applicable
- [ ] Error handling is documented
- [ ] Examples provided for complex operations
- [ ] All parameters and return values documented

## Best Practices

1. **Write documentation as you code** - Don't leave it for later
2. **Keep documentation up-to-date** - Update when code changes
3. **Use clear, concise language** - Avoid jargon, be specific
4. **Document the "why" not just the "what"** - Explain reasoning
5. **Include examples** - Show how to use the code
6. **Document edge cases** - Explain unusual scenarios
7. **Document assumptions** - State what the code assumes
8. **Review documentation** - Check for clarity and completeness

## Related Documentation

- [API Documentation Guidelines](API_DOCUMENTATION.md) - Swagger/OpenAPI documentation
- [Agent Guidelines](AGENT_GUIDELINES.md) - Development workflow
- [Implementation Plan](IMPLEMENTATION_PLAN.md) - Architecture overview

---

**Last Updated**: 2025-12-11  
**Version**: 1.0

