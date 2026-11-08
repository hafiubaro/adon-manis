import os
import secrets
import hmac
import pymysql
from pathlib import Path
from datetime import timedelta
from decimal import Decimal
from dotenv import load_dotenv
from flask import Flask, session, request, abort, render_template
from .db import close_db


def create_app(test_config=None):
    load_dotenv(Path(__file__).resolve().parents[1] / '.env')
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY', ''),
        DB_HOST=os.getenv('DB_HOST', '127.0.0.1'),
        DB_PORT=int(os.getenv('DB_PORT', '3306')),
        DB_NAME=os.getenv('DB_NAME', 'adon_manis'),
        DB_USER=os.getenv('DB_USER', 'root'),
        DB_PASSWORD=os.getenv('DB_PASSWORD', ''),
        SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
        MAX_CONTENT_LENGTH=1024 * 1024,
    )
    if test_config:
        app.config.update(test_config)
    if len(app.config['SECRET_KEY']) < 32 or app.config['SECRET_KEY'].startswith('ganti-'):
        raise RuntimeError('Isi SECRET_KEY acak minimal 32 karakter di .env. Baca README.md.')
    app.teardown_appcontext(close_db)

    def csrf_token():
        if '_csrf' not in session:
            session['_csrf'] = secrets.token_hex(32)
        return session['_csrf']
    app.jinja_env.globals['csrf_token'] = csrf_token

    @app.before_request
    def protect_csrf():
        if request.method == 'POST':
            expected = session.get('_csrf', '')
            actual = request.form.get('_csrf', '')
            valid_tokens = (isinstance(expected, str) and isinstance(actual, str)
                            and len(expected) == 64 and len(actual) == 64
                            and expected.isascii() and actual.isascii())
            if not valid_tokens or not hmac.compare_digest(expected, actual):
                abort(400, description='Form kedaluwarsa atau token tidak valid. Muat ulang halaman.')

    @app.errorhandler(pymysql.OperationalError)
    @app.errorhandler(pymysql.InterfaceError)
    def database_unavailable(error):
        # Tangani hanya kegagalan koneksi, bukan error SQL/aturan data lain.
        code = error.args[0] if error.args else None
        if code not in (0, 2002, 2003, 2006, 2013, 2055):
            raise error
        app.logger.warning('Koneksi database tidak tersedia; kode %s', code)
        return render_template('database_unavailable.html'), 503

    @app.template_filter('rupiah')
    def rupiah(value):
        return 'Rp' + format(Decimal(value or 0), ',.0f').replace(',', '.')

    @app.errorhandler(400)
    @app.errorhandler(403)
    @app.errorhandler(404)
    @app.errorhandler(409)
    def error_page(error):
        return render_template('error.html', error=error), error.code

    from .auth import bp as auth_bp
    from .customers import bp as customers_bp
    from .orders import bp as orders_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(orders_bp)
    return app
