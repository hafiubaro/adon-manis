"""Kasus Modul 9: ID TC konsisten dengan LKM; tidak ada hasil pengguna manusia."""
import re
from datetime import datetime,timedelta
from decimal import Decimal
import pytest,pymysql
from werkzeug.datastructures import MultiDict
from app.db import query,get_db
from app.services import create_order,change_status,ValidationError
from conftest import login,token
from test_core import form,order,sql
from test_reporting import dated


def submit(client,data):
    page=client.get('/pesanan/baru').text
    for key in ['_csrf','kunci_input']:
        data[key]=re.search('name="'+key+'" value="([^"]+)"',page).group(1)
    return client.post('/pesanan/baru',data=data)


def test_TC01_login_valid(client):
    assert login(client).status_code==302
    assert client.get('/').status_code==200


def test_TC02_customer_crud(client,app):
    login(client)
    r=client.post('/pelanggan/baru',data={'_csrf':token(client,'/pelanggan'),'nama':'Pelanggan Uji M9','no_telepon':'081299999999'})
    assert r.status_code==302
    row=sql(app,'SELECT * FROM pelanggan WHERE no_telepon=%s',('081299999999',),True);cid=row['id_pelanggan']
    assert 'Pelanggan Uji M9' in client.get('/pelanggan').text
    client.post(f'/pelanggan/{cid}/edit',data={'_csrf':token(client,'/pelanggan'),'nama':'Nama Diperbarui','no_telepon':'081299999999'})
    assert sql(app,'SELECT nama FROM pelanggan WHERE id_pelanggan=%s',(cid,),True)['nama']=='Nama Diperbarui'
    client.post(f'/pelanggan/{cid}/hapus',data={'_csrf':token(client,'/pelanggan')})
    assert not sql(app,'SELECT * FROM pelanggan WHERE id_pelanggan=%s',(cid,))


def test_TC03_multi_item_total(client,app):
    login(client);r=submit(client,form(total_harga='1'))
    assert r.status_code==302
    row=sql(app,'SELECT * FROM pesanan',one=True)
    assert row['total_harga']==Decimal('65000') and row['status']=='diterima'
    assert len(sql(app,'SELECT * FROM detail_pesanan'))==2


def test_TC04_status_and_log(client,app):
    oid=order(app);login(client)
    for status in ['diproses','selesai']:
        r=client.post(f'/pesanan/{oid}/status',data={'_csrf':token(client,f'/pesanan/{oid}'),'status':status})
        assert r.status_code==302
    row=sql(app,'SELECT status,waktu_selesai FROM pesanan',one=True)
    assert row['status']=='selesai' and row['waktu_selesai']
    assert len(sql(app,'SELECT * FROM status_log'))==3


def test_TC05_dashboard_report_and_cancelled(app,client):
    a=order(app,'a');b=order(app,'b',id_pelanggan='2')
    with app.app_context():
        change_status(a,'diproses',1);change_status(a,'selesai',1)
        change_status(b,'dibatalkan',1,'bahan_habis')
    login(client)
    assert 'Rp65.000' in client.get('/').text
    page=client.get('/laporan').text
    assert 'data-testid="report-count">2 pesanan' in page
    assert 'data-testid="report-value">Rp65.000' in page
    assert sql(app,"SELECT SUM(total_harga) n FROM pesanan WHERE status='selesai'",one=True)['n']==65000


def test_TC06_owner_reads_report(client):
    login(client,'pemilik','TestOwner123!')
    assert client.get('/laporan').status_code==200


def test_TC07_wrong_password(client):
    assert login(client,password='wrong').status_code==401
    assert client.get('/').status_code==302


def test_TC08_empty_customer_name(client,app):
    login(client)
    r=client.post('/pelanggan/baru',data={'_csrf':token(client,'/pelanggan'),'nama':''})
    assert r.status_code==400
    assert len(sql(app,'SELECT * FROM pelanggan'))==3


def test_TC09_no_customer(client,app):
    login(client);r=submit(client,form(id_pelanggan=''))
    assert r.status_code==400 and not sql(app,'SELECT * FROM pesanan')


def test_TC10_owner_cannot_input(client):
    login(client,'pemilik','TestOwner123!')
    assert client.get('/pesanan/baru').status_code==403
    assert client.post('/pesanan/baru',data={'_csrf':token(client,'/')}).status_code==403


@pytest.mark.parametrize('tc,qty,accepted',[('TC11','0',False),('TC12','1',True),('TC13','999',True),('TC14','1000',False)],ids=['TC11_qty0','TC12_qty1','TC13_qty999','TC14_qty1000'])
def test_quantity_boundary(app,client,tc,qty,accepted):
    login(client)
    data=MultiDict([('id_pelanggan','1'),('id_channel','1'),('id_produk','1'),('jumlah',qty)])
    response=submit(client,data)
    assert response.status_code==(302 if accepted else 400)
    rows=sql(app,'SELECT total_harga FROM pesanan')
    assert len(rows)==int(accepted)
    if accepted:assert rows[0]['total_harga']==Decimal('15000')*int(qty)


@pytest.mark.parametrize('tc,seconds,accepted',[('TC15',1799,False),('TC16',1800,True)],ids=['TC15_29m59s','TC16_30m00s'])
def test_cancel_time_boundary(app,monkeypatch,tc,seconds,accepted):
    instant=datetime(2026,10,27,10,0,0)
    monkeypatch.setattr('app.services.now_jakarta',lambda:instant)
    oid=order(app)
    with app.app_context():
        with get_db().cursor() as c:c.execute('UPDATE pesanan SET waktu_masuk=%s WHERE id_pesanan=%s',(instant-timedelta(seconds=seconds),oid))
        get_db().commit()
        if accepted:change_status(oid,'dibatalkan',1,'tidak_merespons')
        else:
            with pytest.raises(ValidationError):change_status(oid,'dibatalkan',1,'tidak_merespons')
        assert query('SELECT status FROM pesanan',one=True)['status']==('dibatalkan' if accepted else 'diterima')


def test_TC17_end_date_boundary(app,client):
    a=dated(app,'a',1,'2026-10-27 23:59:59')
    b=dated(app,'b',2,'2026-10-28 00:00:00')
    login(client);page=client.get('/pesanan?mulai=2026-10-27&akhir=2026-10-27').text
    assert f'AM-{a:04d}' in page and f'AM-{b:04d}' not in page


def test_TC18_rollback_and_foreign_key(app):
    with app.app_context():
        with get_db().cursor() as c:c.execute("CREATE TRIGGER m9_fail_log BEFORE INSERT ON status_log FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='uji rollback M9'")
        try:
            with pytest.raises(pymysql.MySQLError):create_order(form(),1,'m9-rollback')
        finally:
            with get_db().cursor() as c:c.execute('DROP TRIGGER m9_fail_log')
        assert not query('SELECT * FROM pesanan') and not query('SELECT * FROM detail_pesanan')
        with pytest.raises(ValidationError):create_order(form(id_pelanggan='99999'),1,'invalid-customer')
        assert not query('SELECT * FROM pesanan')


def test_TC19_non_ascii_csrf(client,app):
    app.config['PROPAGATE_EXCEPTIONS']=False
    token(client)
    r=client.post('/login',data={'_csrf':'rusak-漢','username':'admin','password':'anything'})
    assert r.status_code==400, f'Actual HTTP {r.status_code}; expected 400'
    assert 'Form kedaluwarsa' in r.text


def test_TC20_database_unavailable(client,app,monkeypatch):
    app.config['PROPAGATE_EXCEPTIONS']=False
    csrf=token(client)
    monkeypatch.setitem(app.config,'DB_PORT',1) # koneksi sungguhan ke port tanpa layanan, tidak mematikan DB lain
    r=client.post('/login',data={'_csrf':csrf,'username':'admin','password':'anything'})
    assert r.status_code==503, f'Actual HTTP {r.status_code}; expected 503'
    assert 'Database sementara tidak tersedia' in r.text
    assert 'password' not in r.text.lower() and 'Traceback' not in r.text


def test_TC21_literal_search(app,client):
    order(app,'a');order(app,'b',id_pelanggan='2');login(client)
    for path in ['/pesanan','/laporan','/']:
        r=client.get(path,query_string={'q':'%'})
        assert r.status_code==200
        assert 'Siti Aminah' not in r.text and 'Budi Santoso' not in r.text, 'Actual: wildcard returns unrelated customers'
