from flask import request, redirect, url_for, Blueprint, session, flash
from models.proveedor_model import Proveedor
from views import proveedor_view
from decorators import login_required, admin_required

proveedor_bp = Blueprint('proveedor', __name__, url_prefix="/proveedores")

@proveedor_bp.route("/")
@admin_required
def index():
    proveedores = Proveedor.get_all()
    return proveedor_view.list(proveedores)

@proveedor_bp.route("/create", methods=['GET', 'POST'])
@admin_required
def create():
    if request.method == 'POST':
        nombre = request.form['nombre']
        contacto = request.form['contacto']
        telefono = request.form['telefono']
        email = request.form['email']
        direccion = request.form['direccion']

        proveedor = Proveedor(nombre, contacto, telefono, email, direccion)
        proveedor.save()
        flash('Proveedor creado exitosamente', 'success')
        return redirect(url_for('proveedor.index'))

    return proveedor_view.create()

@proveedor_bp.route("/edit/<int:id>", methods=['GET', 'POST'])
@admin_required
def edit(id):
    proveedor = Proveedor.get_by_id(id)
    if not proveedor:
        flash('Proveedor no encontrado', 'error')
        return redirect(url_for('proveedor.index'))
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        contacto = request.form['contacto']
        telefono = request.form['telefono']
        email = request.form['email']
        direccion = request.form['direccion']
        
        proveedor.update(nombre=nombre, contacto=contacto, telefono=telefono, email=email, direccion=direccion)
        flash('Proveedor actualizado exitosamente', 'success')
        return redirect(url_for('proveedor.index'))

    return proveedor_view.edit(proveedor)

@proveedor_bp.route("/delete/<int:id>")
@admin_required
def delete(id):
    proveedor = Proveedor.get_by_id(id)
    if not proveedor:
        flash('Proveedor no encontrado', 'error')
        return redirect(url_for('proveedor.index'))
    
    proveedor.delete()
    flash('Proveedor eliminado exitosamente', 'success')
    return redirect(url_for('proveedor.index'))
