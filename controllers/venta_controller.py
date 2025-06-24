from flask import request, redirect, url_for, Blueprint, session, flash
from models.venta_model import Venta
from models.producto_model import Producto
from views import venta_view
from decorators import login_required, admin_required

venta_bp = Blueprint('venta', __name__, url_prefix="/ventas")

@venta_bp.route("/")
@admin_required
def index():
    ventas = Venta.get_all()
    return venta_view.list(ventas)

@venta_bp.route("/directas")
@admin_required
def directas():
    """Ver solo ventas directas (no generadas por compras)"""
    ventas = Venta.get_ventas_directas()
    return venta_view.list_directas(ventas)

@venta_bp.route("/por_compras")
@admin_required
def por_compras():
    """Ver solo ventas generadas por compras aprobadas"""
    ventas = Venta.get_ventas_por_compra()
    return venta_view.list_por_compras(ventas)

@venta_bp.route("/create", methods=['GET', 'POST'])
@admin_required
def create():
    if request.method == 'POST':
        cliente = request.form['cliente']
        producto_id = int(request.form['producto_id'])
        cantidad = int(request.form['cantidad'])
        precio_unitario = float(request.form['precio_unitario'])

        venta = Venta(cliente, producto_id, cantidad, precio_unitario, tipo_venta='directa')
        venta.save()
        flash('Venta directa registrada exitosamente', 'success')
        return redirect(url_for('venta.index'))

    productos = Producto.get_all()
    return venta_view.create(productos)

@venta_bp.route("/edit/<int:id>", methods=['GET', 'POST'])
@admin_required
def edit(id):
    venta = Venta.get_by_id(id)
    if not venta:
        flash('Venta no encontrada', 'error')
        return redirect(url_for('venta.index'))
    
    # Solo se pueden editar ventas directas
    if venta.tipo_venta == 'por_compra':
        flash('No se pueden editar ventas generadas automáticamente por compras', 'warning')
        return redirect(url_for('venta.index'))
    
    if request.method == 'POST':
        cliente = request.form['cliente']
        producto_id = int(request.form['producto_id'])
        cantidad = int(request.form['cantidad'])
        precio_unitario = float(request.form['precio_unitario'])
        
        venta.update(cliente=cliente, producto_id=producto_id, cantidad=cantidad, precio_unitario=precio_unitario)
        flash('Venta actualizada exitosamente', 'success')
        return redirect(url_for('venta.index'))

    productos = Producto.get_all()
    return venta_view.edit(venta, productos)

@venta_bp.route("/delete/<int:id>")
@admin_required
def delete(id):
    venta = Venta.get_by_id(id)
    if not venta:
        flash('Venta no encontrada', 'error')
        return redirect(url_for('venta.index'))
    
    # Solo se pueden eliminar ventas directas
    if venta.tipo_venta == 'por_compra':
        flash('No se pueden eliminar ventas generadas automáticamente por compras', 'warning')
        return redirect(url_for('venta.index'))
    
    venta.delete()
    flash('Venta eliminada exitosamente', 'success')
    return redirect(url_for('venta.index'))

@venta_bp.route("/detalle/<int:id>")
@admin_required
def detalle(id):
    """Ver detalle completo de una venta"""
    venta = Venta.get_by_id(id)
    if not venta:
        flash('Venta no encontrada', 'error')
        return redirect(url_for('venta.index'))
    
    return venta_view.detalle(venta)
