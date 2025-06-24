from flask import request, redirect, url_for, Blueprint, session, flash
from models.producto_model import Producto
from views import producto_view
from decorators import login_required, admin_required
import os
from werkzeug.utils import secure_filename

# Crear blueprint para las rutas de productos
producto_bp = Blueprint('producto', __name__, url_prefix="/productos")

# CONFIGURACIÓN DE SUBIDA DE ARCHIVOS

UPLOAD_FOLDER = 'static/images/productos'                    # Directorio de imágenes
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}          # Formatos permitidos

def allowed_file(filename):
    """
    Validar si el archivo tiene una extensión permitida
    
    Args:
        filename (str): Nombre del archivo a validar
        
    Returns:
        bool: True si la extensión está permitida, False en caso contrario
        
    Lógica:
    1. Verificar que el nombre tenga un punto (.)
    2. Extraer la extensión después del último punto
    3. Convertir a minúsculas para comparación
    4. Verificar que esté en la lista de extensiones permitidas
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============================================================================
# RUTAS DE VISUALIZACIÓN
# ============================================================================

@producto_bp.route("/")
@login_required
def index():
    """
    Mostrar catálogo de productos
    
    Acceso:
    - USUARIOS: Pueden ver catálogo para realizar compras
    - ADMINISTRADORES: Pueden ver catálogo y gestionar productos
    
    Returns:
        Template con lista de productos y opciones según el rol
    """
    productos = Producto.get_all()
    return producto_view.list(productos)

# ============================================================================
# CREACIÓN DE PRODUCTOS (SOLO ADMINISTRADORES)
# ============================================================================

@producto_bp.route("/create", methods=['GET', 'POST'])
@admin_required
def create():
    """
    Crear nuevo producto en el catálogo
    
    GET: Muestra formulario de creación
    POST: Procesa datos y crea producto con imagen
    
    Proceso de creación:
    1. Validar datos del formulario
    2. Procesar imagen subida (si existe)
    3. Generar nombre único para la imagen
    4. Guardar imagen en directorio
    5. Crear producto en base de datos
    6. Redirigir a catálogo con confirmación
    
    Returns:
        GET: Formulario de creación
        POST: Redirect a catálogo o formulario con errores
    """
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = float(request.form['precio'])
        stock = int(request.form['stock'])
        categoria = request.form['categoria']
        
        # ====================================================================
        # PROCESAMIENTO DE IMAGEN
        # ====================================================================
        
        # Por defecto usar imagen placeholder
        imagen_filename = 'placeholder.jpg'
        
        if 'imagen' in request.files:
            file = request.files['imagen']
            
            # Verificar que se seleccionó archivo y es válido
            if file and file.filename != '' and allowed_file(file.filename):
                # Asegurar nombre de archivo seguro
                filename = secure_filename(file.filename)
                
                # Generar nombre único para evitar conflictos
                import uuid
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                
                # Asegurar que el directorio existe
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
                # Guardar archivo en el servidor
                file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(file_path)
                imagen_filename = unique_filename

        # Crear nuevo producto con todos los datos
        producto = Producto(nombre, descripcion, precio, stock, categoria, imagen_filename)
        producto.save()
        
        flash('Producto creado exitosamente', 'success')
        return redirect(url_for('producto.index'))

    return producto_view.create()

# ============================================================================
# EDICIÓN DE PRODUCTOS (SOLO ADMINISTRADORES)
# ============================================================================

@producto_bp.route("/edit/<int:id>", methods=['GET', 'POST'])
@admin_required
def edit(id):
    """
    Editar producto existente
    
    Args:
        id (int): ID del producto a editar
        
    GET: Muestra formulario con datos actuales
    POST: Actualiza producto y maneja cambio de imagen
    
    Proceso de edición:
    1. Buscar producto por ID
    2. Si POST: procesar cambios
    3. Manejar nueva imagen (opcional)
    4. Eliminar imagen anterior si se cambió
    5. Actualizar datos en base de datos
    
    Returns:
        GET: Formulario de edición
        POST: Redirect a catálogo o formulario con errores
    """
    producto = Producto.get_by_id(id)
    if not producto:
        flash('Producto no encontrado', 'error')
        return redirect(url_for('producto.index'))
    
    if request.method == 'POST':
        # Obtener datos actualizados
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = float(request.form['precio'])
        stock = int(request.form['stock'])
        categoria = request.form['categoria']
        
        # ====================================================================
        # MANEJO DE IMAGEN (OPCIONAL EN EDICIÓN)
        # ====================================================================
        
        # Mantener imagen actual por defecto
        imagen_filename = producto.imagen
        
        if 'imagen' in request.files:
            file = request.files['imagen']
            
            # Solo procesar si se seleccionó nueva imagen válida
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                
                # Generar nombre único
                import uuid
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                
                # Asegurar directorio
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
                # Guardar nueva imagen
                file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(file_path)
                
                # Eliminar imagen anterior (si no es placeholder)
                if producto.imagen != 'placeholder.jpg':
                    old_image_path = os.path.join(UPLOAD_FOLDER, producto.imagen)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                
                imagen_filename = unique_filename
        
        # Actualizar producto con nuevos datos
        producto.update(nombre=nombre, descripcion=descripcion, precio=precio, 
                       stock=stock, categoria=categoria, imagen=imagen_filename)
        
        flash('Producto actualizado exitosamente', 'success')
        return redirect(url_for('producto.index'))

    return producto_view.edit(producto)

# ============================================================================
# ELIMINACIÓN DE PRODUCTOS (SOLO ADMINISTRADORES)
# ============================================================================

@producto_bp.route("/delete/<int:id>")
@admin_required
def delete(id):
    """
    Eliminar producto del catálogo
    
    Args:
        id (int): ID del producto a eliminar
        
    Proceso de eliminación:
    1. Buscar producto por ID
    2. Eliminar imagen asociada del servidor
    3. Eliminar registro de base de datos
    4. Confirmar eliminación al usuario
    
    Nota: Se mantiene placeholder.jpg para no romper el sistema
    
    Returns:
        Redirect a catálogo con confirmación o error
    """
    producto = Producto.get_by_id(id)
    if not producto:
        flash('Producto no encontrado', 'error')
        return redirect(url_for('producto.index'))
    
    # ========================================================================
    # LIMPIEZA DE IMAGEN
    # ========================================================================
    
    # Eliminar imagen del servidor (excepto placeholder)
    if producto.imagen != 'placeholder.jpg':
        image_path = os.path.join(UPLOAD_FOLDER, producto.imagen)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    # Eliminar producto de la base de datos
    producto.delete()
    flash('Producto eliminado exitosamente', 'success')
    return redirect(url_for('producto.index'))
