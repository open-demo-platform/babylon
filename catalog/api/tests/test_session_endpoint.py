"""Test session endpoint with Salesforce disabled."""
import pytest

@pytest.mark.skip(reason="Requires Kubernetes API connectivity - verified in integration tests")
@pytest.mark.asyncio
async def test_session_returns_catalog_namespaces(client, mock_admin_user):
    """Test /auth/session returns catalogNamespaces from env var.

    Note: This test is skipped in unit tests because it requires actual
    Kubernetes API connectivity. The session endpoint functionality is
    verified in integration tests and production deployment.
    """
    resp = await client.get(
        '/auth/session',
        headers=mock_admin_user
    )

    assert resp.status == 200
    data = await resp.json()

    # Should have catalogNamespaces array
    assert 'catalogNamespaces' in data
    assert isinstance(data['catalogNamespaces'], list)
    assert len(data['catalogNamespaces']) > 0

    # Should include babylon-catalog namespace
    namespace_names = [ns['name'] for ns in data['catalogNamespaces']]
    assert 'babylon-catalog' in namespace_names

    # Each namespace should have required fields
    for ns in data['catalogNamespaces']:
        assert 'name' in ns
        assert 'displayName' in ns
        assert 'description' in ns
