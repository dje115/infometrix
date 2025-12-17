# Database Migrations Guide

## How to Apply Migrations

### Method 1: Using bash -c with echo (Recommended for Windows/PowerShell)

**CRITICAL:** PostgreSQL table/column names are case-sensitive. The most reliable method is to use `bash -c` with `echo` to pipe SQL to psql:

```powershell
docker-compose -f infra/docker/docker-compose.yml -p enforcesense exec -T postgres bash -c 'echo "ALTER TABLE \"PromptTemplate\" ADD COLUMN IF NOT EXISTS \"tenantId\" TEXT;" | psql -U enforcesense -d enforcesense_db'
```

**Key Rules:**
- Use `bash -c` to execute commands in bash (not PowerShell)
- Use `echo` with the SQL command, then pipe (`|`) to `psql`
- Use **escaped double quotes** (`\"`) for PostgreSQL identifiers inside the echo string
- The outer single quotes prevent PowerShell from interpreting the content
- Always verify the migration was applied by checking the database schema

**Why this works:** By using `bash -c`, we avoid PowerShell's quote interpretation entirely. The SQL is constructed in bash and piped directly to psql.

### Method 1b: Using Get-Content Pipe (Alternative)

When applying entire migration files, use the `Get-Content` pipe method:

```powershell
Get-Content "infra\db\migrations\<migration_name>\migration.sql" | docker-compose -f infra/docker/docker-compose.yml -p enforcesense exec -T postgres psql -U enforcesense -d enforcesense_db
```

**Important Notes:**
- Use backslashes (`\`) in the file path for PowerShell
- Use forward slashes (`/`) in docker-compose paths
- The pipe (`|`) passes the SQL content directly to psql, avoiding quote escaping issues
- Verify the file path exists first with `Test-Path`

### Method 2: Copy File to Container

If Method 1 doesn't work, copy the file to the container and execute:

```powershell
# Copy migration file to container
docker cp "infra\db\migrations\<migration_name>\migration.sql" enforcesense-postgres-1:/tmp/migration.sql

# Execute the migration
docker-compose -f infra/docker/docker-compose.yml -p enforcesense exec -T postgres psql -U enforcesense -d enforcesense_db -f /tmp/migration.sql
```

### Method 3: Using Prisma Migrate (If Available)

If Prisma is set up in the container:

```powershell
docker-compose -f infra/docker/docker-compose.yml -p enforcesense exec -T api-platform npx prisma migrate deploy --schema=../../infra/db/schema.prisma
```

### Verifying Migrations

After applying a migration, always verify it was successful:

```powershell
# Check if columns exist
docker-compose -f infra/docker/docker-compose.yml -p enforcesense exec -T postgres psql -U enforcesense -d enforcesense_db -c "SELECT column_name FROM information_schema.columns WHERE table_name = 'TableName' ORDER BY ordinal_position;"

# Check if table exists
docker-compose -f infra/docker/docker-compose.yml -p enforcesense exec -T postgres psql -U enforcesense -d enforcesense_db -c "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'TableName');"
```

## Common Issues

### Issue: "unterminated quoted identifier"
**Cause:** PowerShell is interpreting quotes in SQL commands incorrectly
**Solution:** Use Method 1 (Get-Content pipe) instead of inline SQL strings

### Issue: "relation does not exist"
**Cause:** Table name case sensitivity or table doesn't exist yet
**Solution:** Check actual table names with: `SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';`

### Issue: "syntax error at or near"
**Cause:** SQL syntax error or PowerShell escaping issues
**Solution:** Use Method 1 or Method 2 to avoid PowerShell quote escaping

## Migration File Location

All migrations are stored in: `infra/db/migrations/<timestamp>_<description>/migration.sql`

## Creating New Migrations

1. Create a new directory: `infra/db/migrations/<timestamp>_<description>/`
2. Create `migration.sql` file with your SQL statements
3. Use `IF NOT EXISTS` clauses to make migrations idempotent
4. Test the migration using Method 1 above
5. Commit the migration file to git

## Example: Applying the Prompts Migration

```powershell
# Apply individual ALTER TABLE commands using bash -c
docker-compose -f infra/docker/docker-compose.yml -p enforcesense exec -T postgres bash -c 'echo "ALTER TABLE \"PromptTemplate\" ADD COLUMN IF NOT EXISTS \"tenantId\" TEXT;" | psql -U enforcesense -d enforcesense_db'
docker-compose -f infra/docker/docker-compose.yml -p enforcesense exec -T postgres bash -c 'echo "ALTER TABLE \"PromptTemplate\" ADD COLUMN IF NOT EXISTS \"category\" TEXT;" | psql -U enforcesense -d enforcesense_db'
docker-compose -f infra/docker/docker-compose.yml -p enforcesense exec -T postgres bash -c 'echo "ALTER TABLE \"PromptTemplate\" ADD COLUMN IF NOT EXISTS \"isDefault\" BOOLEAN NOT NULL DEFAULT false;" | psql -U enforcesense -d enforcesense_db'
docker-compose -f infra/docker/docker-compose.yml -p enforcesense exec -T postgres bash -c 'echo "ALTER TABLE \"PromptVersion\" ADD COLUMN IF NOT EXISTS \"outputSchemaJson\" JSONB;" | psql -U enforcesense -d enforcesense_db'
docker-compose -f infra/docker/docker-compose.yml -p enforcesense exec -T postgres bash -c 'echo "ALTER TABLE \"PromptVersion\" ADD COLUMN IF NOT EXISTS \"languageMode\" TEXT;" | psql -U enforcesense -d enforcesense_db'

# Verify columns using bash -c with proper quoting
docker-compose -f infra/docker/docker-compose.yml -p enforcesense exec -T postgres bash -c "psql -U enforcesense -d enforcesense_db -c 'SELECT column_name FROM information_schema.columns WHERE table_name = '\''PromptTemplate'\'' ORDER BY ordinal_position;'"
docker-compose -f infra/docker/docker-compose.yml -p enforcesense exec -T postgres bash -c "psql -U enforcesense -d enforcesense_db -c 'SELECT column_name FROM information_schema.columns WHERE table_name = '\''PromptVersion'\'' ORDER BY ordinal_position;'"
docker-compose -f infra/docker/docker-compose.yml -p enforcesense exec -T postgres bash -c "psql -U enforcesense -d enforcesense_db -c 'SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '\''TenantCompanyProfile'\'');'"
```

**Critical Notes for Future Agents:**
1. **Always use `bash -c`** when executing SQL via docker-compose exec in PowerShell
2. **Use single quotes** around the bash command, **escaped double quotes** (`\"`) for PostgreSQL identifiers
3. **For verification queries**, use nested quotes: outer double quotes, inner single quotes with escaped single quotes (`'\''`)
4. **Table names are case-sensitive** - use exact case: `PromptTemplate`, `PromptVersion`, `TenantCompanyProfile`
5. **If columns don't appear after ALTER**, check if the command actually succeeded (look for "ALTER" in output)

