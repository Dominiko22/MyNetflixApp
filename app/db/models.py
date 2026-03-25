"""
Moduł definicji modeli bazy danych (SQLAlchemy).
Zgodnie z wzorcem App Factory, przechowuje instancję `db` oraz schematy tabel (User, Favorite).
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    favorites = db.relationship('Favorite', backref='owner', lazy=True)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_email = db.Column(db.String(120), index=True, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(120), nullable=False)
    poster = db.Column(db.String(500))
