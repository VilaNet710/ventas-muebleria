from flask import render_template

def list(compras):
    return render_template('compras/index.html', compras=compras)

def create(proveedores, productos):
    return render_template('compras/create.html', proveedores=proveedores, productos=productos)

def edit(compra, proveedores, productos):
    return render_template('compras/edit.html', compra=compra, proveedores=proveedores, productos=productos)

def pendientes(compras_pendientes):
    return render_template('compras/pendientes.html', compras_pendientes=compras_pendientes)
