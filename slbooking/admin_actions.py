from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash

from slbooking.admin import admin_login_required
from slbooking.db import get_db

bp = Blueprint('admin_actions', __name__, url_prefix='/admin_actions')

@bp.route('/organize_rooms', methods=('GET', 'POST'))
@admin_login_required
def organize_rooms():
    db = get_db()
    rooms = db.execute('SELECT * FROM room').fetchall()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        picture = request.form['picture']
        db.execute('INSERT INTO room (name, description, picture) VALUES \
                    (?, ?, ?)', (name, description, picture))
        db.commit()
        return redirect(url_for('admin_actions.organize_rooms'))

    return render_template('admin/organize_rooms.html', rooms=rooms);

@bp.route('/edit_room', methods=('GET', 'POST'))
@admin_login_required
def edit_room():
    room_id = request.args.get('room_id')
    db = get_db()
    room = db.execute('SELECT * FROM room WHERE id = (?)', (room_id,)).fetchone()

    if request.method == 'POST':
        name = request.form['room_name']
        description = request.form['room_description']
        picture = request.form['room_picture']
        db.execute('UPDATE room SET name = (?), description = (?), picture = (?)\
                    WHERE id = (?)', (name, description, picture, room_id))
        db.commit()
        return redirect(url_for('admin_actions.organize_rooms'))

    return render_template('admin/edit_room.html', room=room);

@bp.route('/delete_room', methods=('GET',))
@admin_login_required
def delete_room():
    room_id = request.args.get('room_id')
    db = get_db()
    db.execute('DELETE FROM room WHERE id = (?)', (room_id,))
    db.commit()

    return redirect(url_for('admin_actions.organize_rooms'))

@bp.route('/organize_bookings', methods=('GET', 'POST'))
@admin_login_required
def organize_bookings():
    db = get_db()
    booked_rooms = db.execute('SELECT booking.id AS booking_id, room_id, \
        user_id, b_checkin, b_checkout, room.name AS name,\
        user.username AS username FROM booking\
        INNER JOIN room ON booking.room_id = room.id\
        INNER JOIN user on booking.user_id = user.id').fetchall()

    return render_template('admin/organize_bookings.html', 
        booked_rooms=booked_rooms);

@bp.route('/delete_booking', methods=('GET',))
@admin_login_required
def delete_booking():
    booking_id = request.args.get('booking_id')
    db = get_db()
    db.execute('DELETE FROM booking WHERE id = (?)', (booking_id,))
    db.commit()

    return redirect(url_for('admin_actions.organize_bookings'))

@bp.route('/organize_user', methods=('GET', 'POST'))
@admin_login_required
def organize_user():
    db = get_db()
    user = db.execute('SELECT * FROM user').fetchall()
    if request.method == 'POST':
        username = request.form['username']
        mail = request.form['mail']
        password = request.form['password']
        db.execute('INSERT INTO user (username, mail, password) VALUES \
                   (?, ?, ?)', (username, mail, generate_password_hash(password)))
        db.commit()
        return redirect(url_for('admin_actions.organize_user'))

    return render_template('admin/organize_user.html', user=user);

@bp.route('/edit_user', methods=('GET', 'POST'))
@admin_login_required
def edit_user():
    user_id = request.args.get('user_id')
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE id = (?)', (user_id,)).fetchone()

    if request.method == 'POST':
        username = request.form['username']
        mail = request.form['mail']
        password = request.form['password']
        
        db.execute('UPDATE user SET username = (?), mail = (?), password = (?)\
                    WHERE id = (?)', (username, mail, generate_password_hash
                    (password), user_id))
        db.commit()
        return redirect(url_for('admin_actions.organize_user'))

    return render_template('admin/edit_user.html', user=user);

@bp.route('/delete_user', methods=('GET',))
@admin_login_required
def delete_user():
    user_id = request.args.get('user_id')
    db = get_db()
    db.execute('DELETE FROM user WHERE id = (?)', (user_id,))
    db.commit()

    return redirect(url_for('admin_actions.organize_user'))

@bp.route('/admin_index', methods=('GET', ))
@admin_login_required
def admin_index():
    return render_template('admin/admin_index.html');