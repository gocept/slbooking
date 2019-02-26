import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from slbooking.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    #noch dafür sorgen, dass der user nicht wie ein admin heißen kann!
    if request.method == 'POST':
        username = request.form['username']
        mail = request.form['mail']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Nutzername fehlt.'
        elif not mail:
            error = 'Email-Adresse fehlt.'
        elif not password:
            error = 'Passwort fehlt.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'Der Nutzer {} ist schon registriert.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, mail, password) VALUES (?, ?, ?)',
                (username, mail, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (name,)).fetchone()

        #if not check_password_hash(user['password'], password):
         #       error = 'Falsches Passwort.'

        if user is None:
            admin = db.execute(
            'SELECT * FROM admin WHERE adminname = ?', (name,)).fetchone()
            if admin is None:
                error = 'Falscher Name.'
            #if not check_password_hash(admin['password'], password):
             #   error = 'Falsches Passwort.'

        if error is None:
            session.clear()
            if user is not None:
                session['user_id'] = user['id']
                return redirect(url_for('index'))
            else:
                session['admin_id'] = admin['id']
                return redirect(url_for('admin_actions.admin_index'))
            

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view