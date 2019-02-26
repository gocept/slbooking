import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from slbooking.auth import login_required
from slbooking.db import get_db

bp = Blueprint('booking', __name__)

@bp.route('/')
def index():
    db = get_db()
    rooms = db.execute(
        'SELECT name FROM room'
    ).fetchall()
    return render_template('booking/index.html', rooms=rooms)

#user wählt zeitraum und anschließend verfügbaren raum aus
@bp.route('/date', methods=('GET', 'POST'))
@login_required
def date():
    db = get_db()
    if request.method == 'POST':
        
        #Format für den Nutzer
        checkin = request.form['checkin']
        checkout = request.form['checkout']

        error = None

        if not checkin:
            error = 'Startdatum fehlt.'

        if not checkout:
            error = 'Enddatum fehlt.'

        if error is not None:
            flash(error)
        else:
            #Format, um zu überprüfen, dass Buchungsstart vor Buchungsende liegt
            comp_checkin = datetime.datetime.strptime(
                checkin,'%d.%m.%Y %H:%M').strftime('%Y%m%d%H%M')
            comp_checkout = datetime.datetime.strptime(
                checkout,'%d.%m.%Y %H:%M').strftime('%Y%m%d%H%M')

            #Format für Datenbank
            db_checkin = datetime.datetime.strptime(
                checkin,'%d.%m.%Y %H:%M').strftime('%Y-%m-%d %H:%M')
            db_checkout = datetime.datetime.strptime(
                checkout,'%d.%m.%Y %H:%M').strftime('%Y-%m-%d %H:%M')

            if comp_checkin > comp_checkout:
                error = 'Fehlgeschlagen'

            if error is not None:
                flash(error)
            else:
                return book(db_checkin, db_checkout, checkin, checkout)    

    return render_template('booking/date.html')

def book(db_checkin, db_checkout, checkin, checkout):
    r_checkin = db_checkin
    r_checkout = db_checkout
    db = get_db()
    room_avb = db.execute('SELECT name FROM room WHERE id NOT IN \
                          (SELECT room_id FROM booking WHERE \
                          b_checkin <= (?) AND b_checkout > (?) OR \
                          b_checkin < (?) AND b_checkout >= (?) OR \
                          b_checkin > (?) AND b_checkout < (?))',\
                          (r_checkin, r_checkin, r_checkout, r_checkout,
                           r_checkin, r_checkout)).fetchall()
    
    return render_template('booking/book.html', 
                            room_avb=room_avb, checkin=checkin,
                            checkout=checkout, db_checkin=db_checkin,
                            db_checkout=db_checkout)

#nimmt auswahl des users entgegen und trägt die buchung in booking ein
@bp.route('/process', methods=('POST',))
@login_required
def process():
    #kommt an in Datenbankformat
    r_checkin = request.form['checkin']
    r_checkout = request.form['checkout']
    #Daten werden umgewandelt in nutzerfreundliches Format
    checkin = datetime.datetime.strptime(
        r_checkin,'%Y-%m-%d %H:%M').strftime('%d.%m.%Y %H:%M')

    checkout = datetime.datetime.strptime(
        r_checkout,'%Y-%m-%d %H:%M').strftime('%d.%m.%Y %H:%M')
    user_id = session.get('user_id')

    room_booked = request.form['room_to_be_booked']

    db = get_db()
    room_id = db.execute('SELECT id FROM room WHERE name = (?)' 
        ,(room_booked,)).fetchall()[0]['id']
    db.execute('INSERT INTO booking (user_id, room_id, b_checkin, b_checkout)\
                VALUES (?, ?, ?, ?)',(user_id, room_id, r_checkin, r_checkout))
    db.commit()
    
    return render_template('booking/process.html', r_checkin=r_checkin,
                            r_checkout=r_checkout, room_booked=room_booked,
                            checkin=checkin, checkout=checkout);

@bp.route('/user_rooms', methods=('GET', 'POST'))
@login_required
def user_rooms():
    db = get_db()
    user_id = session.get('user_id')
    if request.method == 'POST':
        ids_to_delete = request.form.getlist("to_be_deleted")
        #import pdb; pdb.set_trace()
        for ids in ids_to_delete:
            print(ids)
            db.execute('DELETE FROM booking WHERE id = (?)', (ids,))
            db.commit()
    rooms_booked_when = db.execute('SELECT booking.id AS booking_id,\
                                    room.name AS name, room_id, b_checkin,\
                                    b_checkout FROM booking INNER JOIN room \
                                    ON booking.room_id = room.id  \
                                    WHERE user_id = (?) ', (user_id,)).fetchall()
    
    return render_template('booking/user_rooms.html',
                            rooms_booked=rooms_booked_when); 
