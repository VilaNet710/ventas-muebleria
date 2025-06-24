from flask import request, redirect, url_for, Blueprint, session, flash, send_file, render_template
from models.compra_model import Compra
from models.venta_model import Venta
from models.proveedor_model import Proveedor
from models.producto_model import Producto
from models.usuario_model import Usuario
from views import compra_view
from decorators import login_required, user_only_required, admin_required
from utils.pdf_generator import generar_factura_compra

# Crear blueprint para las rutas de compras
compra_bp = Blueprint('compra', __name__, url_prefix="/compras")

# RUTAS DE VISUALIZACIÓN

@compra_bp.route("/")
@login_required
def index():
    if session.get('tipo') == 'usuario':
        # Los usuarios solo ven sus propias compras
        compras = Compra.get_by_usuario(session.get('user_id'))
    else:
        # Los administradores ven todas las compras
        compras = Compra.get_all()
    return compra_view.list(compras)

@compra_bp.route("/pendientes")
@admin_required
def pendientes():
    compras_pendientes = Compra.get_pendientes()
    return compra_view.pendientes(compras_pendientes)

# CREACIÓN DE SOLICITUDES DE COMPRa

@compra_bp.route("/create", methods=['GET', 'POST'])
@user_only_required
def create():

    if request.method == 'POST':
        # Obtener datos del formulario
        proveedor_id = int(request.form['proveedor_id'])
        producto_id = int(request.form['producto_id'])
        cantidad = int(request.form['cantidad'])
        precio_unitario = float(request.form['precio_unitario'])

        # Crear nueva compra con estado 'pendiente'
        compra = Compra(session.get('user_id'), proveedor_id, producto_id, cantidad, precio_unitario)
        compra.save()
        
        flash('Solicitud de compra enviada exitosamente. Esperando aprobación del administrador.', 'success')
        return render_template('compras/success.html', compra_id=compra.id)

    # Obtener datos para el formulario
    proveedores = Proveedor.get_all()
    productos = Producto.get_all()
    return compra_view.create(proveedores, productos)

# PROCESO DE APROBACIÓN (ADMINISTRADORES)

@compra_bp.route("/aprobar/<int:id>", methods=['POST'])
@admin_required
def aprobar(id):

    compra = Compra.get_by_id(id)
    if not compra:
        flash('Compra no encontrada', 'error')
        return redirect(url_for('compra.pendientes'))
    
    if compra.estado != 'pendiente':
        flash('Esta compra ya fue procesada', 'warning')
        return redirect(url_for('compra.pendientes'))
    
    comentarios = request.form.get('comentarios', '')
    
    # Aprobar la compra
    compra.update(estado='aprobada', aprobado_por=session.get('user_id'), comentarios=comentarios)
    
    # CREACIÓN AUTOMÁTICA DE VENTA
    
    try:
        cliente_nombre = compra.usuario.nombre if compra.usuario else 'Cliente Desconocido'
        
        # Crear venta relacionada con la compra aprobada
        nueva_venta = Venta(
            cliente=cliente_nombre,
            producto_id=compra.producto_id,
            cantidad=compra.cantidad,
            precio_unitario=compra.precio_unitario,
            compra_id=compra.id,                    # Relación con la compra
            vendedor_id=session.get('user_id'),
            tipo_venta='por_compra'
        )
        nueva_venta.save()
        
        flash(f'Compra aprobada exitosamente. Se ha generado automáticamente la venta #{nueva_venta.id}', 'success')
    except Exception as e:
        flash('Compra aprobada, pero hubo un error al crear la venta automática', 'warning')
    
    return redirect(url_for('compra.pendientes'))

@compra_bp.route("/rechazar/<int:id>", methods=['POST'])
@admin_required
def rechazar(id):

    compra = Compra.get_by_id(id)
    if not compra:
        flash('Compra no encontrada', 'error')
        return redirect(url_for('compra.pendientes'))
    
    if compra.estado != 'pendiente':
        flash('Esta compra ya fue procesada', 'warning')
        return redirect(url_for('compra.pendientes'))
    
    comentarios = request.form.get('comentarios', 'Compra rechazada por el administrador')
    compra.update(estado='rechazada', aprobado_por=session.get('user_id'), comentarios=comentarios)
    flash('Compra rechazada', 'warning')
    return redirect(url_for('compra.pendientes'))

# GENERACIÓN DE FACTURAS PDF

@compra_bp.route("/factura/<int:id>")
@login_required
def generar_factura(id):

    compra = Compra.get_by_id(id)
    if not compra:
        flash('Compra no encontrada', 'error')
        return redirect(url_for('compra.index'))
    
    # Verificar permisos de acceso
    if session.get('tipo') == 'usuario' and compra.usuario_id != session.get('user_id'):
        flash('No tienes permisos para ver esta factura', 'error')
        return redirect(url_for('compra.index'))
    
    # Solo compras aprobadas pueden generar factura
    if compra.estado != 'aprobada':
        flash('Solo se pueden generar facturas de compras aprobadas', 'warning')
        return redirect(url_for('compra.index'))
    
    # Generar PDF usando el generador de reportes
    pdf_buffer = generar_factura_compra(compra)
    filename = f"factura_compra_{compra.id}.pdf"
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )

# EDICIÓN Y ELIMINACIÓN (SOLO USUARIOS, SOLO PENDIENTES)

@compra_bp.route("/edit/<int:id>", methods=['GET', 'POST'])
@user_only_required
def edit(id):

    compra = Compra.get_by_id(id)
    if not compra:
        flash('Compra no encontrada', 'error')
        return redirect(url_for('compra.index'))
    
    # Validar propiedad de la compra
    if compra.usuario_id != session.get('user_id'):
        flash('No puedes editar esta compra', 'error')
        return redirect(url_for('compra.index'))
    
    # Solo compras pendientes pueden editarse
    if compra.estado != 'pendiente':
        flash('Solo se pueden editar compras pendientes', 'warning')
        return redirect(url_for('compra.index'))
    
    if request.method == 'POST':
        # Actualizar datos de la compra
        proveedor_id = int(request.form['proveedor_id'])
        producto_id = int(request.form['producto_id'])
        cantidad = int(request.form['cantidad'])
        precio_unitario = float(request.form['precio_unitario'])
        
        compra.update(proveedor_id=proveedor_id, producto_id=producto_id, cantidad=cantidad, precio_unitario=precio_unitario)
        flash('Compra actualizada exitosamente', 'success')
        return redirect(url_for('compra.index'))

    # Obtener datos para el formulario
    proveedores = Proveedor.get_all()
    productos = Producto.get_all()
    return compra_view.edit(compra, proveedores, productos)

@compra_bp.route("/delete/<int:id>")
@user_only_required
def delete(id):

    compra = Compra.get_by_id(id)
    if not compra:
        flash('Compra no encontrada', 'error')
        return redirect(url_for('compra.index'))
    
    # Validar propiedad
    if compra.usuario_id != session.get('user_id'):
        flash('No puedes eliminar esta compra', 'error')
        return redirect(url_for('compra.index'))
    
    # Solo pendientes pueden eliminarse
    if compra.estado != 'pendiente':
        flash('Solo se pueden eliminar compras pendientes', 'warning')
        return redirect(url_for('compra.index'))
    
    compra.delete()
    flash('Compra eliminada exitosamente', 'success')
    return redirect(url_for('compra.index'))
