from flask import request, redirect, url_for, Blueprint, session, flash
from models.administrador_model import Administrador
from views import administrador_view
from decorators import login_required, admin_required, super_admin_required

administrador_bp = Blueprint('administrador', __name__, url_prefix="/administradores")

@administrador_bp.route("/")
@admin_required
def index():
    administradores = Administrador.get_all()
    return administrador_view.list(administradores)

@administrador_bp.route("/create", methods=['GET', 'POST'])
@super_admin_required
def create():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        telefono = request.form['telefono']
        
        # Verificar si el email ya existe
        administradores = Administrador.get_all()
        for admin in administradores:
            if admin.email == email:
                flash('El email ya está registrado', 'error')
                return administrador_view.create()

        administrador = Administrador(nombre, email, password, telefono, super_admin=False)
        administrador.save()
        flash('Administrador creado exitosamente', 'success')
        return redirect(url_for('administrador.index'))

    return administrador_view.create()

@administrador_bp.route("/edit/<int:id>", methods=['GET', 'POST'])
@admin_required
def edit(id):
    administrador = Administrador.get_by_id(id)
    if not administrador:
        flash('Administrador no encontrado', 'error')
        return redirect(url_for('administrador.index'))
    
    # Solo el super admin puede editar otros admins, o cada admin puede editarse a sí mismo
    if not session.get('super_admin', False) and session.get('user_id') != id:
        flash('Solo puedes editar tu propio perfil', 'error')
        return redirect(url_for('administrador.index'))
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
        
        # Solo el super admin puede cambiar el estado de super admin
        if session.get('super_admin', False) and 'super_admin' in request.form:
            super_admin = request.form.get('super_admin') == 'on'
            administrador.update(nombre=nombre, email=email, telefono=telefono, super_admin=super_admin)
        else:
            administrador.update(nombre=nombre, email=email, telefono=telefono)
        
        flash('Administrador actualizado exitosamente', 'success')
        return redirect(url_for('administrador.index'))

    return administrador_view.edit(administrador)

@administrador_bp.route("/delete/<int:id>")
@super_admin_required
def delete(id):
    administrador = Administrador.get_by_id(id)
    if not administrador:
        flash('Administrador no encontrado', 'error')
        return redirect(url_for('administrador.index'))
    
    # No permitir eliminar al super admin
    if administrador.super_admin:
        flash('No se puede eliminar al Super Administrador', 'error')
        return redirect(url_for('administrador.index'))
    
    administrador.delete()
    flash('Administrador eliminado exitosamente', 'success')
    return redirect(url_for('administrador.index'))
