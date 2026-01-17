from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Modelo de usuário com suporte a Premium"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Dados do usuário
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Sistema Premium
    is_premium = db.Column(db.Boolean, default=False)
    premium_activated_at = db.Column(db.DateTime, nullable=True)
    premium_expires_at = db.Column(db.DateTime, nullable=True)
    
    # Admin
    is_admin = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        """Gera hash da senha usando bcrypt"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.password_hash, password)
    
    def activate_premium(self, days=30):
        """Ativa o plano Premium por X dias"""
        self.is_premium = True
        self.premium_activated_at = datetime.utcnow()
        self.premium_expires_at = datetime.utcnow() + timedelta(days=days)
        db.session.commit()
    
    def deactivate_premium(self):
        """Desativa o plano Premium"""
        self.is_premium = False
        self.premium_expires_at = None
        db.session.commit()
    
    @property
    def premium_status(self):
        """Retorna o status atual do Premium"""
        if not self.is_premium:
            return 'free'
        
        if self.premium_expires_at and datetime.utcnow() > self.premium_expires_at:
            # Expirou - desativar automaticamente
            self.is_premium = False
            db.session.commit()
            return 'expired'
        
        return 'active'
    
    @property
    def premium_days_remaining(self):
        """Retorna dias restantes do Premium"""
        if not self.is_premium or not self.premium_expires_at:
            return 0
        
        remaining = self.premium_expires_at - datetime.utcnow()
        return max(0, remaining.days)
    
    def has_premium_access(self):
        """Verifica se o usuário tem acesso Premium ativo"""
        return self.premium_status == 'active' or self.is_admin
    
    def update_last_login(self):
        """Atualiza data do último login"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<User {self.username}>'


class UserSearch(db.Model):
    """Histórico de buscas do usuário (para analytics futuro)"""
    __tablename__ = 'user_searches'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    search_params = db.Column(db.Text)  # JSON dos parâmetros de busca
    results_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('searches', lazy='dynamic'))


class PremiumActivation(db.Model):
    """Log de ativações Premium (para auditoria)"""
    __tablename__ = 'premium_activations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Admin que ativou
    days_granted = db.Column(db.Integer, default=30)
    reason = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('activations', lazy='dynamic'))
    admin = db.relationship('User', foreign_keys=[activated_by])
