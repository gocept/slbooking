import pytest
from slbooking.db import get_db


@pytest.mark.parametrize('path', (
    '/admin_actions/organize_user',
    '/admin_actions/organize_rooms',
    '/admin_actions/organize_bookings',
    '/admin_actions/edit_room',
    '/admin_actions/edit_user',
))

def test_admin_login_required(client, path):
    response = client.post(path)
    assert response.status_code == 302
    assert response.headers['Location'] == 'http://localhost/auth/login'

def test_access_not_logged_in(app, client):
    assert client.get('/admin_actions/admin_index').status_code == 302
    assert client.get('/admin_actions/admin_index').headers['Location']\
    == 'http://localhost/auth/login'

def test_access_as_normal_user(app, client, auth):
    auth.login()
    assert client.get('/admin_actions/admin_index').status_code == 302
    assert client.get('/admin_actions/admin_index').headers['Location'] \
    == 'http://localhost/auth/login'

def test_access_as_admin(app, client, auth):
    auth.admin_login()
    assert client.get('/admin_actions/admin_index').status_code == 200

def test_organize_rooms(app, client, auth):
    auth.admin_login()
    assert client.get('/admin_actions/organize_rooms').status_code == 200
    app_context_insert_room(app)
    response = client.get('/admin_actions/organize_rooms')
    assert b"raum1" in response.data
    assert_entries(app, 'room', 1)
    response = client.post('/admin_actions/organize_rooms', data={
                            'id': '2',
                            'name': 'raum2', 
                            'description': 'beschreibung raum2', 
                            'picture': 'bild von raum2'})

    assert response.status_code == 302
    response = client.get('/admin_actions/organize_rooms')
    assert b"raum2" in response.data
    assert_entries(app, 'room', 2)

def test_edit_room(app, client, auth):
    auth.admin_login()
    assert client.get('/admin_actions/edit_room').status_code == 200
    app_context_insert_room(app)
    with app.app_context():
        db = get_db()
        name = db.execute('SELECT name FROM room').fetchone()[0]
        assert name == "raum1"
        id_r = db.execute('SELECT id FROM room').fetchone()[0]
        assert id_r == 1

    with app.app_context():
        client.post('/admin_actions/edit_room',
                data={
                "room_id": 1,
                "room_name": "neuerRaum",
                "room_description": "neueBeschreibung",
                "room_picture": "neuesBild"})

        db = get_db()
        name = db.execute('SELECT name FROM room').fetchone()[0]
        assert name == "neuerRaum"

    assert response.headers['Location'] == 'http://localhost/admin_actions/organize_rooms'

def test_delete_room(app, client, auth):
    auth.admin_login()
    assert_entries(app, "room", 0)
    app_context_insert_room(app)
    assert_entries(app, "room", 1)
    data={"room_id": "1",}
    client.get('admin_actions/delete_room', query_string=data)
    assert_entries(app, "room", 0)

def test_organize_bookings(app, client, auth):
    auth.admin_login()
    assert client.get('admin_actions/organize_bookings').status_code == 200
    assert_entries(app, "booking", 0)
    app_context_insert_room(app)
    app_context_insert_booking(app)
    assert_entries(app, "booking", 1)

def test_delete_booking(app, client, auth):
    auth.admin_login()
    assert_entries(app, "booking", 0)
    app_context_insert_booking(app)
    assert_entries(app, "booking", 1)
    data={"booking_id": "1",}
    client.get('admin_actions/delete_booking', query_string=data)
    assert_entries(app, "booking", 0)

def test_organize_user(app, client, auth):
    auth.admin_login()
    assert client.get('/admin_actions/organize_user').status_code == 200
    assert_entries(app, 'user', 2)
    assert b"a" in client.get('admin_actions/organize_user').data
    client.post('admin_actions/organize_user', data={
                                                'username': 'newUser',
                                                'mail': 'newMail',
                                                'password': 'newPass'})
    assert_entries(app, 'user', 3)

def test_edit_user(app, client, auth):
    auth.admin_login()
    assert client.get('/admin_actions/edit_user').status_code == 200
    assert_entries(app, 'user', 2)
    response = client.post('/admin_actions/edit_user', data={
                                                        "user_id": "2",
                                                        "username": "user3",
                                                        "mail": "mail3",
                                                        "password": "password3",
                                                        })
    assert response.status_code == 302
    #noch testen, dass tatsächlich eine änderung in der db erfolgt ist?
    #s. edit_rooms

def test_delete_user(app, client, auth):
    auth.admin_login()
    assert_entries(app, "user", 2)
    data={"user_id": "1",}
    client.get('admin_actions/delete_user', query_string=data)
    assert_entries(app, "user", 1)

def app_context_insert_room(app):
    with app.app_context():
        db = get_db()
        db.execute('INSERT INTO room ("id", "name", "description", "picture")\
            VALUES ("1", "raum1", "beschreibung", "bild")')
        db.commit()

def app_context_insert_booking(app):
    with app.app_context():
        db = get_db()
        db.execute('INSERT INTO booking \
                            ("id", "user_id", "room_id", \
                            "b_checkin", "b_checkout")\
                    VALUES ("1", "3", "1", "2019-12-03 02:30", \
                            "2019-12-03 02:50")')
        db.commit()

def assert_entries(app, table, expected):
    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM {0}'.format(table)).fetchone()[0]
        assert count == expected