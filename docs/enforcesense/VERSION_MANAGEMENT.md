# Version Management Guide

This document describes how version numbering is managed across the EnforceSense platform.

## Overview

EnforceSense uses a centralized version management system to ensure all applications and services display the same version number. This is critical for:
- **Verifying Docker containers** are running the correct code
- **Troubleshooting** production issues
- **Tracking deployments** across environments
- **Ensuring consistency** across all services

## Version Format

Version numbers follow [Semantic Versioning](https://semver.org/) format: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes that are not backwards compatible
- **MINOR**: New features that are backwards compatible
- **PATCH**: Bug fixes that are backwards compatible

**Current Version**: `0.0.2`

## Version Display

### Frontend Applications

Version is displayed on all web portals:
- **Platform Portal** (http://127.0.0.2:6300) - Bottom right corner
- **Admin Portal** (http://127.0.0.2:6301) - Bottom right corner
- **Client Portal** (http://localhost:4302) - Bottom right corner
- **Debtor Portal** (http://localhost:4303) - Bottom right corner

The version display shows:
- **Compact mode**: `v0.0.2`
- **Full mode**: `EnforceSense v0.0.2 (2025-12-11)`

### API Services

All API services expose a version endpoint:

```bash
# Get version from any API service
curl http://127.0.0.2:6310/version  # api-platform
curl http://127.0.0.2:6311/version  # api-admin
curl http://localhost:4312/version  # api-client
curl http://localhost:4313/version  # api-debtor
curl http://localhost:4314/version  # api-agent
```

Response format:
```json
{
  "version": "0.0.2",
  "name": "EnforceSense",
  "buildDate": "2025-12-11T16:00:00.000Z",
  "gitCommit": "abc123def",
  "service": "api-platform"
}
```

## Version Management

### Centralized Version Source

The version is defined in a single location:
- **File**: `packages/config/src/version.ts`
- **Root package.json**: `package.json` (version field)

Both must be kept in sync when updating versions.

### Updating the Version

### Automated Method (Recommended)

Use the release script to automatically update both files and create a git tag:

```bash
# Using npm script (cross-platform)
pnpm release 0.0.2

# Or using platform-specific scripts
./scripts/create-release.sh 0.0.2      # Linux/Mac
.\scripts\create-release.ps1 0.0.2     # Windows PowerShell
```

The script will:
1. Update `package.json` version
2. Update `packages/config/src/version.ts` version
3. Verify versions match
4. Commit the changes
5. Create a git tag (e.g., `v0.0.2`)

Then push to trigger GitHub release:
```bash
git push origin main
git push origin v0.0.2
```

### Manual Method

1. **Update the version in `packages/config/src/version.ts`**:
   ```typescript
   export const APP_VERSION = '0.0.2'; // Update here
   ```

2. **Update the root `package.json`**:
   ```json
   {
     "version": "0.0.2"  // Update here
   }
   ```

3. **Verify versions are synchronized**:
   ```bash
   pnpm version:check
   ```

4. **Commit and tag**:
   ```bash
   git add package.json packages/config/src/version.ts
   git commit -m "Bump version to 0.0.2"
   git tag -a "v0.0.2" -m "Release v0.0.2"
   git push origin main
   git push origin v0.0.2
   ```

5. **Rebuild all services**:
   ```bash
   # Rebuild all containers with new version
   docker-compose -f infra/docker/docker-compose.yml -p enforcesense build --no-cache
   docker-compose -f infra/docker/docker-compose.yml -p enforcesense up -d
   ```

### Version in Docker Builds

Docker builds automatically use the version from `package.json`:

```bash
# Build with explicit version (optional)
docker-compose -f infra/docker/docker-compose.yml -p enforcesense build \
  --build-arg APP_VERSION=0.0.2 \
  --build-arg BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
  --build-arg GIT_COMMIT=$(git rev-parse --short HEAD)
```

Build arguments:
- `APP_VERSION`: Application version (defaults to 0.0.2)
- `BUILD_DATE`: ISO timestamp of build (auto-generated if not provided)
- `GIT_COMMIT`: Git commit hash (auto-generated if not provided)

## Version Components

### VersionDisplay Component

The `VersionDisplay` React component is available in `@enforcesense/ui`:

```tsx
import { VersionDisplay } from '@enforcesense/ui';

// Compact version in footer (default)
<VersionDisplay />

// Full version with build date
<VersionDisplay variant="full" position="footer" />

// Version in header
<VersionDisplay variant="compact" position="header" />

// Inline (no fixed positioning)
<VersionDisplay variant="full" position="inline" />
```

### Version API Endpoint

All API services include a version controller that returns version information:

```typescript
// Example: apps/api-platform/src/version/version.controller.ts
@Controller('version')
export class VersionController {
  @Get()
  getVersion() {
    return {
      ...getVersionInfo(),
      service: 'api-platform',
    };
  }
}
```

## Verifying Versions in Production

### Check Frontend Version

1. Open any web portal (Admin, Client, or Debtor)
2. Look at the bottom right corner for the version display
3. Hover over the version to see full build information

### Check API Version

```bash
# Check all API versions
for port in 6310 6311 6312 6313 6314; do
  echo "Port $port:"
  curl -s http://localhost:$port/version | jq .
  echo ""
done
```

### Check Docker Container Versions

```bash
# Get version from running container
docker exec enforcesense-api-platform node -e "console.log(require('./packages/config/src/version').APP_VERSION)"

# Or check via API endpoint
docker exec enforcesense-api-platform wget -qO- http://localhost:3000/version
```

## Version Numbering Guidelines

### When to Increment Versions

- **PATCH (0.0.x)**: Bug fixes, security patches, minor improvements
- **MINOR (0.x.0)**: New features, API additions (backwards compatible)
- **MAJOR (x.0.0)**: Breaking changes, major refactoring, API changes

### GitHub Releases

GitHub releases are automatically created when version tags are pushed. The workflow:

1. **Triggers** when a tag matching `v*.*.*` is pushed (e.g., `v0.0.2`)
2. **Verifies** the tag version matches `package.json`
3. **Generates** a changelog from git commits since the last release
4. **Creates** a GitHub release with the changelog

### Creating a Release

```bash
# 1. Create release (updates files, commits, creates tag)
pnpm release 0.0.2

# 2. Push commit and tag
git push origin main
git push origin v0.0.2

# 3. GitHub Actions automatically creates the release
```

### Viewing Releases

- **GitHub**: https://github.com/[your-org]/enforcesense/releases
- **API**: `GET /repos/[owner]/[repo]/releases`

### Release Notes

Release notes are automatically generated from git commits since the last release. The workflow:
- Lists all commits between the previous tag and current tag
- Formats them as a changelog
- Includes them in the GitHub release

## Version History

- `0.0.2` - Documentation review and improvements
- `0.0.1` - Initial version with version management system

## Troubleshooting

### Version Not Displaying

1. **Check component import**: Ensure `@enforcesense/ui` is in dependencies
2. **Verify build**: Rebuild containers after version changes
3. **Check console**: Look for import errors in browser console

### Version Mismatch

If different services show different versions:

1. **Verify source**: Check `packages/config/src/version.ts` matches `package.json`
2. **Rebuild all**: Rebuild all containers with `--no-cache`
3. **Check build args**: Ensure Docker build args are passed correctly

### API Version Endpoint Not Working

1. **Check module import**: Verify `VersionModule` is imported in `app.module.ts`
2. **Check route**: Ensure `/version` endpoint is accessible
3. **Check logs**: Review API container logs for errors

## Best Practices

1. **Always update both files**: `packages/config/src/version.ts` and `package.json`
2. **Use semantic versioning**: Follow MAJOR.MINOR.PATCH format
3. **Tag releases**: Create git tags for each version release
4. **Document changes**: Update CHANGELOG.md with version changes
5. **Test version display**: Verify version appears correctly after deployment

## Related Documentation

- [Setup Guide](SETUP_GUIDE.md) - Initial setup instructions
- [Docker Setup Guide](DOCKER_SETUP.md) - Docker configuration
- [Implementation Plan](IMPLEMENTATION_PLAN.md) - Architecture details

