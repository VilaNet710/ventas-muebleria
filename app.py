from flask import Flask, render_template, request, session, flash, redirect, url_for
from controllers import usuario_controller, administrador_controller, producto_controller, venta_controller, compra_controller, proveedor_controller
from controllers.reporte_controller import reporte_bp
from models.usuario_model import Usuario
from models.administrador_model import Administrador
from database import db
from decorators import login_required

# Crear instancia de Flask
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ventasmuebleria.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializar base de datos con la aplicación
db.init_app(app)

# REGISTRO DE BLUEPRINTS (MÓDULOS)

# Los blueprints organizan las rutas por funcionalidad

app.register_blueprint(usuario_controller.usuario_bp)           # Gestión de usuarios
app.register_blueprint(administrador_controller.administrador_bp) # Gestión de administradores
app.register_blueprint(producto_controller.producto_bp)         # Gestión de productos
app.register_blueprint(venta_controller.venta_bp)              # Gestión de ventas
app.register_blueprint(compra_controller.compra_bp)            # Gestión de compras
app.register_blueprint(proveedor_controller.proveedor_bp)      # Gestión de proveedores
app.register_blueprint(reporte_bp)                             # Generación de reportes PDF

# RUTAS PRINCIPALES

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        tipo_usuario = request.form['tipo_usuario']
        
        if tipo_usuario == 'usuario':
            # Buscar en tabla usuarios
            usuarios = Usuario.get_all()
            for usuario in usuarios:
                if usuario.username == username and usuario.password == password:
                    # Crear sesión de usuario
                    session['user'] = username
                    session['user_id'] = usuario.id
                    session['tipo'] = 'usuario'
                    session['super_admin'] = False
                    flash('Bienvenido al sistema', 'success')
                    return redirect(url_for('dashboard'))
        
        elif tipo_usuario == 'administrador':
            # Buscar en tabla administradores
            administradores = Administrador.get_all()
            for admin in administradores:
                if admin.email == username and admin.password == password:
                    # Crear sesión de administrador
                    session['user'] = username
                    session['user_id'] = admin.id
                    session['tipo'] = 'administrador'
                    session['super_admin'] = admin.super_admin
                    flash('Bienvenido al sistema', 'success')
                    return redirect(url_for('dashboard'))
        
        flash('Credenciales incorrectas', 'error')
    
    return render_template('login.html')

@app.route("/dashboard")
@login_required
def dashboard():
    # Obtener datos adicionales para el dashboard
    compras_pendientes_count = 0
    if session.get('tipo') == 'administrador':
        from models.compra_model import Compra
        compras_pendientes_count = len(Compra.get_pendientes())
    
    return render_template('dashboard.html', compras_pendientes_count=compras_pendientes_count)

@app.route("/logout")
def logout():
    """
    Cerrar sesión del usuario
    Limpia todas las variables de sesión y redirige al inicio
    """
    session.clear()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('home'))

@app.route("/registro_usuario", methods=['GET', 'POST'])
def registro_usuario():

    if request.method == 'POST':
        nombre = request.form['nombre']
        username = request.form['username']
        password = request.form['password']
        rol = request.form['rol']
        
        # Verificar si el usuario ya existe
        usuarios = Usuario.get_all()
        for usuario in usuarios:
            if usuario.username == username:
                flash('El nombre de usuario ya existe', 'error')
                return render_template('registro_usuario.html')
        
        # Crear nuevo usuario
        nuevo_usuario = Usuario(nombre, username, password, rol)
        nuevo_usuario.save()
        flash('Usuario registrado exitosamente', 'success')
        return redirect(url_for('login'))
    
    return render_template('registro_usuario.html')

@app.route("/registro_administrador", methods=['GET', 'POST'])
def registro_administrador():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        telefono = request.form['telefono']
        
        # Verificar si el administrador ya existe
        administradores = Administrador.get_all()
        for admin in administradores:
            if admin.email == email:
                flash('El email ya está registrado', 'error')
                return render_template('registro_administrador.html')
        
        # Si es el primer administrador, hacerlo super admin
        is_first_admin = Administrador.count() == 0
        
        # Crear nuevo administrador
        nuevo_admin = Administrador(nombre, email, password, telefono, super_admin=is_first_admin)
        nuevo_admin.save()
        
        if is_first_admin:
            flash('Primer administrador registrado como Super Administrador', 'success')
        else:
            flash('Administrador registrado exitosamente', 'success')
        
        return redirect(url_for('login'))
    
    return render_template('registro_administrador.html')

@app.route("/crear_super_admin")
def crear_super_admin():
    # Solo para desarrollo - crear el primer super admin si no existe
    if Administrador.count() == 0:
        super_admin = Administrador(
            nombre="Super Administrador",
            email="admin@mueblesmetvil.com",
            password="admin123",
            telefono="123456789",
            super_admin=True
        )
        super_admin.save()
        flash('Super Administrador creado: admin@mueblesmetvil.com / admin123', 'success')
    else:
        flash('Ya existe un administrador en el sistema', 'info')
    
    return redirect(url_for('home'))

# Clave secreta para sesiones (CAMBIAR EN PRODUCCIÓN)
app.secret_key = 'tu_clave_secreta_'

if __name__ == "__main__":
    # Crear todas las tablas de base de datos al iniciar
    with app.app_context():
        db.create_all()
    
    # Ejecutar aplicación en modo debug
    app.run(debug=True)
