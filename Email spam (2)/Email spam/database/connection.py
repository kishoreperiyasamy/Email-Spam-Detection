import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from config import Config

_connection_pool = None

def init_connection_pool():
    global _connection_pool
    if _connection_pool is None:
        try:
            _connection_pool = pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=20,
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                dbname=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                connect_timeout=5
            )
            print(f"[DB] PostgreSQL Connection Pool established for {Config.DB_NAME}")
        except Exception as e:
            print(f"[DB Error] Failed to initialize connection pool: {e}")
            raise e

def get_connection():
    global _connection_pool
    if _connection_pool is None:
        init_connection_pool()
    return _connection_pool.getconn()

def release_connection(conn):
    global _connection_pool
    if _connection_pool and conn:
        _connection_pool.putconn(conn)

@contextmanager
def get_db_connection():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        release_connection(conn)

@contextmanager
def get_db_cursor(commit=True):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            yield cur
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        release_connection(conn)

def init_db():
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    if not os.path.exists(schema_path):
        print(f"[DB] schema.sql not found at {schema_path}")
        return

    print("[DB] Initializing database schema...")
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
    print("[DB] Schema initialized and default users verified.")
