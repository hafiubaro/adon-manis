"""Inisialisasi aman: menolak database berisi tabel. Akun dibuat dengan password pengguna."""
import argparse
import getpass
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from app.db import connect

ROOT = Path(__file__).resolve().parent


def initialize(config, admin_password, owner_password):
    name = config['DB_NAME']
    if not re.fullmatch(r'[A-Za-z0-9_]+', name):
        raise ValueError('Nama database hanya boleh huruf, angka, dan underscore.')
    for password in (admin_password, owner_password):
        if len(password) < 10:
            raise ValueError('Password minimal 10 karakter.')
    server = connect(config, database=False)
    try:
        with server.cursor() as c:
            c.execute(f'CREATE DATABASE IF NOT EXISTS `{name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
            c.execute(f'USE `{name}`')
            c.execute('SHOW TABLES')
            if c.fetchall():
                raise RuntimeError('Database sudah berisi tabel. Inisialisasi dihentikan agar data tidak tertimpa.')
            sql = (ROOT / 'database/schema.sql').read_text(encoding='utf-8')
            sql = '\n'.join(line for line in sql.splitlines() if not line.lstrip().startswith('--'))
            for statement in sql.split(';'):
                if statement.strip():
                    c.execute(statement)
            c.executemany('INSERT INTO channel (nama_channel) VALUES (%s)',
                          [(x,) for x in ['WhatsApp','GoFood','GrabFood','ShopeeFood','TikTok','Facebook']])
            c.executemany('INSERT INTO produk (nama_produk,harga) VALUES (%s,%s)',
                          [('Roti Coklat',15000),('Kue Sus',20000),('Brownies',35000),('Donat',10000),('Pastry Keju',18000)])
            c.executemany('INSERT INTO pelanggan (nama,no_telepon) VALUES (%s,%s)',
                          [('Siti Aminah','081234567801'),('Budi Santoso','081234567802'),('Rina Wati','081234567803'),('Andi Pratama','081234567804'),('Dewi Lestari','081234567805')])
            c.executemany('INSERT INTO pengguna (nama,username,password_hash,role) VALUES (%s,%s,%s,%s)',
                          [('Admin Adon Manis','admin',generate_password_hash(admin_password),'admin'),
                           ('Pemilik Adon Manis','pemilik',generate_password_hash(owner_password),'pemilik')])
        server.commit()
    finally:
        server.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--test', action='store_true', help='Inisialisasi database khusus pengujian, nama wajib berakhir _test.')
    args = parser.parse_args()
    load_dotenv(ROOT / '.env')
    config = {k: os.getenv(k, d) for k,d in [('DB_HOST','127.0.0.1'),('DB_PORT','3306'),('DB_NAME','adon_manis'),('DB_USER','root'),('DB_PASSWORD','')]}
    if args.test:
        config['DB_NAME'] = os.getenv('TEST_DB_NAME','adon_manis_test')
        if not config['DB_NAME'].endswith('_test'):
            raise ValueError('Database pengujian wajib berakhir _test.')
    admin = getpass.getpass('Password baru akun admin (minimal 10 karakter): ')
    owner = getpass.getpass('Password baru akun pemilik (minimal 10 karakter): ')
    initialize(config, admin, owner)
    print('Database berhasil dibuat. Username: admin dan pemilik. Lima pelanggan adalah data contoh fiktif.')
