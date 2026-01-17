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


@auth_bp.route('/login-ajax', methods=['POST'])
def login_ajax():
    """Login via AJAX para modal"""
    from flask import jsonify
    
    if current_user.is_authenticated:
        return jsonify({'success': True, 'message': 'Já está logado'})
    
    login_input = request.form.get('login', '').strip().lower()
    password = request.form.get('password', '')
    remember = request.form.get('remember_me') == 'on'
    
    if not login_input or not password:
        return jsonify({'success': False, 'message': 'Preencha todos os campos'})
    
    # Tenta encontrar por email primeiro, depois por username
    user = User.query.filter_by(email=login_input).first()
    if not user:
        user = User.query.filter(User.username.ilike(login_input)).first()
    
    if user is None or not user.check_password(password):
        return jsonify({'success': False, 'message': 'Email/usuário ou senha incorretos'})
    
    if not user.is_active:
        return jsonify({'success': False, 'message': 'Sua conta foi desativada'})
    
    login_user(user, remember=remember)
    user.update_last_login()
    
    return jsonify({'success': True, 'message': f'Bem-vindo, {user.username}!'})


@auth_bp.route('/register-ajax', methods=['POST'])
def register_ajax():
    """Registro via AJAX para modal"""
    from flask import jsonify
    
    if current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'Você já está logado'})
    
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    password2 = request.form.get('password2', '')
    
    # Validações
    if not username or not email or not password:
        return jsonify({'success': False, 'message': 'Preencha todos os campos'})
    
    if len(username) < 3:
        return jsonify({'success': False, 'message': 'Nome de usuário deve ter pelo menos 3 caracteres'})
    
    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Senha deve ter pelo menos 6 caracteres'})
    
    if password != password2:
        return jsonify({'success': False, 'message': 'As senhas não coincidem'})
    
    # Verifica se já existe
    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': 'Este email já está cadastrado'})
    
    if User.query.filter(User.username.ilike(username)).first():
        return jsonify({'success': False, 'message': 'Este nome de usuário já está em uso'})
    
    try:
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Faz login automático
        login_user(user, remember=True)
        
        return jsonify({'success': True, 'message': 'Conta criada com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Erro ao criar conta. Tente novamente.'})
