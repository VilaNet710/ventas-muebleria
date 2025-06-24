from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar si existe sesión activa
        if 'user' not in session:
            flash('Debes iniciar sesión para acceder a esta página', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Primero verificar autenticación
        if 'user' not in session:
            flash('Debes iniciar sesión para acceder a esta página', 'error')
            return redirect(url_for('login'))
        
        # Verificar que sea administrador
        if session.get('tipo') != 'administrador':
            flash('No tienes permisos para acceder a esta página', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def super_admin_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar autenticación
        if 'user' not in session:
            flash('Debes iniciar sesión para acceder a esta página', 'error')
            return redirect(url_for('login'))
        
        # Verificar que sea administrador
        if session.get('tipo') != 'administrador':
            flash('No tienes permisos para acceder a esta página', 'error')
            return redirect(url_for('dashboard'))
        
        # Verificar permisos de super admin
        if not session.get('super_admin', False):
            flash('Solo el administrador principal puede realizar esta acción', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def user_only_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar autenticación
        if 'user' not in session:
            flash('Debes iniciar sesión para acceder a esta página', 'error')
            return redirect(url_for('login'))
        
        # Verificar que sea usuario regular (no administrador)
        if session.get('tipo') != 'usuario':
            flash('Esta sección es solo para usuarios', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function
