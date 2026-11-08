"""Satu sumber seleksi untuk daftar, dashboard, dan laporan."""
from datetime import date, timedelta
from decimal import Decimal
from flask import abort
from .db import query

STATUSES = ('diterima', 'diproses', 'selesai', 'dibatalkan')


def select_orders(args, allow_basis=False):
    f = {k: args.get(k, '').strip() for k in ('q','status','channel','mulai','akhir')}
    f['q'] = f['q'][:100]
    f['basis'] = args.get('basis','masuk') if allow_basis else 'masuk'
    if f['basis'] not in ('masuk','selesai'):
        abort(400, description='Dasar tanggal tidak valid.')
    if f['status'] and f['status'] not in STATUSES:
        abort(400, description='Filter status tidak valid.')
    channels = query('SELECT * FROM channel ORDER BY id_channel')
    if f['channel'] and f['channel'] not in {str(c['id_channel']) for c in channels}:
        abort(400, description='Sumber pesanan tidak valid.')
    dates = {}
    try:
        for k in ('mulai','akhir'):
            if f[k]:
                dates[k] = date.fromisoformat(f[k])
                if dates[k].isoformat() != f[k] or dates[k].year < 1000:
                    raise ValueError()
        if 'mulai' in dates and 'akhir' in dates and dates['mulai'] > dates['akhir']:
            raise ValueError()
        end = dates['akhir'] + timedelta(days=1) if 'akhir' in dates else None
    except (ValueError, OverflowError):
        abort(400, description='Periode tidak valid. Gunakan tanggal awal sebelum atau sama dengan tanggal akhir.')
    sql = '''SELECT p.*,pl.nama,c.nama_channel FROM pesanan p
        JOIN pelanggan pl ON pl.id_pelanggan=p.id_pelanggan
        JOIN channel c ON c.id_channel=p.id_channel WHERE 1=1'''
    params = []
    col = 'p.waktu_selesai' if f['basis']=='selesai' else 'p.waktu_masuk'
    if f['basis']=='selesai':
        sql += " AND p.status='selesai'"
    for field in ('status','channel'):
        if f[field]:
            sql += ' AND '+('p.status' if field=='status' else 'p.id_channel')+'=%s'
            params.append(f[field])
    if f['q']:
        # Pengguna mencari teks nama, bukan pola wildcard SQL.
        literal = f['q'].replace('!', '!!').replace('%', '!%').replace('_', '!_')
        sql += " AND (pl.nama LIKE %s ESCAPE '!' OR CAST(p.id_pesanan AS CHAR)=%s)"
        params += ['%'+literal+'%',f['q'].removeprefix('AM-').lstrip('0') or '0']
    if 'mulai' in dates:
        sql += ' AND '+col+'>=%s'; params.append(dates['mulai'])
    if end:
        sql += ' AND '+col+'<%s'; params.append(end)
    rows = query(sql+' ORDER BY '+col+' DESC,p.id_pesanan DESC',params)
    return rows, f, channels


def summarize(rows):
    counts = dict.fromkeys(STATUSES,0)
    revenue = Decimal('0')
    by_channel = {}
    for row in rows:
        counts[row['status']] += 1
        group = by_channel.setdefault(row['nama_channel'], {'jumlah':0,'selesai':0,'nilai':Decimal('0')})
        group['jumlah'] += 1
        if row['status']=='selesai':
            revenue += row['total_harga']; group['nilai'] += row['total_harga']; group['selesai'] += 1
    return dict(counts=counts,revenue=revenue,groups=sorted(by_channel.items()),total=len(rows))
