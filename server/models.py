from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates, relationship
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_bcrypt import Bcrypt


metadata = MetaData()
db = SQLAlchemy(metadata=metadata)
bcrypt = Bcrypt()

class User(db.Model):
    
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String)
    email = db.Column(db.String)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    role = db.relationship('Role', back_populates='users')
    guests = db.relationship('Guest', back_populates='user')

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role_id': self.role_id
        }

    @hybrid_property
    def password_hash(self):
        return self._password_hash
    
    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))
        

    @validates('email')
    def validate_email(self, key, email):
        if '@' not in email:
            raise ValueError("Invalid email")
        return email
    
    
    def __repr__(self):
        return f"<User {self.username}>"
    
class Role(db.Model):
    
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

    users = db.relationship('User', back_populates='role')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

    @validates('name')
    def validate_name(self, key, name):
        if name.lower() not in ['user', 'admin']:
            raise ValueError("Role name must be either 'user' or 'admin'")
        return name.lower()

    def __repr__(self):
        return f"<Role {self.name} ID: {self.id}>"
    
class Event(db.Model):
    
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    guests = db.relationship('Guest', back_populates='event')


    
class Guest(db.Model):
    
    __tablename__ = 'guests'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    rsvp_status = db.Column(db.Boolean)

    event = db.relationship('Event', back_populates='guests')
    user = db.relationship('User', back_populates='guests')



    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'user_id': self.user_id,
            'name': self.name,
            'email': self.name
        }
    
    @validates('email')
    def validate_email(self, key, email):
        if '@' not in email:
            raise ValueError("Invalid email")
        return email
    
    def __repr__(self):
        return f"<Guest {self.name}, ID: {self.id}"
    

