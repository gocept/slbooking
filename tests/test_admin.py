import pytest
from flask import g, session
from slbooking.db import get_db


def test_admin_logout(client, auth):
    auth.admin_login()

    with client:
        auth.admin_logout()
        assert 'admin_id' not in session