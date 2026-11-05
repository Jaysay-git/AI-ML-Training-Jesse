import pytest
from types import SimpleNamespace
from fastapi import HTTPException

from app.api.dependencies import get_admin_user


def test_admin_access_allowed():
    admin = SimpleNamespace(role="admin")

    result = get_admin_user(current_user=admin)

    assert result == admin


def test_regular_user_admin_access_denied():
    user = SimpleNamespace(role="user")

    with pytest.raises(HTTPException) as error:
        get_admin_user(current_user=user)

    assert error.value.status_code == 403
    assert error.value.detail == "Administrator privileges required"
