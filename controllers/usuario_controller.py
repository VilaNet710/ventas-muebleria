from flask import request, redirect,url_for, Blueprint, session, flash
from models.usuario_model import Usuario
from views import usuario_view
from decorators import login_required, admin_required

usuario_bp = Blueprint('usuario',__name__,url_prefix="/usuarios")

@usuario_bp.route("/")
@login_required
def index():
    usuarios = Usuario.get_all()
    return usuario_view.list(usuarios)

@usuario_bp.route("/create", methods = ['GET','POST'])
@admin_required
def create():
    if request.method == 'POST':
        nombre = request.form['nombre']
        username = request.form['username']   
        password = request.form['password']   
        rol = request.form['rol']

        usuario = Usuario(nombre,username,password,rol) 
        usuario.save()
        flash('Usuario creado exitosamente', 'success')
        return redirect(url_for('usuario.index'))
              
    return usuario_view.create()

@usuario_bp.route("/edit/<int:id>", methods = ['GET','POST'])
@admin_required
def edit(id):
    usuario = Usuario.get_by_id(id)
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('usuario.index'))
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        username = request.form['username']   
        rol = request.form['rol']
        # No actualizar contraseña
        usuario.update(nombre=nombre,username=username,rol=rol)
        flash('Usuario actualizado exitosamente', 'success')
        return redirect(url_for('usuario.index'))

    return usuario_view.edit(usuario)

@usuario_bp.route("/delete/<int:id>")
@admin_required
def delete(id):
    usuario = Usuario.get_by_id(id)
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('usuario.index'))
    
    usuario.delete()
    flash('Usuario eliminado exitosamente', 'success')
    return redirect(url_for('usuario.index'))
