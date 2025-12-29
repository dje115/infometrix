# Dependency Updates - December 2024

## Summary
All components have been updated to the latest stable versions to eliminate deprecated packages and improve security/performance.

## Frontend Updates (package.json)

### Major Dependencies Updated:
- **React**: `19.2.0` → `19.2.3` (latest patch)
- **React DOM**: `19.2.0` → `19.2.3` (latest patch)
- **Vite**: `7.2.7` (already latest)
- **TypeScript**: `5.7.2` (already latest)

### UI Libraries Updated:
- **@emotion/react**: `11.11.4` → `11.14.0`
- **@emotion/styled**: `11.11.5` → `11.14.1`
- **@mui/material**: `7.3.4` → `7.3.6`
- **@mui/icons-material**: `7.3.4` → `7.3.6`
- **@mui/x-data-grid**: `7.21.2` → `7.29.12`
- **@mui/x-date-pickers**: `7.21.2` → `7.29.4`

### HTTP & Data Libraries:
- **axios**: `1.7.7` → `1.13.2`
- **chart.js**: `4.4.0` → `4.5.1`
- **react-chartjs-2**: `5.2.0` → `5.3.1`
- **dompurify**: `3.2.2` → `3.3.1`
- **i18next**: `23.7.6` → `23.16.8`
- **react-router-dom**: `7.9.4` → `7.11.0`

### Dev Dependencies Updated:
- **ESLint**: `8.57.0` → `9.18.0` ⚠️ **MAJOR UPDATE** (migrated to flat config)
- **@eslint/js**: Added `9.18.0` (required for ESLint 9)
- **@types/node**: `20.14.17` → `22.10.5`

### ESLint Migration:
- Migrated from `.eslintrc.json` to `eslint.config.js` (flat config format)
- Updated lint scripts to work with ESLint 9
- Removed deprecated `--ext` flag

## Backend Updates (requirements.txt)

### Core Framework:
- **FastAPI**: `0.115.6` (already latest stable)
- **Uvicorn**: `0.32.1` (already latest stable)
- **Pydantic**: `2.10.3` (already latest stable 2.x)
- **SQLAlchemy**: `2.0.36` (already latest stable 2.x)

### Updated:
- **OpenAI**: Changed from `==2.1.0` to `>=2.1.0` (allows latest patches)

### All other packages verified as latest stable versions.

## Docker Updates

### Build Improvements:
- Added pip timeout/retry configuration to prevent network timeouts:
  - `--default-timeout=300` (5 minute timeout)
  - `--retries=5` (5 retry attempts)
- Applied to both `backend/Dockerfile` and `apps/enforcement-api/Dockerfile.dev`

## Breaking Changes

### ESLint 9 Migration:
- **Breaking**: ESLint 9 uses flat config format
- Old `.eslintrc.json` replaced with `eslint.config.js`
- Lint scripts updated (removed `--ext` flag)
- All existing rules preserved and migrated

## Next Steps

1. **Rebuild Docker containers** to apply all updates:
   ```bash
   docker-compose build --no-cache backend enforcement-api frontend
   docker-compose up -d
   ```

2. **Install updated npm packages** (if not using Docker):
   ```bash
   cd frontend
   npm install
   ```

3. **Verify ESLint works**:
   ```bash
   cd frontend
   npm run lint
   ```

## Notes

- All updates are to latest **stable** versions (no beta/rc)
- Breaking changes documented above
- Python packages already at latest stable versions
- Frontend packages updated to latest compatible versions
- Docker build process improved with timeout/retry handling


