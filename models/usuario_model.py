from database import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(20), nullable=False)
    
    def __init__(self, nombre, username, password, rol):
        self.nombre = nombre
        self.username = username
        self.password = password
        self.rol = rol
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self, nombre=None, username=None, password=None, rol=None):
        if nombre:
            self.nombre = nombre
        if username:
            self.username = username
        if password:
            self.password = password
        if rol:
            self.rol = rol
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    @staticmethod
    def get_all():
        return Usuario.query.all()
    
    @staticmethod
    def get_by_id(id):
        return Usuario.query.get(id)
