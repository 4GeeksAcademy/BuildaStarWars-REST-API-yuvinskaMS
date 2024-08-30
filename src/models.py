from flask_sqlalchemy import SQLAlchemy



db = SQLAlchemy()


#aqui vamos a escribir todas las tablas(objetos)
#serialize -> crea un diccionaria con toda la informacion del objeto para enviarla atravez de API
#__repr__ -> nos ayuda a visualizar el codigo convirtiendolo en texto



class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    favorites = db.relationship('Favorite', backref = 'user', lazy = True)

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            #"password": self.password,
            "is_active": self.is_active,
            "favorites": [favorite.serialize() for favorite in self.favorites]

            
        }
class Character(db.Model):
    __tablename__= 'character'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30),index=True, nullable=False)
    gender = db.Column(db.String(10),unique=False, nullable=False)
    height = db.Column(db.String(5), nullable=False)
    weight = db.Column(db.String(5), nullable=False)
    hair_color = db.Column(db.String(15), nullable=True)
    skin_color = db.Column(db.String(15), nullable=True)
    favorites = db.relationship('Favorite', backref = 'character', lazy = True)
    


    def __repr__(self):
        return '<Characters %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "height": self.height,
            "weight": self.weight,
            "hair_color": self.hair_color,
            "skin_color": self.skin_color
        }


class Planet(db.Model):
    __tablename__= 'planet'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30),index=True, nullable=False)
    territory = db.Column(db.String(25), nullable=False)
    population = db.Column(db.String(15), nullable=False)
    diameter = db.Column(db.String(10), nullable=False)
    favorites = db.relationship('Favorite', backref = 'planet', lazy = True)

    def __repr__(self):
        return '<Planets %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "territory": self.territory,
            "population": self.population,
            "diameter": self.diameter
        }


class Favorite(db.Model):
    __tablename__= 'favorite'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'), nullable=True)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=True)

    def __repr__(self):
        return '<Favourites %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id,
            "character_id": self.character_id,
            "user": self.user.serialize() if self.user else None, 
            "planet": self.planet.serialize() if self.planet else None, 
            "character": self.character.serialize() if self.character else None, 
            
        }