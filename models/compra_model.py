from database import db
from datetime import datetime

class Compra(db.Model):
    """
    Modelo de Compra - Representa las solicitudes de compra de usuarios
    
    Flujo del modelo:
    1. Usuario crea compra → estado 'pendiente'
    2. Administrador revisa → cambia a 'aprobada' o 'rechazada'
    3. Si aprobada → se crea Venta automáticamente
    4. Usuario puede generar factura PDF
    """
    
    __tablename__ = 'compras'
    
    # ========================================================================
    # CAMPOS PRINCIPALES
    # ========================================================================
    
    id = db.Column(db.Integer, primary_key=True)                           # ID único de la compra
    fecha = db.Column(db.DateTime, default=datetime.utcnow)                # Fecha de creación automática
    
    # ========================================================================
    # RELACIONES CON OTRAS TABLAS
    # ========================================================================
    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)      # Quien solicita
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=False) # Proveedor del producto
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)    # Producto solicitado
    
    # ========================================================================
    # INFORMACIÓN DE LA COMPRA
    # ========================================================================
    
    cantidad = db.Column(db.Integer, nullable=False)                       # Cantidad solicitada
    precio_unitario = db.Column(db.Float, nullable=False)                  # Precio por unidad
    total = db.Column(db.Float, nullable=False)                            # Total calculado (cantidad * precio)
    
    # ========================================================================
    # CONTROL DE ESTADO Y APROBACIÓN
    # ========================================================================
    
    estado = db.Column(db.String(20), default='pendiente')                 # pendiente, aprobada, rechazada
    aprobado_por = db.Column(db.Integer, db.ForeignKey('administradores.id'), nullable=True)  # Quien aprobó/rechazó
    fecha_aprobacion = db.Column(db.DateTime, nullable=True)               # Cuándo se aprobó/rechazó
    comentarios = db.Column(db.Text, nullable=True)                        # Comentarios del administrador
    
    # ========================================================================
    # DEFINICIÓN DE RELACIONES
    # ========================================================================
    
    # Estas relaciones permiten acceder fácilmente a los objetos relacionados
    usuario = db.relationship('Usuario', backref='compras')                # compra.usuario.nombre
    proveedor = db.relationship('Proveedor', backref='compras')            # compra.proveedor.nombre
    producto = db.relationship('Producto', backref='compras')              # compra.producto.nombre
    
    def __init__(self, usuario_id, proveedor_id, producto_id, cantidad, precio_unitario):
        """
        Constructor de la compra
        
        Args:
            usuario_id (int): ID del usuario que solicita
            proveedor_id (int): ID del proveedor
            producto_id (int): ID del producto
            cantidad (int): Cantidad solicitada
            precio_unitario (float): Precio por unidad
            
        Nota: El total se calcula automáticamente y el estado inicial es 'pendiente'
        """
        self.usuario_id = usuario_id
        self.proveedor_id = proveedor_id
        self.producto_id = producto_id
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.total = cantidad * precio_unitario  # Cálculo automático del total
        self.estado = 'pendiente'                # Estado inicial siempre pendiente
    
    # ========================================================================
    # MÉTODOS DE PERSISTENCIA
    # ========================================================================
    
    def save(self):
        """
        Guardar compra en la base de datos
        Utilizado cuando se crea una nueva solicitud de compra
        """
        db.session.add(self)
        db.session.commit()
    
    def update(self, usuario_id=None, proveedor_id=None, producto_id=None, cantidad=None, 
               precio_unitario=None, estado=None, aprobado_por=None, comentarios=None):
        """
        Actualizar campos de la compra
        
        Args:
            usuario_id (int, optional): Nuevo usuario
            proveedor_id (int, optional): Nuevo proveedor
            producto_id (int, optional): Nuevo producto
            cantidad (int, optional): Nueva cantidad
            precio_unitario (float, optional): Nuevo precio
            estado (str, optional): Nuevo estado (pendiente/aprobada/rechazada)
            aprobado_por (int, optional): ID del administrador que aprueba
            comentarios (str, optional): Comentarios del administrador
            
        Lógica especial:
        - Si cambia cantidad o precio → recalcula total automáticamente
        - Si cambia estado a aprobada/rechazada → registra fecha de aprobación
        """
        if usuario_id:
            self.usuario_id = usuario_id
        if proveedor_id:
            self.proveedor_id = proveedor_id
        if producto_id:
            self.producto_id = producto_id
        if cantidad:
            self.cantidad = cantidad
        if precio_unitario:
            self.precio_unitario = precio_unitario
            
        # Recalcular total si cambió cantidad o precio
        if cantidad and precio_unitario:
            self.total = cantidad * precio_unitario
            
        # Manejar cambio de estado
        if estado:
            self.estado = estado
            # Si se aprueba o rechaza, registrar fecha automáticamente
            if estado in ['aprobada', 'rechazada']:
                self.fecha_aprobacion = datetime.utcnow()
                
        if aprobado_por:
            self.aprobado_por = aprobado_por
        if comentarios:
            self.comentarios = comentarios
            
        db.session.commit()
    
    def delete(self):
        """
        Eliminar compra de la base de datos
        Solo se permite eliminar compras pendientes
        """
        db.session.delete(self)
        db.session.commit()
    
    # ========================================================================
    # MÉTODOS DE CONSULTA ESTÁTICOS
    # ========================================================================
    
    @staticmethod
    def get_all():
        """
        Obtener todas las compras del sistema
        Utilizado por administradores para ver todo
        
        Returns:
            list: Lista de todas las compras
        """
        return Compra.query.all()
    
    @staticmethod
    def get_by_id(id):
        """
        Buscar compra por ID
        
        Args:
            id (int): ID de la compra
            
        Returns:
            Compra: Objeto compra o None si no existe
        """
        return Compra.query.get(id)
    
    @staticmethod
    def get_by_usuario(usuario_id):
        """
        Obtener compras de un usuario específico
        Utilizado para que usuarios vean solo sus compras
        
        Args:
            usuario_id (int): ID del usuario
            
        Returns:
            list: Lista de compras del usuario
        """
        return Compra.query.filter_by(usuario_id=usuario_id).all()
    
    @staticmethod
    def get_pendientes():
        """
        Obtener solo compras pendientes de aprobación
        Utilizado por administradores para ver qué necesita revisión
        
        Returns:
            list: Lista de compras con estado 'pendiente'
        """
        return Compra.query.filter_by(estado='pendiente').all()
    
    @staticmethod
    def get_aprobadas():
        """
        Obtener solo compras aprobadas
        Utilizado para estadísticas y reportes
        
        Returns:
            list: Lista de compras con estado 'aprobada'
        """
        return Compra.query.filter_by(estado='aprobada').all()
