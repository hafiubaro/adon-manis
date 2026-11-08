"""Penguatan retest pencarian literal dan error handling, di luar 21 TC LKM."""
import pytest,pymysql
from app.db import get_db,query
from conftest import login
from test_core import order

@pytest.mark.parametrize('name,needle',[('Diskon 10%','%'),('Nama_Uji','_'),('Nama!Uji','!')])
def test_literal_special_characters_preserved(app,client,name,needle):
    with app.app_context():
        with get_db().cursor() as c:c.execute('UPDATE pelanggan SET nama=%s WHERE id_pelanggan=1',(name,))
        get_db().commit()
    order(app,'a');order(app,'b',id_pelanggan='2');login(client)
    for path in ['/pesanan','/laporan','/']:
        text=client.get(path,query_string={'q':needle}).text
        assert name in text and 'Budi Santoso' not in text


def test_other_sql_errors_not_hidden(app,client,monkeypatch):
    csrf=client.get('/login')
    with client.session_transaction() as s:token=s['_csrf']
    def wrong_query(*args,**kwargs):raise pymysql.OperationalError(1054,'Kolom tidak dikenal')
    monkeypatch.setattr('app.auth.query',wrong_query)
    with pytest.raises(pymysql.OperationalError):client.post('/login',data={'_csrf':token,'username':'admin','password':'x'})
