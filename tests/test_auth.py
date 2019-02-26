import pytest
from flask import g, session
from slbooking.db import get_db


def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={
                            'username': 'a',
                            'mail': 'a',
                            'password': 'a'})
    
    with app.app_context():
        assert get_db().execute(
            "select * from user where username = 'a'",
        ).fetchone() is not None

    response = client.post('/auth/register', data={
                            'id': '3',
                            'username': '2', 
                            'mail': 'mail3', 
                            'password': 'password3'})
    
    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM user').fetchone()[0]
        assert count == 3

    assert response.status_code == 302

@pytest.mark.parametrize(('username', 'mail', 'password', 'message'), (
    ('', 'a', 'a', b'Nutzername fehlt.'),
    ('a', '', 'a', b'Email-Adresse fehlt.'),
    ('a', 'a', '', b'Passwort fehlt.'),
    ('a', 'mail', 'test', b'schon registriert'),
))
def test_register_validate_input(client, username, mail, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'mail': mail, 'password': password}
    )
    assert message in response.data

def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200

    response = client.post(
        '/auth/login',
        data={'name': 'b', 'password': 'b'}
    )
    assert b'Falscher Name' in response.data

    auth.login()
    with client:
        client.get('/')
        assert session['user_id'] == 2
        assert g.user['username'] == 'a2'

def test_admin_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    auth.admin_login()

    with client:
        client.get('/')
        assert session['admin_id'] == 2
        assert g.admin['adminname'] == 'test'


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Falscher Name.'),
    ('test', 'b', b'Falsches Passwort.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)

def test_logout(client, auth):
    auth.login()
    
    with client:
        auth.logout()
        assert 'user_id' not in session
