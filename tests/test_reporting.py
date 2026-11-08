from datetime import datetime
from decimal import Decimal
import re
import pytest
from app.db import get_db, query
from app.services import change_status
from app.reporting import select_orders, summarize
from conftest import login, token
from test_core import order, form, sql


def dated(app,key,customer,created,completed=None,channel='1'):
    oid=order(app,key,id_pelanggan=str(customer),id_channel=channel)
    with app.app_context():
        if completed:
            change_status(oid,'diproses',1);change_status(oid,'selesai',1)
        with get_db().cursor() as c:
            c.execute('UPDATE pesanan SET waktu_masuk=%s,waktu_selesai=%s WHERE id_pesanan=%s',(created,completed,oid))
        get_db().commit()
    return oid


def test_report_authentication(client):
    assert client.get('/laporan').location.endswith('/login')


def test_owner_read_report_only(client):
    login(client,'pemilik','TestOwner123!')
    assert client.get('/laporan').status_code==200
    assert client.get('/pesanan').status_code==403
    assert client.get('/pesanan/baru').status_code==403


@pytest.mark.parametrize('query_string',['mulai=2026-02-30','mulai=2026-10-21&akhir=2026-10-20','akhir=9999-12-31','channel=999','status=x','basis=x','mulai=abc'])
def test_bad_filters(client,query_string):
    login(client)
    assert client.get('/laporan?'+query_string).status_code==400


def test_end_date_inclusive_and_next_day_excluded(app):
    a=dated(app,'a',1,'2026-10-20 00:00:00')
    b=dated(app,'b',2,'2026-10-20 23:59:59')
    dated(app,'c',3,'2026-10-21 00:00:00')
    with app.app_context():
        rows,_,_=select_orders({'mulai':'2026-10-20','akhir':'2026-10-20'})
    assert [r['id_pesanan'] for r in rows]==[b,a]


def test_completion_date_differs_from_record_date(app):
    dated(app,'a',1,'2026-10-19 23:00:00','2026-10-20 01:00:00')
    with app.app_context():
        f={'mulai':'2026-10-20','akhir':'2026-10-20'}
        assert not select_orders(f,True)[0]
        f['basis']='selesai'
        assert summarize(select_orders(f,True)[0])['revenue']==Decimal('65000')


def test_filter_combination_and_no_double_count(app,client):
    a=dated(app,'a',1,'2026-10-20 10:00:00','2026-10-20 11:00:00')
    dated(app,'b',2,'2026-10-20 12:00:00',channel='2')
    with app.app_context():
        rows,_,_=select_orders({'q':f'AM-{a:04d}','channel':'1','status':'selesai','mulai':'2026-10-20'})
        summary=summarize(rows)
        assert summary['total']==1 and summary['revenue']==Decimal('65000')
        assert summary['groups']==[('WhatsApp',{'jumlah':1,'selesai':1,'nilai':Decimal('65000')})]
    login(client)
    for path in ['/', '/pesanan','/laporan']:
        page=client.get(path+'?channel=1&status=selesai&mulai=2026-10-20&akhir=2026-10-20')
        assert page.status_code==200 and 'Rp65.000' in page.text and 'Budi Santoso' not in page.text


def test_empty_report(client):
    login(client)
    page=client.get('/laporan')
    assert '0 pesanan' in page.text and 'Rp0' in page.text and 'Tidak ada pesanan' in page.text


def test_report_cancellation_excluded_and_not_multiplied_by_details(app,client):
    a=order(app,'a');b=order(app,'b',id_pelanggan='2')
    with app.app_context():
        change_status(a,'diproses',1);change_status(a,'selesai',1)
        change_status(b,'dibatalkan',1,'bahan_habis')
        summary=summarize(select_orders({})[0])
        assert summary['total']==2 and summary['revenue']==Decimal('65000')
    login(client)
    assert 'data-testid="report-value">Rp65.000' in client.get('/laporan').text


def test_e2e_login_multi_item_dashboard_report(app,client):
    login(client)
    assert 'data-testid="report-count">0 pesanan' in client.get('/laporan').text
    page=client.get('/pesanan/baru').text
    data=form()
    for key in ['_csrf','kunci_input']:
        data[key]=re.search('name="'+key+'" value="([^"]+)"',page).group(1)
    response=client.post('/pesanan/baru',data=data)
    assert response.status_code==302
    oid=int(response.location.rsplit('/',1)[1])
    assert len(sql(app,'SELECT * FROM detail_pesanan WHERE id_pesanan=%s',(oid,)))==2
    assert 'Rp65.000' in client.get('/pesanan').text
    with app.app_context():
        first=summarize(select_orders({})[0]);assert first['counts']['diterima']==1 and first['revenue']==0
    for status in ['diproses','selesai']:
        client.post(f'/pesanan/{oid}/status',data={'_csrf':token(client,response.location),'status':status})
    assert 'Rp65.000' in client.get('/').text
    assert 'data-testid="report-value">Rp65.000' in client.get('/laporan?basis=selesai').text
    assert len(sql(app,'SELECT * FROM status_log WHERE id_pesanan=%s',(oid,)))==3
