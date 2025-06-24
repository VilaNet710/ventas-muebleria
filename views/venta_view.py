from flask import render_template
from models.venta_model import Venta

def list(ventas):
    total_ventas = Venta.get_total_ventas()
    ventas_directas_count = len([v for v in ventas if v.tipo_venta == 'directa'])
    ventas_compras_count = len([v for v in ventas if v.tipo_venta == 'por_compra'])
    
    return render_template('ventas/index.html', 
                         ventas=ventas, 
                         total_ventas=total_ventas,
                         ventas_directas_count=ventas_directas_count,
                         ventas_compras_count=ventas_compras_count)

def list_directas(ventas):
    return render_template('ventas/directas.html', ventas=ventas)

def list_por_compras(ventas):
    return render_template('ventas/por_compras.html', ventas=ventas)

def create(productos):
    return render_template('ventas/create.html', productos=productos)

def edit(venta, productos):
    return render_template('ventas/edit.html', venta=venta, productos=productos)

def detalle(venta):
    return render_template('ventas/detalle.html', venta=venta)
