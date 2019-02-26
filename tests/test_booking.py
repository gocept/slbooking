import pytest
from slbooking.db import get_db


def test_index(client, auth):
    response = client.get('/')
    assert b"Registrieren" in response.data

    auth.login()
    response = client.get('/')

    assert b'Raum buchen' in response.data

    auth.admin_login()
    response = client.get('/')
    assert b'Nutzerverwaltung' in response.data


@pytest.mark.parametrize('path', (
    '/date',
    '/process',
))

def test_login_required(client, path):
    response = client.post(path)
    assert response.headers['Location'] == 'http://localhost/auth/login'

def test_date(client, auth, app):
    auth.login()
    assert client.get('/date').status_code == 200
    assert b'method="post"' in client.get('/date').data

    app_context_insert_room(app)

    #raum1 ist gebucht am selben tag von 12 bis 15 uhr
    with app.app_context():
        db = get_db()
        db.execute('INSERT INTO booking ("id", "user_id", "room_id",\
                    "b_checkin", "b_checkout") VALUES ("1", "1", "1",\
                    "2019-2-16 12:00", "2019-2-16 15:00")')
        db.commit()

@pytest.mark.parametrize(('checkin', 'checkout', 'room_to_be_booked', 'message'), (
('', '16.02.2019 10:00', '1', b'Startdatum fehlt.'),
('16.02.2019 12:00', '', '1', b'Enddatum fehlt.'),
('16.02.2019 12:00', '16.02.2019 10:00', '1', b'Fehlgeschlagen')))
def test_date_cases(auth, client, checkin, checkout, room_to_be_booked, message):
    auth.login()
    response = client.post('/date', data={
                            'checkin': checkin, 
                            'checkout': checkout, 
                            'room_to_be_booked': room_to_be_booked})
    
    assert response.status_code == 200
    assert message in response.data

    #die verschiedenen grenzfälle für die raumbuchung testen

    def assert_booking_sql_query_room_not_in(checkin_time, checkout_time):
        response = client.post('/book', data={
                                'checkin': '2019-2-16 {}'.format(checkin_time),
                                'checkout': '2019-2-16 {}'.format(checkout_time),
                                'room_to_be_booked': '1'})

        assert response.status_code == 200
        assert b'action="/process"' in response.data
        assert b'raum1' not in response.data
        assert b'Kein Raum im Zeitraum von' in response.data

        #start liegt vor start und ende liegt nach ende
        assert_booking_sql_query_room_not_in("09:00", "18:00")

        #buchung liegt mitten drin
        assert_booking_sql_query_room_not_in("13:00", "14:00")

        #start und ende fallen genau auf start und ende einer anderen buchung
        assert_booking_sql_query_room_not_in("12:00", "15:00")

        #start fällt auf start einer buchung, ende außerhalb
        assert_booking_sql_query_room_not_in("12:00", "16:00")

        #ende fällt auf ende einer buchung, start außerhalb
        assert_booking_sql_query_room_not_in("10:00", "15:00")

        #start fällt auf ende einer buchung, ende außerhalb
        response = client.post('/book', data={
                                'checkin': '2019-2-16 15:00',
                                'checkout': '2019-2-16 17:00',
                                'room_to_be_booked': '1'})

        assert response.status_code == 200
        assert b'action="/process"' in response.data
        assert b'raum1' in response.data
        assert b'Kein Raum im Zeitraum von' not in response.data

        #gleiches ergebnis anderes datumsformat (mm)
        response = client.post('/book', data={
                                'checkin': '2019-02-16 15:00',
                                'checkout': '2019-02-16 17:00',
                                'room_to_be_booked': '1'})

        assert response.status_code == 200
        assert b'action="/process"' in response.data
        assert b'raum1' in response.data
        assert b'Kein Raum im Zeitraum von' not in response.data

        #ende fällt auf start einer buchung
        response = client.post('/book', data={
                                'checkin': '2019-2-16 09:00',
                                'checkout': '2019-2-16 12:00',
                                'room_to_be_booked': '1'})

        assert response.status_code == 200
        assert b'action="/process"' in response.data
        assert b'raum1' in response.data
        assert b'Kein Raum im Zeitraum von' not in response.data

        #keine berührungen oder überschneidungen
        response = client.post('/book', data={
                                'checkin': '2019-2-15 13:00',
                                'checkout': '2019-2-15 14:00',
                                'room_to_be_booked': '1'})

        assert response.status_code == 200
        assert b'action="/process"' in response.data
        assert b'raum1' in response.data

        assert_entries(app, "room", 1)

def test_book(client,auth,app):
    auth.login()
    response = client.post('/date', data={
                                        "checkin": "16.02.2019 12:00",
                                        "checkout": "16.02.2019 13:00"})

    assert response.status_code == 200
    assert b"Raumbuchung" in response.data

    
def test_process(client, auth, app):
    auth.login()
    assert client.get('/process').status_code == 405

    assert_entries(app, "booking", 0)

    app_context_insert_room(app)

    response = client.post('/process', data={
                            'room_to_be_booked': 'raum1',
                            'checkin': '2019-2-16 12:00',
                            'checkout': '2019-2-16 13:00'
                            })
    
    assert_entries(app, "booking", 1)

    assert b'weiteren Raum buchen' in response.data
    
def test_user_rooms(client, auth, app):
    auth.login()

    assert client.get('/user_rooms').status_code == 200

    app_context_insert_room(app)

    with app.app_context():
        db = get_db()
        db.execute('INSERT INTO booking ("id", "user_id", "room_id",\
                                         "b_checkin", "b_checkout") \
                                         VALUES ("1", "1", "1", \
                                         "2019-2-16 12:00", "2019-2-16 13:00")')
        db.commit()

    response = client.post('/user_rooms', data={'to_be_deleted': "1"})

    assert_entries(app, "booking", 0)


def assert_entries(app, table, expected):
    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM {0}'.format(table)).fetchone()[0]
        assert count == expected

def app_context_insert_room(app):
    with app.app_context():
        db = get_db()
        db.execute('INSERT INTO room ("id", "name", "description", "picture")\
            VALUES ("1", "raum1", "beschreibung", "bild")')
        db.commit()
