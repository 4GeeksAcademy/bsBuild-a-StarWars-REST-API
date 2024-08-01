import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite
#from models import Person
app = Flask(__name__)
app.url_map.strict_slashes = False
db_url = os.getenv("DATABASE_URL")

if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code
# generate sitemap with all your endpoints

#home route
@app.route('/')
def sitemap():
    return generate_sitemap(app)

#GET PEOPLE
@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    people_list = [person.serialize() for person in people]
    return jsonify(people_list), 200

#GET PEOPLE BY ID
@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.get(people_id)
    return jsonify(person.serialize()), 200

#GET PLANETS
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    planets_list = [planet.serialize() for planet in planets]
    return jsonify(planets_list), 200

#GET PLANET BY ID
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    return jsonify(planet.serialize()), 200

#GET USERS
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_list = [user.serialize() for user in users]
    return jsonify(users_list), 200

#DELETE USER BY ID
@app.route('/admin/user/delete/<int:user_id>', methods=['DELETE'])
def delete_planet(user_id):
    user = User.query.get(user_id)
    print('----------'+str(user))
    
    Favorite.query.filter_by(user_id=user_id).delete()
    User.query.filter_by(id=user_id).delete()
    db.session.commit()
    return '',200
 
    
#USER GET FAVS
@app.route('/users/favorites/', methods=['GET'])
def get_user_favorites():
    user_test = 4
    print('here '+ str(user_test))
    user = User.query.get(user_test)
    favorites = Favorite.query.filter_by(user_id=user.id).all()
    favorites_list = [favorite.serialize() for favorite in favorites]
    return jsonify(favorites_list), 200

#ADD FAV PLANET
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_test = 4
    try:
        #user_id = request.json.get('user_test')
        if not user_test:
            return jsonify({"message": "User ID is required"}), 400
        
        user = User.query.get(user_test)
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        planet = Planet.query.get(planet_id)
        if not planet:
            return jsonify({"message": "Planet not found"}), 404
        
        favorite = Favorite(user_id=user.id, planet_id=planet_id)
        db.session.add(favorite)
        db.session.commit()
        
        return jsonify(favorite.serialize()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


#ADD FAV CHARACTER
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    try:
        user_test = 4
        #user_id = request.json.get('user_id')
        if not user_test:
            return jsonify({"message": "User ID is required"}), 400
        
        user = User.query.get(user_test)
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        person = People.query.get(people_id)
        if not person:
            return jsonify({"message": "Person not found"}), 404
        
        favorite = Favorite(user_id=user.id, people_id=people_id)
        db.session.add(favorite)
        db.session.commit()
        
        return jsonify(favorite.serialize()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


#DELETE PLANET FAV
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet_route(planet_id):  # Updated function name
    try:
        user_test = 4
       #user_id = request.json.get('user_id')
        if not user_test:
            return jsonify({"message": "User ID is required"}), 400
        
        user = User.query.get(user_test)
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        favorite = Favorite.query.filter_by(user_id=user.id, planet_id=planet_id).first()
        if not favorite:
            return jsonify({"message": "Favorite not found"}), 404
        
        db.session.delete(favorite)
        db.session.commit()
        
        return jsonify({"message": "Favorite deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


#DELETE CHARACTER FAV
@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people_route(people_id):  # Updated function name
    try:
        user_test = 4
        #user_id = request.json.get('user_id')
        if not user_test:
            return jsonify({"message": "User ID is required"}), 400
        
        user = User.query.get(user_test)
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        favorite = Favorite.query.filter_by(user_id=user.id, people_id=people_id).first()
        if not favorite:
            return jsonify({"message": "Favorite not found"}), 404
        
        db.session.delete(favorite)
        db.session.commit()
        
        return jsonify({"message": "Favorite deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)