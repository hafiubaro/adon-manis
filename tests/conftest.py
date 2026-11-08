import os
import re
import sys
from pathlib import Path
import pytest
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import create_app
from app.db import connect


@pytest.fixture
def app():
    root = Path(__file__).resolve().parents[1]
    load_dotenv(root/'.env')
    dbname = os.getenv('TEST_DB_NAME','adon_manis_test')
    if not dbname.endswith('_test') or dbname == os.getenv('DB_NAME','adon_manis'):
        raise RuntimeError('Pengujian hanya boleh pada database berbeda dengan nama berakhir _test.')
    app = create_app({'TESTING':True,'DB_NAME':dbname})
    db = connect(app.config)
    with db.cursor() as c:
        for table in ['status_log','detail_pesanan','pesanan','pelanggan']:
            c.execute('DELETE FROM '+table)
        c.executemany('INSERT INTO pelanggan (id_pelanggan,nama,no_telepon) VALUES (%s,%s,%s)',[(1,'Siti Aminah','081234567801'),(2,'Budi Santoso','081234567802'),(3,'Rina Wati',None)])
        c.execute('UPDATE pengguna SET password_hash=%s WHERE username=%s',(generate_password_hash('TestAdmin123!'),'admin'))
        c.execute('UPDATE pengguna SET password_hash=%s WHERE username=%s',(generate_password_hash('TestOwner123!'),'pemilik'))
    db.commit();db.close()
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def token(client, path='/login'):
    page = client.get(path)
    match = re.search(r'name="_csrf" value="([^"]+)"',page.text)
    assert match, page.text
    return match.group(1)


def login(client, username='admin', password='TestAdmin123!'):
    return client.post('/login',data={'_csrf':token(client),'username':username,'password':password})
