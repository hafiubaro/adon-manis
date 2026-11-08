from functools import wraps
from flask import Blueprint, request, session, g, redirect, url_for, render_template, flash, abort
from werkzeug.security import check_password_hash
from .db import query

bp = Blueprint('auth', __name__)


@bp.before_app_request
def load_user():
    uid = session.get('user_id')
    g.user = query('SELECT id_pengguna,nama,username,role FROM pengguna WHERE id_pengguna=%s', (uid,), one=True) if uid else None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not g.user:
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if g.user['role'] != 'admin':
            abort(403, description='Aksi ini hanya dapat dilakukan admin.')
        return view(*args, **kwargs)
    return wrapped


@bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        password = request.form.get('password','')
        user = query('SELECT * FROM pengguna WHERE username=%s', (username,), one=True)
        if not user or not check_password_hash(user['password_hash'], password):
            flash('Username atau password salah.', 'error')
            return render_template('login.html'), 401
        session.clear()
        session['user_id'] = user['id_pengguna']
        session.permanent = True
        return redirect(url_for('orders.dashboard'))
    return render_template('login.html')


@bp.post('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
