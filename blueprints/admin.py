from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from models import db, User, PremiumActivation
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Decorator para verificar se usuário é admin"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Acesso negado. Área restrita a administradores.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@admin_required
def dashboard():
    """Painel de administração"""
    total_users = User.query.count()
    premium_users = User.query.filter_by(is_premium=True).count()
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html', 
                         total_users=total_users,
                         premium_users=premium_users,
                         recent_users=recent_users)


@admin_bp.route('/users')
@admin_required
def users_list():
    """Lista todos os usuários"""
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/users.html', users=users)


@admin_bp.route('/user/<int:user_id>/activate-premium', methods=['POST'])
@admin_required
def activate_premium(user_id):
    """Ativa Premium para um usuário"""
    user = User.query.get_or_404(user_id)
    days = request.form.get('days', 30, type=int)
    reason = request.form.get('reason', 'Ativação manual pelo admin')
    
    user.activate_premium(days=days)
    
    # Log da ativação
    activation = PremiumActivation(
        user_id=user.id,
        activated_by=current_user.id,
        days_granted=days,
        reason=reason
    )
    db.session.add(activation)
    db.session.commit()
    
    flash(f'Premium ativado para {user.username} por {days} dias.', 'success')
    return redirect(url_for('admin.users_list'))


@admin_bp.route('/user/<int:user_id>/deactivate-premium', methods=['POST'])
@admin_required
def deactivate_premium(user_id):
    """Desativa Premium de um usuário"""
    user = User.query.get_or_404(user_id)
    user.deactivate_premium()
    
    flash(f'Premium desativado para {user.username}.', 'success')
    return redirect(url_for('admin.users_list'))


@admin_bp.route('/user/<int:user_id>/toggle-active', methods=['POST'])
@admin_required
def toggle_user_active(user_id):
    """Ativa/desativa um usuário"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('Você não pode desativar sua própria conta.', 'error')
        return redirect(url_for('admin.users_list'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'ativado' if user.is_active else 'desativado'
    flash(f'Usuário {user.username} foi {status}.', 'success')
    return redirect(url_for('admin.users_list'))


@admin_bp.route('/user/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    """Promove/remove admin de um usuário"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('Você não pode remover seu próprio status de admin.', 'error')
        return redirect(url_for('admin.users_list'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = 'promovido a admin' if user.is_admin else 'removido de admin'
    flash(f'Usuário {user.username} foi {status}.', 'success')
    return redirect(url_for('admin.users_list'))


# API para ativar premium via AJAX
@admin_bp.route('/api/user/<int:user_id>/premium', methods=['POST'])
@admin_required
def api_activate_premium(user_id):
    """API para ativar premium"""
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}
    
    days = data.get('days', 30)
    reason = data.get('reason', 'Ativação via API')
    
    user.activate_premium(days=days)
    
    activation = PremiumActivation(
        user_id=user.id,
        activated_by=current_user.id,
        days_granted=days,
        reason=reason
    )
    db.session.add(activation)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Premium ativado para {user.username} por {days} dias',
        'premium_expires_at': user.premium_expires_at.isoformat() if user.premium_expires_at else None
    })
