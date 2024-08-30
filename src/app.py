from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite
import os

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

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

# USERS

@app.route('/users', methods=['GET'])
def get_users():
    all_users = User.query.all()
    return jsonify([user.serialize() for user in all_users]), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_single_user(user_id):
    single_user = User.query.get(user_id)
    if single_user is None:
        return jsonify({'msg': f'User with ID {user_id} does not exist'}), 404
    return jsonify(single_user.serialize()), 200

@app.route('/sign_up', methods=['POST'])
def add_single_user():
    request_body = request.json
    user_query = User.query.filter_by(email=request_body['email']).first()
    if user_query is None:
        new_user = User(
            username=request_body['name'],
            email=request_body['email'],
            password=request_body['password'],
            is_active=request_body['is_active']
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'msg': 'User successfully created'}), 200
    return jsonify({'msg': 'User already exists'}), 409

@app.route("/users/favorites/<int:user_id>", methods=["GET"])
def get_user_favorites(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    favorites = [{"id": fav.character.id, "name": fav.character.name} if fav.character else
                 {"id": fav.planet.id, "name": fav.planet.name} for fav in user.favorites]
    return jsonify(favorites), 200

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_single_user(user_id):
    user_to_delete = User.query.get(user_id)
    if user_to_delete:
        db.session.delete(user_to_delete)
        db.session.commit()
        return jsonify({'msg': 'User successfully deleted'}), 200
    return jsonify({'msg': 'User not found'}), 404

# CHARACTERS

@app.route("/character/<int:character_id>", methods=["GET"])
def get_character(character_id):
    character = Character.query.get(character_id)
    if character is None:
        return jsonify({"error": "Character not found"}), 404
    return jsonify(character.serialize()), 200

@app.route("/characters", methods=["GET"])
def get_all_characters():
    characters = Character.query.all()
    return jsonify([character.serialize() for character in characters]), 200

@app.route("/favorite/character/<int:character_id>", methods=["POST"])
def add_favorite_character(character_id):
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    character = Character.query.get(character_id)
    if character is None:
        return jsonify({"error": "Character not found"}), 404
    favorite = Favorite(user_id=user_id, character_id=character_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"message": "Favorite added"}), 200

@app.route("/favorite/character/<int:character_id>", methods=["DELETE"])
def delete_favorite_character(character_id):
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    favorite = Favorite.query.filter_by(user_id=user_id, character_id=character_id).first()
    if favorite is None:
        return jsonify({"error": "Favorite not found"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": "Favorite deleted"}), 200

# PLANETS

@app.route("/planets", methods=["GET"])
def get_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

@app.route("/planets/<int:planet_id>", methods=["GET"])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200

@app.route("/favorite/planet/<int:planet_id>", methods=["POST"])
def add_favorite_planet(planet_id):
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404
    favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"message": "Favorite added"}), 200

@app.route("/favorite/planet/<int:planet_id>", methods=["DELETE"])
def delete_favorite_planet(planet_id):
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if favorite is None:
        return jsonify({"error": "Favorite not found"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": "Favorite deleted"}), 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)