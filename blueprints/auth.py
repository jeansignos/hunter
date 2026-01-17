from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from forms import LoginForm, RegistrationForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login - aceita email ou username"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        login_input = form.login.data.strip().lower()
        
        # Tenta encontrar por email primeiro, depois por username
        user = User.query.filter_by(email=login_input).first()
        if not user:
            user = User.query.filter(User.username.ilike(login_input)).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Email/usuário ou senha incorretos.', 'error')
            return render_template('auth/login.html', form=form)
        
        if not user.is_active:
            flash('Sua conta foi desativada. Entre em contato com o suporte.', 'error')
            return render_template('auth/login.html', form=form)
        
        login_user(user, remember=form.remember_me.data)
        user.update_last_login()
        
        flash(f'Bem-vindo, {user.username}!', 'success')
        
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('index'))
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data.lower()
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Conta criada com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('index'))


@auth_bp.route('/profile')
@login_required
def profile():
    """Página de perfil do usuário"""
    return render_template('auth/profile.html')
