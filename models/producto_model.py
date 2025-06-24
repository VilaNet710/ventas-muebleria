"""
================================================================================
MODELO DE PRODUCTOS - SISTEMA DE VENTAS MUEBLERÍA
================================================================================
Este modelo maneja toda la información relacionada con los productos de la 
mueblería, incluyendo la gestión de imágenes.

Funcionalidades:
- CRUD completo de productos
- Gestión de imágenes con URLs dinámicas
- Categorización de productos
- Control de inventario (stock)
- Métodos de consulta optimizados
================================================================================
"""

from database import db

class Producto(db.Model):
    """
    Modelo de Producto - Representa los muebles en venta
    
    Campos:
    - id: Identificador único del producto
    - nombre: Nombre comercial del producto
    - descripcion: Descripción detallada del producto
    - precio: Precio de venta en formato decimal
    - stock: Cantidad disponible en inventario
    - categoria: Categoría del producto (sillas, mesas, etc.)
    - imagen: Nombre del archivo de imagen asociado
    """
    
    __tablename__ = 'productos'
    
    # ========================================================================
    # DEFINICIÓN DE CAMPOS
    # ========================================================================
    
    id = db.Column(db.Integer, primary_key=True)                    # ID único
    nombre = db.Column(db.String(100), nullable=False)             # Nombre del producto
    descripcion = db.Column(db.Text)                               # Descripción detallada
    precio = db.Column(db.Float, nullable=False)                   # Precio de venta
    stock = db.Column(db.Integer, default=0)                       # Cantidad en inventario
    categoria = db.Column(db.String(50))                           # Categoría del producto
    imagen = db.Column(db.String(200), default='placeholder.jpg')  # Archivo de imagen
    
    def __init__(self, nombre, descripcion, precio, stock=0, categoria=None, imagen='placeholder.jpg'):
        """
        Constructor del producto
        
        Args:
            nombre (str): Nombre del producto
            descripcion (str): Descripción del producto
            precio (float): Precio de venta
            stock (int): Cantidad inicial en inventario
            categoria (str): Categoría del producto
            imagen (str): Nombre del archivo de imagen
        """
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = precio
        self.stock = stock
        self.categoria = categoria
        self.imagen = imagen
    
    # ========================================================================
    # MÉTODOS DE PERSISTENCIA
    # ========================================================================
    
    def save(self):
        """
        Guardar producto en la base de datos
        Agrega el objeto a la sesión y confirma los cambios
        """
        db.session.add(self)
        db.session.commit()
    
    def update(self, nombre=None, descripcion=None, precio=None, stock=None, categoria=None, imagen=None):
        """
        Actualizar campos del producto
        Solo actualiza los campos que se proporcionen (no None)
        
        Args:
            nombre (str, optional): Nuevo nombre
            descripcion (str, optional): Nueva descripción
            precio (float, optional): Nuevo precio
            stock (int, optional): Nuevo stock
            categoria (str, optional): Nueva categoría
            imagen (str, optional): Nueva imagen
        """
        if nombre:
            self.nombre = nombre
        if descripcion:
            self.descripcion = descripcion
        if precio:
            self.precio = precio
        if stock is not None:  # Permitir stock = 0
            self.stock = stock
        if categoria:
            self.categoria = categoria
        if imagen:
            self.imagen = imagen
        db.session.commit()
    
    def delete(self):
        """
        Eliminar producto de la base de datos
        Remueve el objeto de la sesión y confirma los cambios
        """
        db.session.delete(self)
        db.session.commit()
    
    # ========================================================================
    # MÉTODOS DE CONSULTA ESTÁTICOS
    # ========================================================================
    
    @staticmethod
    def get_all():
        """
        Obtener todos los productos
        
        Returns:
            list: Lista de todos los productos en la base de datos
        """
        return Producto.query.all()
    
    @staticmethod
    def get_by_id(id):
        """
        Buscar producto por ID
        
        Args:
            id (int): ID del producto a buscar
            
        Returns:
            Producto: Objeto producto o None si no existe
        """
        return Producto.query.get(id)
    
    @staticmethod
    def get_by_categoria(categoria):
        """
        Obtener productos por categoría
        
        Args:
            categoria (str): Categoría a filtrar
            
        Returns:
            list: Lista de productos de la categoría especificada
        """
        return Producto.query.filter_by(categoria=categoria).all()
    
    # ========================================================================
    # MÉTODOS DE UTILIDAD
    # ========================================================================
    
    def get_imagen_url(self):
        """
        Obtener URL completa de la imagen del producto
        
        Returns:
            str: URL de la imagen o placeholder si no tiene imagen
            
        Lógica:
        - Si tiene imagen personalizada: /static/images/productos/{imagen}
        - Si no tiene imagen: /static/images/productos/placeholder.jpg
        """
        if self.imagen and self.imagen != 'placeholder.jpg':
            return f'/static/images/productos/{self.imagen}'
        else:
            return f'/static/images/productos/placeholder.jpg'
