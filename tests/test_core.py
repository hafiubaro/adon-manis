import re
from decimal import Decimal
from datetime import timedelta
import pytest
import pymysql
from werkzeug.datastructures import MultiDict
from app.db import connect,query,get_db
from app.services import create_order,change_status,ValidationError,DuplicateWarning,now_jakarta
from conftest import token,login


def form(**kw):
    data=MultiDict([('id_pelanggan','1'),('id_channel','1'),('id_produk','1'),('jumlah','2'),('id_produk','3'),('jumlah','1')])
    for key,value in kw.items():data[key]=value
    return data


def sql(app, statement, args=(), one=False):
    with app.app_context():return query(statement,args,one=one)


def order(app, key='test-key', **kw):
    with app.app_context():return create_order(form(**kw),1,key)


def test_database_connection(app):
    assert sql(app,'SELECT DATABASE() db',one=True)['db'].endswith('_test')
    assert len(sql(app,'SHOW TABLES')) == 7


def test_login_correct_and_logout(client):
    assert login(client).status_code == 302
    assert client.get('/').status_code == 200
    assert client.post('/logout',data={'_csrf':token(client,'/')}).status_code == 302
    assert client.get('/pesanan').location.endswith('/login')


def test_wrong_password_rejected(client):
    assert login(client,password='salah').status_code == 401
    assert client.get('/').status_code == 302


def test_protected_page_redirect(client):
    assert client.get('/pesanan').location.endswith('/login')


def test_csrf_required(client):
    assert client.post('/login',data={'username':'admin','password':'TestAdmin123!'}).status_code == 400


def test_owner_cannot_mutate_or_open_admin_page(client):
    login(client,'pemilik','TestOwner123!')
    assert client.get('/').status_code == 200
    assert client.get('/pelanggan').status_code == 403
    assert client.post('/pelanggan/baru',data={'_csrf':token(client,'/'),'nama':'Tidak boleh'}).status_code == 403
    assert client.get('/pesanan/baru').status_code == 403


def test_customer_create_read_update_delete(client,app):
    login(client)
    assert client.post('/pelanggan/baru',data={'_csrf':token(client,'/pelanggan/baru'),'nama':'Uji Pelanggan','no_telepon':'08199999999'}).status_code==302
    assert 'Uji Pelanggan' in client.get('/pelanggan').text
    cid=sql(app,'SELECT id_pelanggan FROM pelanggan WHERE no_telepon=%s',('08199999999',),True)['id_pelanggan']
    assert client.post(f'/pelanggan/{cid}/edit',data={'_csrf':token(client,'/pelanggan'),'nama':'Pelanggan Diperbarui','no_telepon':'08199999999'}).status_code==302
    assert sql(app,'SELECT nama FROM pelanggan WHERE id_pelanggan=%s',(cid,),True)['nama']=='Pelanggan Diperbarui'
    assert client.post(f'/pelanggan/{cid}/hapus',data={'_csrf':token(client,'/pelanggan')}).status_code==302
    assert not sql(app,'SELECT * FROM pelanggan WHERE id_pelanggan=%s',(cid,))


@pytest.mark.parametrize('name,phone',[('','08199999999'),('A','08199999999'),('Nama','abc'),('Nama','081')])
def test_customer_validation(client,name,phone):
    login(client)
    assert client.post('/pelanggan/baru',data={'_csrf':token(client,'/pelanggan/baru'),'nama':name,'no_telepon':phone}).status_code==400


def test_duplicate_phone_normalized(client):
    login(client)
    response=client.post('/pelanggan/baru',data={'_csrf':token(client,'/pelanggan/baru'),'nama':'Siti Lain','no_telepon':'+62 812-3456-7801'})
    assert response.status_code==400 and 'sudah digunakan' in response.text


def test_delete_customer_with_order_blocked(client,app):
    order(app);login(client)
    response=client.post('/pelanggan/1/hapus',data={'_csrf':token(client,'/pelanggan')},follow_redirects=True)
    assert 'tidak dapat dihapus' in response.text
    assert sql(app,'SELECT * FROM pelanggan WHERE id_pelanggan=1')


def test_create_order_total_details_initial_log(app):
    oid=order(app)
    assert sql(app,'SELECT total_harga,status FROM pesanan WHERE id_pesanan=%s',(oid,),True)=={'total_harga':Decimal('65000.00'),'status':'diterima'}
    assert len(sql(app,'SELECT * FROM detail_pesanan WHERE id_pesanan=%s',(oid,)))==2
    assert len(sql(app,'SELECT * FROM status_log WHERE id_pesanan=%s',(oid,)))==1


@pytest.mark.parametrize('qty',['0','-1','1.5','abc','1000'])
def test_quantity_validation_no_partial_order(app,qty):
    with app.app_context():
        with pytest.raises(ValidationError):create_order(form(jumlah=qty),1,'invalid')
    assert not sql(app,'SELECT * FROM pesanan')


@pytest.mark.parametrize('field,value',[('id_pelanggan','9999'),('id_channel','9999'),('id_produk','9999')])
def test_unknown_foreign_reference_rejected(app,field,value):
    with app.app_context():
        with pytest.raises(ValidationError):create_order(form(**{field:value}),1,'invalid-reference')
    assert not sql(app,'SELECT * FROM pesanan')


def test_duplicate_warning_then_override(app):
    order(app)
    with app.app_context():
        with pytest.raises(DuplicateWarning):create_order(form(id_channel='2'),1,'another')
        oid=create_order(form(id_channel='2',konfirmasi_duplikat='ya',catatan_duplikat='Pesanan tambahan telah dikonfirmasi'),1,'another')
    assert len(sql(app,'SELECT * FROM pesanan'))==2
    assert sql(app,'SELECT catatan_duplikat FROM pesanan WHERE id_pesanan=%s',(oid,),True)['catatan_duplikat']


def test_same_submit_key_no_double_insert(app):
    assert order(app)==order(app)
    assert len(sql(app,'SELECT * FROM pesanan'))==1


def test_status_forward_and_log(app):
    oid=order(app)
    with app.app_context():
        change_status(oid,'diproses',1);change_status(oid,'selesai',1)
    p=sql(app,'SELECT * FROM pesanan WHERE id_pesanan=%s',(oid,),True)
    assert p['status']=='selesai' and p['waktu_selesai'] is not None
    assert len(sql(app,'SELECT * FROM status_log WHERE id_pesanan=%s',(oid,)))==3


def test_status_skip_and_backward_rejected(app):
    oid=order(app)
    with app.app_context():
        with pytest.raises(ValidationError):change_status(oid,'selesai',1)
        change_status(oid,'diproses',1)
        with pytest.raises(ValidationError):change_status(oid,'diterima',1)


def test_cancel_materials_and_reason_saved(app):
    oid=order(app)
    with app.app_context():change_status(oid,'dibatalkan',1,'bahan_habis','Tepung habis')
    assert 'Tepung habis' in sql(app,'SELECT alasan_pembatalan FROM pesanan WHERE id_pesanan=%s',(oid,),True)['alasan_pembatalan']
    assert len(sql(app,'SELECT * FROM status_log WHERE id_pesanan=%s AND alasan IS NOT NULL',(oid,)))==1


def test_cancel_no_response_before_30_minutes_rejected(app):
    oid=order(app)
    with app.app_context():
        with pytest.raises(ValidationError):change_status(oid,'dibatalkan',1,'tidak_merespons')


def test_cancel_no_response_after_30_minutes(app):
    oid=order(app)
    with app.app_context():
        with get_db().cursor() as cur:cur.execute('UPDATE pesanan SET waktu_masuk=%s WHERE id_pesanan=%s',(now_jakarta()-timedelta(minutes=31),oid))
        get_db().commit();change_status(oid,'dibatalkan',1,'tidak_merespons')
    assert sql(app,'SELECT status FROM pesanan WHERE id_pesanan=%s',(oid,),True)['status']=='dibatalkan'


def test_completed_order_cannot_cancel(app):
    oid=order(app)
    with app.app_context():
        change_status(oid,'diproses',1);change_status(oid,'selesai',1)
        with pytest.raises(ValidationError):change_status(oid,'dibatalkan',1,'bahan_habis')


def test_summary_excludes_cancelled_and_pending(client,app):
    a=order(app,'a');b=order(app,'b',id_pelanggan='2');order(app,'c',id_pelanggan='3')
    with app.app_context():
        change_status(a,'diproses',1);change_status(a,'selesai',1);change_status(b,'dibatalkan',1,'bahan_habis')
    login(client,'pemilik','TestOwner123!')
    page=client.get('/').text
    assert 'Rp65.000' in page
    assert sql(app,"SELECT SUM(total_harga) total FROM pesanan WHERE status='selesai'",one=True)['total']==Decimal('65000')


def test_transaction_rollback_if_log_insert_fails(app):
    with app.app_context():
        with get_db().cursor() as c:c.execute("CREATE TRIGGER fail_log BEFORE INSERT ON status_log FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='uji rollback'")
        try:
            with pytest.raises(pymysql.MySQLError):create_order(form(),1,'rollback-key')
        finally:
            with get_db().cursor() as c:c.execute('DROP TRIGGER fail_log')
        assert not query('SELECT * FROM pesanan')
        assert not query('SELECT * FROM detail_pesanan')


def test_http_order_flow_and_tampered_total(client,app):
    login(client)
    page=client.get('/pesanan/baru').text
    data=form()
    data['_csrf']=re.search(r'name="_csrf" value="([^"]+)"',page).group(1)
    data['kunci_input']=re.search(r'name="kunci_input" value="([^"]+)"',page).group(1)
    data['total_harga']='1'
    response=client.post('/pesanan/baru',data=data)
    assert response.status_code==302
    detail=client.get(response.location)
    assert detail.status_code==200 and 'Rp65.000' in detail.text
    assert sql(app,'SELECT total_harga FROM pesanan',one=True)['total_harga']==Decimal('65000')


def test_xss_escaped_and_sql_injection_login_rejected(client):
    assert login(client,"' OR 1=1 --",'x').status_code==401
    login(client)
    client.post('/pelanggan/baru',data={'_csrf':token(client,'/pelanggan/baru'),'nama':'<script>alert(1)</script>','no_telepon':''})
    page=client.get('/pelanggan').text
    assert '&lt;script&gt;' in page and '<script>alert(1)</script>' not in page


def test_missing_order_returns_404(client):
    login(client)
    assert client.get('/pesanan/999999').status_code==404
