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
            if Config.DATABASE_URL:
                _connection_pool = pool.ThreadedConnectionPool(
                    minconn=1,
                    maxconn=20,
                    dsn=Config.DATABASE_URL,
                    connect_timeout=15
                )
                print("[DB] PostgreSQL Connection Pool established via DATABASE_URL (Supabase/Remote)")
            else:
                _connection_pool = pool.ThreadedConnectionPool(
                    minconn=1,
                    maxconn=20,
                    host=Config.DB_HOST,
                    port=Config.DB_PORT,
                    dbname=Config.DB_NAME,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD,
                    sslmode=Config.DB_SSLMODE,
                    connect_timeout=15
                )
                print(f"[DB] PostgreSQL Connection Pool established for {Config.DB_NAME} at {Config.DB_HOST}:{Config.DB_PORT}")
        except Exception as e:
            print(f"[DB Error] Failed to initialize connection pool: {e}")
            _connection_pool = None
            raise e

def get_connection():
    global _connection_pool
    if _connection_pool is None:
        init_connection_pool()
    try:
        conn = _connection_pool.getconn()
        if conn and getattr(conn, 'closed', 0) != 0:
            try:
                _connection_pool.putconn(conn, close=True)
            except Exception:
                pass
            conn = _connection_pool.getconn()
        return conn
    except Exception as e:
        # If pool became unhealthy, reset it and retry once
        print(f"[DB Pool Warning] Connection failed ({e}), refreshing pool...")
        _connection_pool = None
        init_connection_pool()
        return _connection_pool.getconn()

def release_connection(conn):
    global _connection_pool
    if _connection_pool and conn:
        try:
            _connection_pool.putconn(conn)
        except Exception:
            pass

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
