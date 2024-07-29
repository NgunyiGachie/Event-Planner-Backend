from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from faker import Faker
from app import app, db  
from models import db, User, Role, Event, Guest
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  
fake = Faker()
bcrypt = Bcrypt()


def seed_roles():
    with app.app_context():
        roles_data = [
            {'name': 'admin'},
            {'name': 'user'}
        ]
        
        for role_data in roles_data:
            role = Role.query.filter_by(name=role_data['name']).first()
            if not role:
                role = Role(**role_data)
                db.session.add(role)
        
        db.session.commit()
        print("Roles seeded successfully.")

def seed_users(num_users):
    with app.app_context():
        role_admin = Role.query.filter_by(name='admin').first()
        role_user = Role.query.filter_by(name='user').first()
        
        if not role_user:
            print("Role 'user' does not exist. Please create it first.")
            return
        
        db.session.query(User).delete()
        users = []
        usernames = set()
    
        for _ in range(num_users):
            username = fake.first_name()
            while username in usernames:
                username = fake.first_name()
            usernames.add(username)
            
            email = fake.email()
            password = username + 'password'
            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            
            user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                role_id=role_user.id  
            )
            
            users.append(user)
        
        db.session.add_all(users)
        db.session.commit()
        print(f"{num_users} users seeded successfully")


if __name__ == '__main__':
    with app.app_context():
        seed_roles()
        seed_users(num_users=20)
        
