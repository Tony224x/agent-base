import pytest
import jwt as pyjwt

from src.adapters.auth.jwt_adapter import JWTAuthAdapter

SECRET = "test-secret-key"


@pytest.fixture
def adapter():
    return JWTAuthAdapter(secret=SECRET, algorithm="HS256")


def _make_token(**claims):
    return pyjwt.encode(claims, SECRET, algorithm="HS256")


@pytest.mark.asyncio
async def test_valid_token(adapter):
    token = _make_token(sub="user1", tenant_id="t1", roles=["admin"])
    ctx = await adapter.validate_token(token)
    assert ctx is not None
    assert ctx.user_id == "user1"
    assert ctx.tenant_id == "t1"
    assert ctx.roles == ["admin"]


@pytest.mark.asyncio
async def test_valid_token_minimal(adapter):
    token = _make_token(sub="user2")
    ctx = await adapter.validate_token(token)
    assert ctx is not None
    assert ctx.user_id == "user2"
    assert ctx.tenant_id is None
    assert ctx.roles == []


@pytest.mark.asyncio
async def test_invalid_token(adapter):
    ctx = await adapter.validate_token("totally.invalid.token")
    assert ctx is None


@pytest.mark.asyncio
async def test_wrong_secret(adapter):
    token = pyjwt.encode({"sub": "user1"}, "wrong-secret", algorithm="HS256")
    ctx = await adapter.validate_token(token)
    assert ctx is None


@pytest.mark.asyncio
async def test_missing_sub(adapter):
    token = _make_token(tenant_id="t1")
    ctx = await adapter.validate_token(token)
    assert ctx is None


@pytest.mark.asyncio
async def test_extra_metadata(adapter):
    token = _make_token(sub="user1", custom_field="hello")
    ctx = await adapter.validate_token(token)
    assert ctx is not None
    assert ctx.metadata.get("custom_field") == "hello"
