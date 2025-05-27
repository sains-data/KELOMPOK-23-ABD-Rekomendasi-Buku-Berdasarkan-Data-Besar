# Superset specific config
ROW_LIMIT = 5000
SUPERSET_WEBSERVER_PORT = 8088 # Port internal Superset

# Flask App Builder configuration
# Your App secret key
SECRET_KEY = "your_strong_secret_key_here_too" # GANTI INI! Sama dengan di docker-compose

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://superset:supersetpassword@superset-db:5432/superset'

# Cache
CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_URL': 'redis://redis-airflow:6379/1', # Gunakan DB Redis yang berbeda dari Airflow
}
DATA_CACHE_CONFIG = CACHE_CONFIG

# Feature flags
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
    "DASHBOARD_NATIVE_FILTERS": True,
    "ENABLE_EXPLORE_DRAG_AND_DROP": True,
    "SQLLAB_BACKEND_PERSISTENCE": True,
}

# Jika ingin menghubungkan ke Hive melalui Trino/Presto (ini contoh, butuh setup Trino terpisah)
# Untuk koneksi langsung ke Hive dari Superset, bisa ditambahkan saat setup database di UI Superset
# Pastikan driver Hive (misal PyHive) terinstall di image Superset jika belum ada.
# Atau, bangun image Superset custom dengan driver yang dibutuhkan.