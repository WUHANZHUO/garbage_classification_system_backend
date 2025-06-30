# my_app/models.py

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()



class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.SmallInteger, nullable=False, default=0)
    points = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.SmallInteger, nullable=False, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'points': self.points,
            'status': self.status
        }


class KnowledgeArticle(db.Model):
    __tablename__ = 'KnowledgeArticle'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    status = db.Column(db.SmallInteger, default=0, nullable=False)
    updated_time = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    author = db.relationship('User', backref=db.backref('articles', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'author_id': self.author_id,
            'author_username': self.author.username if self.author else None,
            'status': self.status,
            'updated_time': self.updated_time.isoformat()
        }