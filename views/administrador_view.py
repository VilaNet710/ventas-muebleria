from flask import render_template

def list(administradores):
    return render_template('administrador/index.html', administradores=administradores)

def create():
    return render_template('administrador/create.html')

def edit(administrador):
    return render_template('administrador/edit.html', administrador=administrador)
