# Community Fork Changes

This document describes the modifications made to the babylon-catalog-api for the Open Demo Platform community fork.

## Repository Information

- **Upstream**: https://github.com/redhat-cop/babylon
- **Fork**: https://github.com/open-demo-platform/babylon
- **Container Image**: quay.io/takinosh/babylon-catalog-api
- **License**: Apache 2.0

## Modified Files

### 1. catalog/api/app.py

**Function**: `get_catalog_namespaces(api_client)`  
**Lines**: 183-226  
**Change**: Added environment variable fallback for catalog namespace access

**Reason**: Enable community deployments without Salesforce integration or complex Kubernetes RBAC configuration.

**Implementation**:
```python
async def get_catalog_namespaces(api_client):
    # CUSTOM: Community fork - support environment variable fallback when Salesforce disabled
    if os.environ.get('SALESFORCE_ENABLED', 'true').lower() == 'false':
        # Use DEFAULT_CATALOG_NAMESPACES environment variable (comma-separated list)
        default_namespaces = os.environ.get('DEFAULT_CATALOG_NAMESPACES', '')
        if default_namespaces:
            namespaces = []
            for ns_name in default_namespaces.split(','):
                ns_name = ns_name.strip()
                if ns_name:
                    # Try to get namespace metadata for display name and description
                    try:
                        ns = await core_v1_api.read_namespace(ns_name)
                        namespaces.append({
                            'name': ns.metadata.name,
                            'displayName': ns.metadata.annotations.get('openshift.io/display-name', ns.metadata.name),
                            'description': ns.metadata.annotations.get('openshift.io/description', f"Catalog {ns.metadata.name}")
                        })
                    except Exception:
                        # If namespace doesn't exist or can't be read, add with basic info
                        namespaces.append({
                            'name': ns_name,
                            'displayName': ns_name,
                            'description': f"Catalog {ns_name}"
                        })
            return namespaces
        # If no DEFAULT_CATALOG_NAMESPACES set, return empty list
        return []

    # Original Kubernetes RBAC logic (unchanged)
    # ... rest of original implementation
```

## Environment Variables

### New Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SALESFORCE_ENABLED` | `true` | Set to `false` to disable Salesforce dependency and use DEFAULT_CATALOG_NAMESPACES |
| `DEFAULT_CATALOG_NAMESPACES` | `""` | Comma-separated list of catalog namespaces to expose (e.g., `babylon-catalog,test-catalog`) |

### Example Configuration

**For community deployments** (no Salesforce):
```yaml
env:
  - name: SALESFORCE_ENABLED
    value: "false"
  - name: DEFAULT_CATALOG_NAMESPACES
    value: "babylon-catalog"
```

**For enterprise deployments** (with Salesforce):
```yaml
env:
  - name: SALESFORCE_ENABLED
    value: "true"
  # No DEFAULT_CATALOG_NAMESPACES needed
```

## Testing Custom Logic

### Unit Test (Future)

```python
# tests/test_auth_session_custom.py
import pytest
import os

async def test_session_with_salesforce_disabled():
    """Test session returns catalogNamespaces from env var when Salesforce disabled"""
    os.environ['SALESFORCE_ENABLED'] = 'false'
    os.environ['DEFAULT_CATALOG_NAMESPACES'] = 'babylon-catalog,test-catalog'
    
    response = await get_catalog_namespaces(mock_api_client)
    
    assert len(response) == 2
    assert response[0]['name'] == 'babylon-catalog'
    assert response[1]['name'] == 'test-catalog'

async def test_session_with_salesforce_enabled():
    """Test session uses Kubernetes RBAC when enabled (original behavior)"""
    os.environ['SALESFORCE_ENABLED'] = 'true'
    
    response = await get_catalog_namespaces(mock_api_client)
    
    # Should use Kubernetes RBAC (not env var)
    # Behavior depends on namespace labels and RBAC permissions
```

### Manual Test (Container)

```bash
# Build container
cd /home/vpcuser/babylon/catalog/api
podman build -t babylon-catalog-api:test -f Containerfile .

# Run with SALESFORCE_ENABLED=false
podman run --rm -d --name test-api \
  -e SALESFORCE_ENABLED=false \
  -e DEFAULT_CATALOG_NAMESPACES=babylon-catalog \
  -e KUBERNETES_SERVICE_HOST=kubernetes.default.svc \
  babylon-catalog-api:test

# Test session endpoint (requires proper Kubernetes config)
podman exec test-api curl -H "X-Forwarded-User: admin" \
  http://localhost:8080/auth/session

# Expected response includes: "catalogNamespaces": ["babylon-catalog"]
```

## Upstream Sync Strategy

This fork follows the upstream sync strategy documented in ADR-0014 (Fork and Upstream Tracking).

### Weekly Checks (Automated)

GitHub Actions workflow runs every Monday to check for upstream updates:
- `.github/workflows/upstream-sync-check.yml`
- Creates issue if new commits are available
- Lists commits for manual review

### Monthly Merges (Manual)

```bash
cd /home/vpcuser/babylon
git fetch upstream
git checkout main
git merge --no-ff upstream/main

# Resolve conflicts (preserve CUSTOM: sections in app.py)
# Test changes
git push origin main
```

### Conflict Resolution

When merging upstream changes:

1. **If conflict in `catalog/api/app.py`**:
   - Preserve the custom `get_catalog_namespaces` function
   - Keep the `# CUSTOM:` comment blocks
   - Use `git checkout --ours catalog/api/app.py` if entire function conflicts
   - Manually merge if upstream modified same function

2. **Marker for custom code**:
   - All modifications marked with `# CUSTOM:` comments
   - Search for this marker during conflict resolution

## Building and Publishing

### Local Build

```bash
cd /home/vpcuser/babylon/catalog/api
podman build -t quay.io/takinosh/babylon-catalog-api:test -f Containerfile .
```

### Publish to Quay.io

```bash
# Login to Quay.io
podman login quay.io -u takinosh

# Tag and push
podman tag quay.io/takinosh/babylon-catalog-api:test \
  quay.io/takinosh/babylon-catalog-api:v0.42.6-community.1

podman push quay.io/takinosh/babylon-catalog-api:v0.42.6-community.1
podman push quay.io/takinosh/babylon-catalog-api:test
```

### CI/CD (GitHub Actions)

Automated builds are triggered by:
- Push to `main` branch → builds `latest` tag
- Push tag `v*-community.*` → builds versioned release
- Manual workflow dispatch

Workflow file: `.github/workflows/build-babylon-catalog-api.yml`

## Version Tracking

**Current Community Fork Version**: v0.42.6-community.1

**Versioning Format**: `v{UPSTREAM_VERSION}-community.{PATCH_NUMBER}`
- `UPSTREAM_VERSION`: Version from upstream babylon (e.g., v0.42.6)
- `PATCH_NUMBER`: Community fork patch number (increments with each release)

**Version History**:
- `v0.42.6-community.1` (2026-04-23): Initial release with Salesforce fallback logic

## Contributing Back to Upstream

If this functionality would benefit the broader Babylon community:

1. Open issue in `redhat-cop/babylon` repository
2. Propose Kubernetes-based auth as optional feature
3. Submit PR with feature flag (preserves Salesforce mode for enterprise)
4. If accepted, deprecate community fork in favor of upstream

## References

- **ADR-0024**: Custom Babylon Catalog API Without Salesforce Dependency
- **ADR-0014**: Fork and Upstream Tracking Strategy
- **Task #36**: Build Custom Babylon Catalog API (Phase 2)
- **Upstream Repo**: https://github.com/redhat-cop/babylon
- **License**: Apache 2.0 - https://github.com/redhat-cop/babylon/blob/main/LICENSE

## Support

**Community Fork Support**:
- GitHub Issues: https://github.com/open-demo-platform/babylon/issues
- Documentation: https://github.com/open-demo-platform/open-demo-platform

**Note**: This community fork is not officially supported by Red Hat. For enterprise deployments, use the official Red Hat Demo Platform.
