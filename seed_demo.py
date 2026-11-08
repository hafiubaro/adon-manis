"""Membuat 10 pesanan FIKTIF untuk demonstrasi; hanya ketika tabel pesanan masih kosong."""
from datetime import timedelta
from werkzeug.datastructures import MultiDict
from app import create_app
from app.db import query,get_db
from app.services import create_order,change_status,now_jakarta


def seed(app):
    with app.app_context():
        if query('SELECT id_pesanan FROM pesanan LIMIT 1'):
            raise RuntimeError('Data pesanan sudah ada. Seed demo dihentikan tanpa mengubah data.')
        for i in range(10):
            data=MultiDict([('id_pelanggan',str(i%5+1)),('id_channel',str(i%6+1)),('id_produk',str(i%5+1)),('jumlah',str(i%3+1))])
            oid=create_order(data,1,'demo-modul7-'+str(i))
            if i in (1,2,4,5,7,8):change_status(oid,'diproses',1)
            if i in (2,5,8):change_status(oid,'selesai',1)
            if i==9:change_status(oid,'dibatalkan',1,'bahan_habis','Data demonstrasi')
            base=now_jakarta()-timedelta(hours=12-i)
            with get_db().cursor() as cur:
                cur.execute('UPDATE pesanan SET waktu_masuk=%s,waktu_selesai=IF(status=%s,%s,NULL) WHERE id_pesanan=%s',(base,'selesai',base+timedelta(minutes=20),oid))
                logs=query('SELECT id_log FROM status_log WHERE id_pesanan=%s ORDER BY id_log',(oid,))
                for j,log in enumerate(logs):cur.execute('UPDATE status_log SET waktu_perubahan=%s WHERE id_log=%s',(base+timedelta(minutes=10*j),log['id_log']))
            get_db().commit()
        print('10 pesanan, 10 detail, dan 20 log status fiktif berhasil dibuat.')


if __name__=='__main__':seed(create_app())
