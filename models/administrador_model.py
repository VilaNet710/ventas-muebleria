from database import db

class Administrador(db.Model):
    __tablename__ = 'administradores'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    super_admin = db.Column(db.Boolean, default=False)
    
    def __init__(self, nombre, email, password, telefono=None, super_admin=False):
        self.nombre = nombre
        self.email = email
        self.password = password
        self.telefono = telefono
        self.super_admin = super_admin
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self, nombre=None, email=None, password=None, telefono=None, super_admin=None):
        if nombre:
            self.nombre = nombre
        if email:
            self.email = email
        if password:
            self.password = password
        if telefono:
            self.telefono = telefono
        if super_admin is not None:
            self.super_admin = super_admin
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    @staticmethod
    def get_all():
        return Administrador.query.all()
    
    @staticmethod
    def get_by_id(id):
        return Administrador.query.get(id)
    
    @staticmethod
    def get_super_admin():
        return Administrador.query.filter_by(super_admin=True).first()
    
    @staticmethod
    def count():
        return Administrador.query.count()
