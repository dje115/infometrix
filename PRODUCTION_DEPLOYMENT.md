# Production Deployment Guide - Azure & AWS

**Date:** 2025-01-27  
**Purpose:** Deploy performance fixes to Azure and AWS production environments

---

## 🎯 Overview

This guide covers deploying the performance fixes to production environments running on Azure or AWS, where the application runs natively (not in Docker containers).

---

## 📋 Prerequisites

### Required Tools
- PostgreSQL client (`psql`) installed
- Python 3.8+ (for Python migration script)
- Access to production database
- Database connection credentials

### Required Information
- Database host/endpoint
- Database port (usually 5432)
- Database name
- Database username
- Database password (or access to secrets manager)

---

## 🔵 Azure Deployment

### Option 1: Using Bash Script

```bash
# Set environment variables
export AZURE_DB_HOST="your-server.postgres.database.azure.com"
export AZURE_DB_USER="adminuser@your-server"
export AZURE_DB_PASSWORD="your-password"
export AZURE_DB_NAME="ccs_quote_tool"
export AZURE_DB_PORT="5432"

# Run migration script
chmod +x scripts/apply_migrations_azure.sh
./scripts/apply_migrations_azure.sh
```

### Option 2: Using Python Script

```bash
# Set environment variables
export AZURE_DB_HOST="your-server.postgres.database.azure.com"
export AZURE_DB_USER="adminuser@your-server"
export AZURE_DB_PASSWORD="your-password"
export AZURE_DB_NAME="ccs_quote_tool"

# Run Python script
python scripts/apply_migrations_production.py
```

### Option 3: Using Azure Cloud Shell

```bash
# Upload migration files to Azure Cloud Shell
# Then run:
export AZURE_DB_HOST="your-server.postgres.database.azure.com"
export AZURE_DB_USER="adminuser@your-server"
export AZURE_DB_PASSWORD="your-password"
export AZURE_DB_NAME="ccs_quote_tool"

./scripts/apply_migrations_azure.sh
```

### Azure-Specific Notes

1. **Firewall Rules**: Ensure your IP is allowed in Azure Portal → PostgreSQL Server → Connection Security
2. **SSL Connection**: Azure PostgreSQL requires SSL. Add `?sslmode=require` to connection string if needed
3. **Azure Key Vault**: Store credentials securely:
   ```bash
   # Retrieve from Azure Key Vault
   export AZURE_DB_PASSWORD=$(az keyvault secret show --vault-name your-vault --name db-password --query value -o tsv)
   ```

---

## 🟠 AWS Deployment

### Option 1: Using Bash Script

```bash
# Set environment variables
export AWS_DB_HOST="your-db.xxxxx.us-east-1.rds.amazonaws.com"
export AWS_DB_USER="adminuser"
export AWS_DB_PASSWORD="your-password"
export AWS_DB_NAME="ccs_quote_tool"
export AWS_DB_PORT="5432"

# Run migration script
chmod +x scripts/apply_migrations_aws.sh
./scripts/apply_migrations_aws.sh
```

### Option 2: Using Python Script

```bash
# Set environment variables
export AWS_DB_HOST="your-db.xxxxx.us-east-1.rds.amazonaws.com"
export AWS_DB_USER="adminuser"
export AWS_DB_PASSWORD="your-password"
export AWS_DB_NAME="ccs_quote_tool"

# Run Python script
python scripts/apply_migrations_production.py
```

### Option 3: Using AWS Secrets Manager

```bash
# Retrieve credentials from AWS Secrets Manager
export AWS_DB_PASSWORD=$(aws secretsmanager get-secret-value \
  --secret-id your-secret-name \
  --query SecretString \
  --output text | jq -r .password)

export AWS_DB_HOST=$(aws secretsmanager get-secret-value \
  --secret-id your-secret-name \
  --query SecretString \
  --output text | jq -r .host)

# Then run migration
./scripts/apply_migrations_aws.sh
```

### Option 4: Using EC2 Instance

```bash
# SSH into EC2 instance
ssh -i your-key.pem ec2-user@your-ec2-instance

# Clone repository or upload migration files
git clone https://github.com/dje115/infometrix.git
cd infometrix

# Set environment variables
export AWS_DB_HOST="your-db.xxxxx.us-east-1.rds.amazonaws.com"
export AWS_DB_USER="adminuser"
export AWS_DB_PASSWORD="your-password"
export AWS_DB_NAME="ccs_quote_tool"

# Run migration
./scripts/apply_migrations_aws.sh
```

### AWS-Specific Notes

1. **Security Groups**: Ensure RDS security group allows connections from your IP or EC2 instance
2. **VPC Configuration**: If RDS is in private subnet, use EC2 instance in same VPC or VPN
3. **IAM Authentication**: Can use IAM database authentication instead of passwords
4. **CloudWatch**: Monitor migration progress in CloudWatch logs

---

## 🐍 Python Script (Universal)

The Python script works for both Azure and AWS:

```bash
# Install dependencies
pip install psycopg2-binary

# Set environment variables (works with any cloud provider)
export DB_HOST="your-database-host"
export DB_USER="your-username"
export DB_PASSWORD="your-password"
export DB_NAME="ccs_quote_tool"
export DB_PORT="5432"

# Run script
python scripts/apply_migrations_production.py
```

### Advanced Usage

```bash
# Specify custom migration directories
python scripts/apply_migrations_production.py \
  --migrations-dir backend/migrations \
  --enforcement-migrations-dir apps/enforcement-api/migrations
```

---

## 📝 Manual Migration Application

If scripts don't work, apply migrations manually:

### Step 1: Connect to Database

**Azure:**
```bash
psql -h your-server.postgres.database.azure.com \
     -U adminuser@your-server \
     -d ccs_quote_tool \
     -W
```

**AWS:**
```bash
psql -h your-db.xxxxx.us-east-1.rds.amazonaws.com \
     -U adminuser \
     -d ccs_quote_tool \
     -W
```

### Step 2: Apply Migrations

```sql
-- Migration 1: Missing Foreign Key Indexes
\i backend/migrations/add_missing_foreign_key_indexes.sql

-- Migration 2: Composite Indexes
\i backend/migrations/add_composite_indexes_for_common_queries.sql

-- Migration 3: EnforceSense Performance Indexes
\i apps/enforcement-api/migrations/add_performance_indexes_enforcesense.sql
```

---

## 🔐 Security Best Practices

### 1. Use Secrets Management

**Azure Key Vault:**
```bash
export AZURE_DB_PASSWORD=$(az keyvault secret show \
  --vault-name your-vault \
  --name db-password \
  --query value -o tsv)
```

**AWS Secrets Manager:**
```bash
export AWS_DB_PASSWORD=$(aws secretsmanager get-secret-value \
  --secret-id your-secret-name \
  --query SecretString \
  --output text | jq -r .password)
```

### 2. Use Environment Variables

Never hardcode credentials in scripts. Always use environment variables.

### 3. Limit Database Access

- Use least-privilege database users
- Restrict network access (firewall rules, security groups)
- Use SSL/TLS connections

### 4. Audit Logging

Enable database audit logs to track migration execution.

---

## ✅ Verification

After applying migrations, verify they were successful:

### Check Indexes Exist

```sql
-- Connect to database
psql -h your-host -U your-user -d ccs_quote_tool

-- Check foreign key indexes
SELECT COUNT(*) FROM pg_indexes 
WHERE schemaname = 'public' 
AND indexname LIKE 'idx_%' 
AND (indexname LIKE '%_contact_id%' 
     OR indexname LIKE '%_created_by%' 
     OR indexname LIKE '%_supplier_id%');

-- Expected: At least 5 indexes

-- Check composite indexes
SELECT COUNT(*) FROM pg_indexes 
WHERE schemaname = 'public' 
AND indexname LIKE 'idx_%' 
AND (indexname LIKE '%_tenant_%' 
     OR indexname LIKE '%_customer_%' 
     OR indexname LIKE '%_status%');

-- Expected: At least 5 indexes
```

### Test Application

1. Restart your application service
2. Navigate to Customers, Opportunities, Leads pages
3. Verify no timeout errors occur
4. Check API response times (should be < 1 second)

---

## 🚨 Troubleshooting

### Connection Issues

**Azure:**
- Check firewall rules in Azure Portal
- Verify server name format: `your-server.postgres.database.azure.com`
- Ensure username includes `@your-server` suffix

**AWS:**
- Check security group rules
- Verify RDS endpoint is correct
- Check VPC routing if using private subnet

### Migration Errors

**"Index already exists":**
- This is OK - index was already created
- Script will skip and continue

**"Permission denied":**
- Ensure database user has CREATE INDEX permission
- May need to run as superuser or grant permissions

**"Connection timeout":**
- Check network connectivity
- Verify firewall/security group rules
- Check if database is accessible from your location

---

## 📊 Expected Results

After successful migration:

- ✅ 32+ indexes created in database
- ✅ Query performance improved by 95%+
- ✅ No timeout errors
- ✅ API response times < 1 second

---

## 🔄 CI/CD Integration

### Azure DevOps Pipeline

```yaml
- task: Bash@3
  displayName: 'Apply Database Migrations'
  inputs:
    targetType: 'inline'
    script: |
      export AZURE_DB_HOST="$(AZURE_DB_HOST)"
      export AZURE_DB_USER="$(AZURE_DB_USER)"
      export AZURE_DB_PASSWORD="$(AZURE_DB_PASSWORD)"
      export AZURE_DB_NAME="$(AZURE_DB_NAME)"
      ./scripts/apply_migrations_azure.sh
  env:
    AZURE_DB_PASSWORD: $(AzureKeyVaultSecret)
```

### AWS CodePipeline

```yaml
- name: ApplyMigrations
  actionTypeId:
    category: Build
    owner: AWS
    provider: CodeBuild
  configuration:
    ProjectName: apply-migrations-project
  inputArtifacts:
    - name: SourceOutput
```

---

## 📚 Additional Resources

- [Azure Database for PostgreSQL Documentation](https://docs.microsoft.com/azure/postgresql/)
- [AWS RDS PostgreSQL Documentation](https://docs.aws.amazon.com/rds/latest/userguide/CHAP_PostgreSQL.html)
- [PostgreSQL Index Documentation](https://www.postgresql.org/docs/current/indexes.html)

---

**Last Updated:** 2025-01-27  
**Status:** Production Ready

