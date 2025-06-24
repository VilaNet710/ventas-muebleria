from flask import render_template

def list(proveedores):
    return render_template('proveedores/index.html', proveedores=proveedores)

def create():
    return render_template('proveedores/create.html')

def edit(proveedor):
    return render_template('proveedores/edit.html', proveedor=proveedor)
