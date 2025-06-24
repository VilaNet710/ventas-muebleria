"""
================================================================================
MODELO DE VENTAS - SISTEMA DE VENTAS MUEBLERÍA
================================================================================
Este modelo maneja las ventas del sistema, que pueden ser de dos tipos:
1. DIRECTAS: Registradas manualmente por administradores
2. POR COMPRAS: Generadas automáticamente al aprobar compras de usuarios

El modelo mantiene la relación entre compras aprobadas y sus ventas correspondientes,
permitiendo un seguimiento completo del flujo comercial.

Características importantes:
- Relación opcional con compras (solo ventas por compras la tienen)
- Registro del vendedor/aprobador
- Cálculo automático de totales
- Métodos de consulta especializados por tipo
================================================================================
"""

from database import db
from datetime import datetime

class Venta(db.Model):
    """
    Modelo de Venta - Representa las ventas realizadas en el sistema
    
    Tipos de venta:
    - 'directa': Registrada manualmente por administrador
    - 'por_compra': Generada automáticamente al aprobar compra de usuario
    
    Flujo de creación:
    1. Venta directa: Admin crea manualmente
    2. Venta por compra: Sistema crea al aprobar compra
    """
    
    __tablename__ = 'ventas'
    
    # ========================================================================
    # CAMPOS PRINCIPALES
    # ========================================================================
    
    id = db.Column(db.Integer, primary_key=True)                           # ID único de la venta
    fecha = db.Column(db.DateTime, default=datetime.utcnow)                # Fecha de creación automática
    cliente = db.Column(db.String(100), nullable=False)                    # Nombre del cliente
    
    # ========================================================================
    # INFORMACIÓN DEL PRODUCTO VENDIDO
    # ========================================================================
    
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)  # Producto vendido
    cantidad = db.Column(db.Integer, nullable=False)                       # Cantidad vendida
    precio_unitario = db.Column(db.Float, nullable=False)                  # Precio por unidad
    total = db.Column(db.Float, nullable=False)                            # Total de la venta
    
    # ========================================================================
    # RELACIONES Y CONTROL
    # ========================================================================
    
    compra_id = db.Column(db.Integer, db.ForeignKey('compras.id'), nullable=True)       # Compra relacionada (opcional)
    vendedor_id = db.Column(db.Integer, db.ForeignKey('administradores.id'), nullable=True)  # Quien vendió/aprobó
    tipo_venta = db.Column(db.String(20), default='directa')               # 'directa' o 'por_compra'
    
    # ========================================================================
    # DEFINICIÓN DE RELACIONES
    # ========================================================================
    
    producto = db.relationship('Producto', backref='ventas')               # venta.producto.nombre
    compra = db.relationship('Compra', backref='venta', uselist=False)     # venta.compra (relación uno a uno)
    
    def __init__(self, cliente, producto_id, cantidad, precio_unitario, compra_id=None, vendedor_id=None, tipo_venta='directa'):
        """
        Constructor de la venta
        
        Args:
            cliente (str): Nombre del cliente
            producto_id (int): ID del producto vendido
            cantidad (int): Cantidad vendida
            precio_unitario (float): Precio por unidad
            compra_id (int, optional): ID de compra relacionada (solo para ventas por compra)
            vendedor_id (int, optional): ID del administrador que vendió/aprobó
            tipo_venta (str): Tipo de venta ('directa' o 'por_compra')
            
        Nota: El total se calcula automáticamente
        """
        self.cliente = cliente
        self.producto_id = producto_id
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.total = cantidad * precio_unitario  # Cálculo automático del total
        self.compra_id = compra_id
        self.vendedor_id = vendedor_id
        self.tipo_venta = tipo_venta
    
    # ========================================================================
    # MÉTODOS DE PERSISTENCIA
    # ========================================================================
    
    def save(self):
        """
        Guardar venta en la base de datos
        Utilizado tanto para ventas directas como automáticas
        """
        db.session.add(self)
        db.session.commit()
    
    def update(self, cliente=None, producto_id=None, cantidad=None, precio_unitario=None):
        """
        Actualizar campos de la venta
        
        Args:
            cliente (str, optional): Nuevo nombre del cliente
            producto_id (int, optional): Nuevo producto
            cantidad (int, optional): Nueva cantidad
            precio_unitario (float, optional): Nuevo precio
            
        Restricción: Solo se pueden editar ventas directas
        Las ventas por compra son inmutables una vez creadas
        """
        if cliente:
            self.cliente = cliente
        if producto_id:
            self.producto_id = producto_id
        if cantidad:
            self.cantidad = cantidad
        if precio_unitario:
            self.precio_unitario = precio_unitario
            
        # Recalcular total si cambió cantidad o precio
        if cantidad and precio_unitario:
            self.total = cantidad * precio_unitario
            
        db.session.commit()
    
    def delete(self):
        """
        Eliminar venta de la base de datos
        Restricción: Solo se pueden eliminar ventas directas
        """
        db.session.delete(self)
        db.session.commit()
    
    # ========================================================================
    # MÉTODOS DE CONSULTA ESTÁTICOS
    # ========================================================================
    
    @staticmethod
    def get_all():
        """
        Obtener todas las ventas del sistema
        Incluye tanto directas como por compras
        
        Returns:
            list: Lista de todas las ventas
        """
        return Venta.query.all()
    
    @staticmethod
    def get_by_id(id):
        """
        Buscar venta por ID
        
        Args:
            id (int): ID de la venta
            
        Returns:
            Venta: Objeto venta o None si no existe
        """
        return Venta.query.get(id)
    
    @staticmethod
    def get_ventas_directas():
        """
        Obtener solo ventas directas (registradas manualmente)
        
        Returns:
            list: Lista de ventas con tipo_venta = 'directa'
        """
        return Venta.query.filter_by(tipo_venta='directa').all()
    
    @staticmethod
    def get_ventas_por_compra():
        """
        Obtener solo ventas generadas por compras aprobadas
        
        Returns:
            list: Lista de ventas con tipo_venta = 'por_compra'
        """
        return Venta.query.filter_by(tipo_venta='por_compra').all()
    
    @staticmethod
    def get_total_ventas():
        """
        Calcular el total de ingresos por ventas
        Utilizado para estadísticas y reportes
        
        Returns:
            float: Suma total de todas las ventas o 0 si no hay ventas
        """
        result = db.session.query(db.func.sum(Venta.total)).scalar()
        return result or 0
    
    @staticmethod
    def get_ventas_mes_actual():
        """
        Obtener ventas del mes actual
        Utilizado para estadísticas mensuales
        
        Returns:
            list: Lista de ventas del mes actual
        """
        from datetime import datetime, timedelta
        # Calcular inicio del mes actual
        inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return Venta.query.filter(Venta.fecha >= inicio_mes).all()
