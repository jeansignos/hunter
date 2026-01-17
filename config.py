import os
from datetime import timedelta

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
    
    # Railway fornece DATABASE_URL automaticamente para PostgreSQL
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = database_url or 'sqlite:///mir4_market.db'
    
    # Força HTTPS
    PREFERRED_URL_SCHEME = 'https'


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
