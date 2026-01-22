import os
from datetime import timedelta

def get_database_url():
    """Constrói a URL do banco de dados para Railway"""
    # Tenta usar DATABASE_URL primeiro
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # Corrige formato postgres:// para postgresql://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        print(f"[DB] Usando DATABASE_URL do ambiente")
        return database_url
    
    # Railway: tenta construir a URL a partir das variáveis individuais
    pg_user = os.environ.get('PGUSER') or os.environ.get('POSTGRES_USER')
    pg_pass = os.environ.get('PGPASSWORD') or os.environ.get('POSTGRES_PASSWORD')
    pg_host = os.environ.get('PGHOST') or os.environ.get('RAILWAY_TCP_PROXY_DOMAIN')
    pg_port = os.environ.get('PGPORT', '5432')
    pg_db = os.environ.get('PGDATABASE') or os.environ.get('POSTGRES_DB')
    
    if all([pg_user, pg_pass, pg_host, pg_db]):
        url = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
        print(f"[DB] Construindo URL do Postgres a partir das variáveis PG*")
        return url
    
    # Fallback para SQLite (não recomendado em produção)
    print("[DB] AVISO: Usando SQLite - dados serão perdidos a cada deploy!")
    return 'sqlite:///mir4_market.db'


class Config:
    """Configuração base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações de cache
    CACHE_EXPIRY_MINUTES = int(os.environ.get('CACHE_EXPIRY_MINUTES', 720))
    CACHE_STATUS_EXPIRY = 1440
    
    # Premium
    PREMIUM_TRIAL_DAYS = int(os.environ.get('PREMIUM_TRIAL_DAYS', 30))
    
    # CoinMarketCap
    CMC_API_KEY = os.environ.get('CMC_API_KEY', '051cc3b82a9446fa9771425ab96bd91b')
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # WTF Forms
    WTF_CSRF_ENABLED = True


class DevelopmentConfig(Config):
    """Configuração de desenvolvimento"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///mir4_market.db'


class ProductionConfig(Config):
    """Configuração de produção"""
    DEBUG = False
    PREFERRED_URL_SCHEME = 'https'
    SQLALCHEMY_DATABASE_URI = get_database_url()


class TestingConfig(Config):
    """Configuração de testes"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
