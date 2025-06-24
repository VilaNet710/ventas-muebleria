from flask import Blueprint, session, flash, redirect, url_for, send_file, render_template
from models.venta_model import Venta
from models.producto_model import Producto
from models.compra_model import Compra
from decorators import admin_required
from utils.pdf_generator import generar_reporte_ventas, generar_reporte_productos

reporte_bp = Blueprint('reporte', __name__, url_prefix="/reportes")

@reporte_bp.route("/")
@admin_required
def index():
    """Página principal de reportes"""
    return render_template('reportes/index.html')

@reporte_bp.route("/ventas")
@admin_required
def reporte_ventas():
    """Generar reporte de ventas en PDF"""
    ventas = Venta.get_all()
    pdf_buffer = generar_reporte_ventas(ventas)
    filename = f"reporte_ventas.pdf"
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )

@reporte_bp.route("/productos")
@admin_required
def reporte_productos():
    """Generar reporte de productos en PDF"""
    productos = Producto.get_all()
    pdf_buffer = generar_reporte_productos(productos)
    filename = f"reporte_productos.pdf"
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )

@reporte_bp.route("/compras")
@admin_required
def reporte_compras():
    """Vista de estadísticas de compras"""
    compras_pendientes = len(Compra.get_pendientes())
    compras_aprobadas = len(Compra.get_aprobadas())
    todas_compras = Compra.get_all()
    
    return render_template('reportes/compras.html', 
                         compras_pendientes=compras_pendientes,
                         compras_aprobadas=compras_aprobadas,
                         todas_compras=todas_compras)
