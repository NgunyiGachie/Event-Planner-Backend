from flask import Flask, make_response, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, User, Role, Event, Guest 

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_RECORD_QUERIES"] = True

db.init_app(app)  
migrate = Migrate(app, db)
api = Api(app)

class Register(Resource):

    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        role_id = data.get('role_id')

        if not username or password:
            return jsonify({'error': 'Please input a username and a password'}), 422
        
        new_user = User(
            username=username,
            email=email,
            role_id=role_id
        )

        new_user.password_hash = password
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        return new_user.to_dict(), 201

class Login(Resource):

    def post(self):
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return {'message': 'Missing username or password'}, 400
            
            user = User.query.filter(User.username == username).first()

            if user and user.authenticate(password):
                session['user_id'] = user.id
                return jsonify({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role_id': user.role_id
                }), 200
            return {'message': '401: Not Authorized'}, 401
        except KeyError as e:
            return {'message': f'KeyError: {str(e)}'}, 400
    
class Logout(Resource):

    def delete(self):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        session.pop('user_id', None)
        return '', 401
    
class Guests(Resource):

    def get(self):
        guests = Guest.query.all()
        return jsonify([guest.to_dict() for guest in guests]), 200


    def post(self):
        data = request.get_json()
        event_id = data.get('event_id')
        user_id = data.get('user_id')
        name = data.get('name')
        email = data.get('email')
        rsvp_status = data.get('rsvp_status')

        new_guest = Guest(
            event_id=event_id,
            user_id=user_id,
            name=name,
            email=email,
            rsvp_status=rsvp_status
        )
        db.session.add(new_guest)
        db.session.commit()
        return new_guest.to_dict(), 201

    

    def delete(self):
        data = request.get_json()
        guest_id = data.get('id')
        guest = Guest.query.get_or_404(guest_id)

        db.session.delete(guest)
        db.session.commit()
        return '', 204

class GuestByID(Resource):

    def get(self, id):
        guest = Guest.query.get_or_404(id)
        return guest.to_dict(), 200

    def patch(self):
        data = request.get_json()
        guest_id = data.get("id")
        guest = Guest.query.get_or_404(guest_id)

        guest.name = data.get('name', guest.name)
        guest.email = data.get('email', guest.email)
        guest.rsvp_status = data.get('rsvp_status', guest.rsvp_status)

        db.session.commit()
        return guest.to_dict(), 200
   
    def delete(self, id):
        guest = Guest.query.get_or_404(id)
        
        db.session.delete(guest)
        db.session.commit()
        return '', 204


api.add_resource(Register, '/register', endpoint='register')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(Guests, '/guests', endpoint='guests')
api.add_resource(GuestByID, '/guests/<int:id>', endpoint='guest_by_id')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
