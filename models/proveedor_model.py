from database import db

class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    contacto = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    direccion = db.Column(db.Text)
    
    def __init__(self, nombre, contacto=None, telefono=None, email=None, direccion=None):
        self.nombre = nombre
        self.contacto = contacto
        self.telefono = telefono
        self.email = email
        self.direccion = direccion
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self, nombre=None, contacto=None, telefono=None, email=None, direccion=None):
        if nombre:
            self.nombre = nombre
        if contacto:
            self.contacto = contacto
        if telefono:
            self.telefono = telefono
        if email:
            self.email = email
        if direccion:
            self.direccion = direccion
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    @staticmethod
    def get_all():
        return Proveedor.query.all()
    
    @staticmethod
    def get_by_id(id):
        return Proveedor.query.get(id)
