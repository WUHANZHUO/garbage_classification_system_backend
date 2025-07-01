# my_app/models.py
from . import db, bcrypt
from datetime import datetime


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    # 角色: 0-普通用户, 1-管理员
    role = db.Column(db.SmallInteger, default=0, nullable=False)
    # 状态: 0-正常, 1-封禁
    status = db.Column(db.SmallInteger, default=0, nullable=False)

    # 使用 back_populates 来明确指定反向关系的名称
    articles = db.relationship('KnowledgeArticle', back_populates='author', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'status': self.status
        }


class KnowledgeArticle(db.Model):
    __tablename__ = 'knowledgearticle'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    # 文章状态 (0: 已发布, 1: 已删除) -> 用于逻辑删除
    status = db.Column(db.SmallInteger, default=0, nullable=False)

    # 添加这一行，来完成双向关系的定义
    author = db.relationship('User', back_populates='articles')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'author_id': self.author_id,
            # 这里的 self.author 依然可以正常工作
            'author_name': self.author.username if self.author else 'N/A',
            'updated_time': self.updated_time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': self.status
        }

class GarbageItem(db.Model):
    __tablename__ = 'garbage_item'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True) # 为名称添加索引以提高搜索速度
    category = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category
        }