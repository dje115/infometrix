# API Documentation Guidelines

This document provides guidelines for documenting EnforceSense API endpoints using Swagger/OpenAPI decorators.

## Overview

All EnforceSense API services use Swagger/OpenAPI for API documentation. Documentation is accessible at `/docs` for each API service:

- **Platform API**: http://localhost:4310/docs
- **Admin API**: http://localhost:4311/docs
- **Client API**: http://localhost:4312/docs
- **Debtor API**: http://localhost:4313/docs
- **Agent API**: http://localhost:4314/docs

## Required Decorators

### Controllers

Every controller MUST have:

```typescript
@ApiTags('ResourceName')
@Controller('resource')
export class ResourceController {
  // ...
}
```

**Guidelines:**
- Use plural, PascalCase for tag names (e.g., `'Users'`, `'Cases'`, `'Payments'`)
- Tag names should match the resource name
- Group related endpoints under the same tag

### Endpoints

Every endpoint MUST have:

```typescript
@ApiOperation({ 
  summary: 'Brief description of what the endpoint does',
  description: 'Detailed description (optional but recommended for complex operations)'
})
@ApiResponse({ 
  status: 200, 
  description: 'Success response description',
  type: ResponseDto 
})
@ApiResponse({ 
  status: 400, 
  description: 'Bad request - validation error or invalid input' 
})
@ApiResponse({ 
  status: 401, 
  description: 'Unauthorized - authentication required' 
})
@ApiResponse({ 
  status: 403, 
  description: 'Forbidden - insufficient permissions' 
})
@ApiResponse({ 
  status: 404, 
  description: 'Resource not found' 
})
@Get(':id')
async getResource(@Param('id') id: string) {
  // ...
}
```

**Guidelines:**
- Always include a `summary` - keep it concise (one sentence)
- Include `description` for complex operations
- Document all possible HTTP status codes
- Use appropriate response DTOs with `type` property

### Authentication

For endpoints requiring authentication:

```typescript
@ApiBearerAuth('JWT-auth')
@UseGuards(JwtAuthGuard)
@Get('protected')
async getProtectedResource() {
  // ...
}
```

**Guidelines:**
- Use `@ApiBearerAuth('JWT-auth')` for JWT-protected endpoints
- Document authentication requirements in the operation description if needed

### DTOs (Data Transfer Objects)

Every DTO property MUST have:

```typescript
export class CreateUserDto {
  @ApiProperty({ 
    description: 'User email address',
    example: 'user@example.com',
    format: 'email'
  })
  @IsEmail()
  email: string;

  @ApiProperty({ 
    description: 'User first name',
    example: 'John',
    minLength: 1,
    maxLength: 50
  })
  @IsString()
  @MinLength(1)
  @MaxLength(50)
  firstName: string;

  @ApiProperty({ 
    description: 'User role',
    enum: UserRole,
    example: UserRole.AGENCY_ADMIN
  })
  @IsEnum(UserRole)
  role: UserRole;
}
```

**Guidelines:**
- Always include `description` - explain what the property represents
- Include `example` values - use realistic, non-sensitive data
- Include validation constraints (`minLength`, `maxLength`, `format`, etc.)
- Document enums with `enum` property
- Use `required: false` for optional properties
- For nested objects, use `type` property

### Query Parameters

```typescript
@ApiQuery({ 
  name: 'page', 
  required: false, 
  type: Number, 
  description: 'Page number (default: 1)',
  example: 1
})
@ApiQuery({ 
  name: 'limit', 
  required: false, 
  type: Number, 
  description: 'Items per page (default: 10)',
  example: 10
})
@Get()
async getResources(@Query('page') page?: number) {
  // ...
}
```

### Path Parameters

```typescript
@ApiParam({ 
  name: 'id', 
  description: 'User unique identifier',
  type: String,
  example: '123e4567-e89b-12d3-a456-426614174000'
})
@Get(':id')
async getUser(@Param('id') id: string) {
  // ...
}
```

### Request Bodies

```typescript
@ApiBody({ 
  type: CreateUserDto,
  description: 'User creation data'
})
@Post()
async createUser(@Body() createUserDto: CreateUserDto) {
  // ...
}
```

## Documentation Examples

### Complete Controller Example

```typescript
import { Controller, Get, Post, Body, Param, Query } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiBearerAuth, ApiQuery, ApiParam } from '@nestjs/swagger';
import { UsersService } from './users.service';
import { CreateUserDto } from './dto/create-user.dto';
import { UserResponseDto } from './dto/user-response.dto';

@ApiTags('Users')
@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @ApiOperation({ 
    summary: 'Create a new user',
    description: 'Creates a new user account with the provided information. Requires AGENCY_ADMIN role.'
  })
  @ApiResponse({ 
    status: 201, 
    description: 'User successfully created',
    type: UserResponseDto
  })
  @ApiResponse({ 
    status: 400, 
    description: 'Invalid input data' 
  })
  @ApiResponse({ 
    status: 401, 
    description: 'Unauthorized - authentication required' 
  })
  @ApiResponse({ 
    status: 403, 
    description: 'Forbidden - insufficient permissions' 
  })
  @ApiBearerAuth('JWT-auth')
  @Post()
  async create(@Body() createUserDto: CreateUserDto): Promise<UserResponseDto> {
    return this.usersService.create(createUserDto);
  }

  @ApiOperation({ 
    summary: 'Get user by ID',
    description: 'Retrieves a single user by their unique identifier'
  })
  @ApiParam({ 
    name: 'id', 
    description: 'User unique identifier (UUID)',
    type: String,
    example: '123e4567-e89b-12d3-a456-426614174000'
  })
  @ApiResponse({ 
    status: 200, 
    description: 'User found',
    type: UserResponseDto
  })
  @ApiResponse({ 
    status: 404, 
    description: 'User not found' 
  })
  @ApiBearerAuth('JWT-auth')
  @Get(':id')
  async findOne(@Param('id') id: string): Promise<UserResponseDto> {
    return this.usersService.findOne(id);
  }

  @ApiOperation({ 
    summary: 'List all users',
    description: 'Retrieves a paginated list of users with optional filtering'
  })
  @ApiQuery({ 
    name: 'page', 
    required: false, 
    type: Number, 
    description: 'Page number (default: 1)',
    example: 1
  })
  @ApiQuery({ 
    name: 'limit', 
    required: false, 
    type: Number, 
    description: 'Items per page (default: 10, max: 100)',
    example: 10
  })
  @ApiResponse({ 
    status: 200, 
    description: 'List of users',
    type: [UserResponseDto]
  })
  @ApiBearerAuth('JWT-auth')
  @Get()
  async findAll(
    @Query('page') page?: number,
    @Query('limit') limit?: number
  ): Promise<UserResponseDto[]> {
    return this.usersService.findAll(page, limit);
  }
}
```

### DTO Example

```typescript
import { ApiProperty } from '@nestjs/swagger';
import { IsEmail, IsString, MinLength, MaxLength, IsEnum, IsOptional } from 'class-validator';
import { UserRole } from '@prisma/client';

export class CreateUserDto {
  @ApiProperty({ 
    description: 'User email address (must be unique within tenant)',
    example: 'user@example.com',
    format: 'email'
  })
  @IsEmail()
  email: string;

  @ApiProperty({ 
    description: 'User password (minimum 8 characters)',
    example: 'SecurePassword123!',
    minLength: 8
  })
  @IsString()
  @MinLength(8)
  password: string;

  @ApiProperty({ 
    description: 'User first name',
    example: 'John',
    minLength: 1,
    maxLength: 50
  })
  @IsString()
  @MinLength(1)
  @MaxLength(50)
  firstName: string;

  @ApiProperty({ 
    description: 'User last name',
    example: 'Doe',
    minLength: 1,
    maxLength: 50
  })
  @IsString()
  @MinLength(1)
  @MaxLength(50)
  lastName: string;

  @ApiProperty({ 
    description: 'User role within the tenant',
    enum: UserRole,
    example: UserRole.CASE_MANAGER
  })
  @IsEnum(UserRole)
  role: UserRole;
}

export class UserResponseDto {
  @ApiProperty({ 
    description: 'User unique identifier',
    example: '123e4567-e89b-12d3-a456-426614174000'
  })
  id: string;

  @ApiProperty({ 
    description: 'User email address',
    example: 'user@example.com'
  })
  email: string;

  @ApiProperty({ 
    description: 'User first name',
    example: 'John'
  })
  firstName: string;

  @ApiProperty({ 
    description: 'User last name',
    example: 'Doe'
  })
  lastName: string;

  @ApiProperty({ 
    description: 'User role',
    enum: UserRole,
    example: UserRole.CASE_MANAGER
  })
  role: UserRole;

  @ApiProperty({ 
    description: 'Whether the user account is active',
    example: true
  })
  isActive: boolean;

  @ApiProperty({ 
    description: 'Account creation timestamp',
    example: '2025-12-11T10:00:00Z'
  })
  createdAt: Date;
}
```

## Best Practices

1. **Keep descriptions clear and concise** - Use plain language, avoid jargon
2. **Always include examples** - Help developers understand expected values
3. **Document all error cases** - Include all possible HTTP status codes
4. **Use consistent naming** - Follow the same patterns across all APIs
5. **Update documentation with code** - Don't let documentation become outdated
6. **Test your documentation** - Verify Swagger UI displays correctly
7. **Use appropriate response types** - Always specify response DTO types
8. **Document authentication requirements** - Clearly indicate which endpoints require auth

## Multi-Tenant Considerations

When documenting endpoints that operate on tenant-scoped resources:

- Document that operations are automatically scoped to the authenticated user's tenant
- Do not expose tenant IDs in path parameters (use JWT token instead)
- Document tenant isolation in operation descriptions when relevant

## Security Documentation

For sensitive operations:

- Clearly document authentication requirements
- Document authorization requirements (roles/permissions)
- Include security considerations in descriptions
- Document rate limiting if applicable
- Document data validation rules

## Checklist

Before considering an endpoint fully documented:

- [ ] Controller has `@ApiTags()`
- [ ] Endpoint has `@ApiOperation()` with summary
- [ ] All response status codes documented with `@ApiResponse()`
- [ ] Request DTOs have `@ApiProperty()` on all properties
- [ ] Response DTOs have `@ApiProperty()` on all properties
- [ ] Query parameters documented with `@ApiQuery()`
- [ ] Path parameters documented with `@ApiParam()`
- [ ] Authentication documented with `@ApiBearerAuth()` if required
- [ ] Examples provided for all properties
- [ ] Descriptions are clear and helpful
- [ ] Swagger UI displays correctly

## Related Documentation

- [Code Documentation Standards](CODE_DOCUMENTATION.md) - In-code documentation guidelines
- [Agent Guidelines](AGENT_GUIDELINES.md) - Development workflow
- [Implementation Plan](IMPLEMENTATION_PLAN.md) - Architecture overview

---

**Last Updated**: 2025-12-11  
**Version**: 1.0

