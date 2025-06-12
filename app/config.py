from dotenv import load_dotenv
from os import getenv

load_dotenv()


DBUSER = getenv('DB_USER')
DBNAME = getenv('DB_NAME')
DBPORT = getenv('DB_PORT')
DBHOST = getenv('DB_HOST')
DBPASS = getenv('DB_PASS')
SECRET_KEY = getenv('SECRET')

from typing import Dict, Any

DATABASE: Dict[str, Any] = {
    'engine': 'playhouse.pool.PooledPostgresqlDatabase',
    'name': DBNAME,
    'user': DBUSER,
    'password': DBPASS,
    'host': DBHOST,
    'max_connections': 32,
    'stale_timeout': 600,
}
