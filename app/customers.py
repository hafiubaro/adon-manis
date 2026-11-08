import re
import pymysql
from flask import Blueprint, request, render_template, redirect, url_for, flash, abort
from .auth import admin_required
from .db import get_db, query

bp = Blueprint('customers', __name__, url_prefix='/pelanggan')


def validate_customer(form):
    name = form.get('nama','').strip()
    phone = re.sub(r'[\s\-()]','',form.get('no_telepon','').strip())
    if phone.startswith('+62'):
        phone = '0' + phone[3:]
    elif phone.startswith('62'):
        phone = '0' + phone[2:]
    errors = []
    if not 2 <= len(name) <= 100:
        errors.append('Nama wajib diisi sepanjang 2–100 karakter.')
    if phone and not re.fullmatch(r'0[0-9]{9,14}',phone):
        errors.append('Telepon harus 10–15 digit, diawali 0 atau +62; boleh dikosongkan.')
    return name, phone or None, errors


@bp.get('')
@admin_required
def index():
    return render_template('customers.html', customers=query('SELECT * FROM pelanggan ORDER BY id_pelanggan DESC'))


@bp.route('/baru', methods=['GET','POST'])
@bp.route('/<int:customer_id>/edit', methods=['GET','POST'])
@admin_required
def edit(customer_id=None):
    customer = query('SELECT * FROM pelanggan WHERE id_pelanggan=%s', (customer_id,), one=True) if customer_id else {}
    if customer_id and not customer:
        abort(404)
    if request.method == 'POST':
        name,phone,errors = validate_customer(request.form)
        if not errors:
            try:
                with get_db().cursor() as c:
                    if customer_id:
                        c.execute('UPDATE pelanggan SET nama=%s,no_telepon=%s WHERE id_pelanggan=%s', (name,phone,customer_id))
                    else:
                        c.execute('INSERT INTO pelanggan (nama,no_telepon) VALUES (%s,%s)', (name,phone))
                get_db().commit()
                flash('Data pelanggan berhasil disimpan.', 'success')
                return redirect(url_for('customers.index'))
            except pymysql.IntegrityError:
                get_db().rollback()
                errors.append('Nomor telepon sudah digunakan pelanggan lain.')
        for error in errors:
            flash(error, 'error')
        return render_template('customer_form.html',customer=request.form,editing=bool(customer_id)), 400
    return render_template('customer_form.html',customer=customer,editing=bool(customer_id))


@bp.post('/<int:customer_id>/hapus')
@admin_required
def delete(customer_id):
    try:
        with get_db().cursor() as c:
            c.execute('DELETE FROM pelanggan WHERE id_pelanggan=%s',(customer_id,))
            if c.rowcount == 0:
                abort(404)
        get_db().commit()
        flash('Data pelanggan berhasil dihapus.', 'success')
    except pymysql.IntegrityError:
        get_db().rollback()
        flash('Pelanggan tidak dapat dihapus karena masih memiliki pesanan.', 'error')
    return redirect(url_for('customers.index'))
