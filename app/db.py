import pymysql
from flask import current_app, g


def connect(config, database=True):
    return pymysql.connect(
        host=config['DB_HOST'], port=int(config['DB_PORT']),
        user=config['DB_USER'], password=config['DB_PASSWORD'],
        database=config['DB_NAME'] if database else None,
        charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
        connect_timeout=3, read_timeout=5, write_timeout=5,
        init_command="SET SESSION sql_mode='STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION'",
    )


def get_db():
    if 'db' not in g:
        g.db = connect(current_app.config)
    return g.db


def query(sql, args=(), one=False):
    with get_db().cursor() as cur:
        cur.execute(sql, args)
        return cur.fetchone() if one else cur.fetchall()


def close_db(error=None):
    connection = g.pop('db', None)
    if connection:
        connection.close()
