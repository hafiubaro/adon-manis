import secrets
from flask import Blueprint, render_template, request, g, redirect, url_for, flash, abort, current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from .auth import login_required, admin_required
from .db import query
from .reporting import select_orders, summarize
from .services import create_order, change_status, ValidationError, DuplicateWarning

bp = Blueprint('orders',__name__)


def signer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'],salt='new-order')


@bp.get('/')
@login_required
def dashboard():
    rows, filters, channels = select_orders(request.args, allow_basis=True)
    return render_template('dashboard.html',recent=rows[:7],filters=filters,channels=channels,**summarize(rows))


@bp.get('/pesanan')
@admin_required
def list_orders():
    rows, filters, channels = select_orders(request.args)
    return render_template('orders.html',orders=rows,filters=filters,channels=channels)


@bp.get('/laporan')
@login_required
def report():
    rows, filters, channels = select_orders(request.args, allow_basis=True)
    return render_template('report.html',orders=rows,filters=filters,channels=channels,**summarize(rows))


@bp.route('/pesanan/baru',methods=['GET','POST'])
@admin_required
def new_order():
    duplicates = []
    status_code = 200
    if request.method == 'POST':
        token = request.form.get('kunci_input','')
        try:
            data = signer().loads(token,max_age=7200)
            if data['user_id'] != g.user['id_pengguna']:
                raise BadSignature('Pemilik token berbeda')
            oid = create_order(request.form,g.user['id_pengguna'],data['key'])
            flash('Pesanan berhasil disimpan dengan status diterima.', 'success')
            return redirect(url_for('orders.detail',order_id=oid))
        except (BadSignature,SignatureExpired,KeyError):
            abort(400,description='Form pesanan kedaluwarsa. Buka kembali form pesanan baru.')
        except DuplicateWarning as warning:
            duplicates = warning.orders
            status_code = 409
        except ValidationError as error:
            flash(str(error),'error');status_code = 400
    else:
        token = signer().dumps({'user_id':g.user['id_pengguna'],'key':secrets.token_hex(24)})
    rows = list(zip(request.form.getlist('id_produk'),request.form.getlist('jumlah'))) or [('',1)]
    return render_template('order_form.html',customers=query('SELECT * FROM pelanggan ORDER BY nama'),
        channels=query('SELECT * FROM channel ORDER BY id_channel'),products=query('SELECT * FROM produk ORDER BY id_produk'),
        form=request.form,rows=rows,token=token,duplicates=duplicates),status_code


@bp.get('/pesanan/<int:order_id>')
@admin_required
def detail(order_id):
    order = query('''SELECT p.*,pl.nama,pl.no_telepon,c.nama_channel FROM pesanan p
        JOIN pelanggan pl ON pl.id_pelanggan=p.id_pelanggan JOIN channel c ON c.id_channel=p.id_channel
        WHERE p.id_pesanan=%s''',(order_id,),one=True)
    if not order:
        abort(404)
    items = query('SELECT d.*,pr.nama_produk FROM detail_pesanan d JOIN produk pr ON pr.id_produk=d.id_produk WHERE d.id_pesanan=%s',(order_id,))
    logs = query('SELECT s.*,u.nama FROM status_log s JOIN pengguna u ON u.id_pengguna=s.id_pengguna WHERE s.id_pesanan=%s ORDER BY s.id_log',(order_id,))
    return render_template('order_detail.html',order=order,items=items,logs=logs)


@bp.post('/pesanan/<int:order_id>/status')
@admin_required
def update_status(order_id):
    try:
        change_status(order_id,request.form.get('status'),g.user['id_pengguna'],request.form.get('alasan',''),request.form.get('catatan',''))
        flash('Status pesanan dan riwayat berhasil diperbarui.','success')
    except ValidationError as error:
        flash(str(error),'error')
    return redirect(url_for('orders.detail',order_id=order_id))
