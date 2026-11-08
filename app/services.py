"""Aturan bisnis pesanan; transaksi atomik dan validasi selalu di server."""
from datetime import datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo
from .db import get_db


class ValidationError(ValueError):
    pass


class DuplicateWarning(Exception):
    def __init__(self, orders):
        self.orders = orders


def now_jakarta():
    return datetime.now(ZoneInfo('Asia/Jakarta')).replace(tzinfo=None, microsecond=0)


def positive_id(value):
    try:
        number = int(value)
        if number < 1 or number > 2147483647:
            raise ValueError
        return number
    except (TypeError, ValueError):
        raise ValidationError('Pilih pelanggan, sumber pesanan, dan produk yang valid.')


def create_order(form, user_id, input_key):
    customer_id = positive_id(form.get('id_pelanggan'))
    channel_id = positive_id(form.get('id_channel'))
    ids = form.getlist('id_produk')
    quantities = form.getlist('jumlah')
    if not ids or len(ids) != len(quantities) or len(ids) > 20:
        raise ValidationError('Pesanan harus memiliki 1–20 baris produk.')
    lines = {}
    for raw_id, raw_quantity in zip(ids,quantities):
        pid = positive_id(raw_id)
        try:
            qty = int(raw_quantity)
        except (TypeError, ValueError):
            raise ValidationError('Jumlah produk harus berupa bilangan bulat.')
        if not 1 <= qty <= 999:
            raise ValidationError('Jumlah produk harus antara 1 dan 999.')
        if pid in lines:
            raise ValidationError('Produk yang sama tidak boleh diulang. Gabungkan jumlahnya dalam satu baris.')
        lines[pid] = qty
    db = get_db()
    db.begin()
    try:
        with db.cursor() as cur:
            # Mengunci pelanggan: input bersamaan untuk pelanggan yang sama diproses berurutan.
            cur.execute('SELECT * FROM pelanggan WHERE id_pelanggan=%s FOR UPDATE',(customer_id,))
            customer = cur.fetchone()
            if not customer:
                raise ValidationError('Pelanggan tidak ditemukan.')
            cur.execute('SELECT id_pesanan FROM pesanan WHERE kunci_input=%s',(input_key,))
            existing = cur.fetchone()
            if existing:
                db.commit()
                return existing['id_pesanan']
            cur.execute('SELECT id_channel FROM channel WHERE id_channel=%s',(channel_id,))
            if not cur.fetchone():
                raise ValidationError('Sumber pesanan tidak ditemukan.')
            now = now_jakarta()
            cur.execute('''SELECT p.id_pesanan,c.nama_channel,p.waktu_masuk FROM pesanan p
                JOIN pelanggan pl ON pl.id_pelanggan=p.id_pelanggan JOIN channel c ON c.id_channel=p.id_channel
                WHERE (p.id_pelanggan=%s OR LOWER(TRIM(pl.nama))=LOWER(TRIM(%s)))
                AND p.waktu_masuk BETWEEN %s AND %s AND p.status<>'dibatalkan'
                ORDER BY p.id_pesanan DESC''',(customer_id,customer['nama'],now-timedelta(minutes=10),now))
            duplicates = cur.fetchall()
            note = form.get('catatan_duplikat','').strip()
            if duplicates and (form.get('konfirmasi_duplikat') != 'ya' or not 5 <= len(note) <= 255):
                raise DuplicateWarning(duplicates)
            total = Decimal('0.00')
            details = []
            for pid,qty in lines.items():
                cur.execute('SELECT harga FROM produk WHERE id_produk=%s',(pid,))
                product = cur.fetchone()
                if not product:
                    raise ValidationError('Produk tidak ditemukan.')
                price = product['harga']
                subtotal = price*qty
                details.append((pid,qty,price,subtotal))
                total += subtotal
            if total > Decimal('999999999999.99'):
                raise ValidationError('Total pesanan melebihi batas penyimpanan.')
            cur.execute('''INSERT INTO pesanan
                (id_pelanggan,id_channel,waktu_masuk,status,total_harga,id_pencatat,kunci_input,catatan_duplikat)
                VALUES (%s,%s,%s,'diterima',%s,%s,%s,%s)''',
                (customer_id,channel_id,now,total,user_id,input_key,note if duplicates else None))
            oid = cur.lastrowid
            cur.executemany('INSERT INTO detail_pesanan (id_pesanan,id_produk,jumlah,harga_satuan,subtotal) VALUES (%s,%s,%s,%s,%s)',[(oid,*detail) for detail in details])
            cur.execute('INSERT INTO status_log (id_pesanan,id_pengguna,status_lama,status_baru,waktu_perubahan) VALUES (%s,%s,NULL,%s,%s)',(oid,user_id,'diterima',now))
        db.commit()
        return oid
    except Exception:
        db.rollback()
        raise


def change_status(order_id, new_status, user_id, reason_code='', note=''):
    db = get_db()
    db.begin()
    try:
        with db.cursor() as cur:
            cur.execute('SELECT * FROM pesanan WHERE id_pesanan=%s FOR UPDATE',(order_id,))
            order = cur.fetchone()
            if not order:
                raise ValidationError('Pesanan tidak ditemukan.')
            old = order['status']
            now = now_jakarta()
            reason = None
            if new_status == 'dibatalkan':
                if old not in ('diterima','diproses'):
                    raise ValidationError('Pesanan selesai atau dibatalkan tidak dapat dibatalkan lagi.')
                if reason_code == 'bahan_habis':
                    reason = 'Bahan baku tidak tersedia'
                elif reason_code == 'tidak_merespons':
                    if old != 'diterima' or now < order['waktu_masuk'] + timedelta(minutes=30):
                        raise ValidationError('Pembatalan tanpa respons hanya untuk pesanan diterima setelah minimal 30 menit sejak dicatat.')
                    reason = 'Pelanggan tidak merespons konfirmasi selama 30 menit'
                else:
                    raise ValidationError('Pilih alasan pembatalan yang sesuai aturan.')
                note = note.strip()
                if len(note) > 150:
                    raise ValidationError('Catatan pembatalan maksimal 150 karakter.')
                if note:
                    reason += ': ' + note
            elif {'diterima':'diproses','diproses':'selesai'}.get(old) != new_status:
                raise ValidationError('Status hanya boleh maju satu tahap: diterima → diproses → selesai.')
            cur.execute('UPDATE pesanan SET status=%s,waktu_selesai=%s,alasan_pembatalan=%s WHERE id_pesanan=%s',
                        (new_status,now if new_status=='selesai' else None,reason,order_id))
            cur.execute('INSERT INTO status_log (id_pesanan,id_pengguna,status_lama,status_baru,waktu_perubahan,alasan) VALUES (%s,%s,%s,%s,%s,%s)',
                        (order_id,user_id,old,new_status,now,reason))
        db.commit()
    except Exception:
        db.rollback()
        raise
