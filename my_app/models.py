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
    points = db.Column(db.Integer, default=0, nullable=False)
    # 状态: 0-正常, 1-封禁
    status = db.Column(db.SmallInteger, default=0, nullable=False)
    # 使用 back_populates 来明确指定反向关系的名称
    articles = db.relationship('KnowledgeArticle', back_populates='author', lazy=True)
    histories = db.relationship('QueryHistory', back_populates='owner', lazy='dynamic', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'status': self.status,
            'points': self.points
        }


class KnowledgeArticle(db.Model):
    __tablename__ = 'knowledgearticle'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    # 文章状态 (0: 已发布, 1: 已删除) 用于逻辑删除
    status = db.Column(db.SmallInteger, default=0, nullable=False)
    # 双向关系的定义
    author = db.relationship('User', back_populates='articles')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'author_id': self.author_id,
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


class QueryHistory(db.Model):
    __tablename__ = 'queryhistory'
    id = db.Column(db.Integer, primary_key=True, comment='记录ID, 主键, 自增')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, comment='用户ID, 外键, 关联User(id)')
    query_type = db.Column(db.String(20), nullable=False, comment="查询方式 ('text' 或 'image')")
    query_content = db.Column(db.Text, nullable=False, comment='查询内容 (文字或图片URL)')
    result_category = db.Column(db.String(50), nullable=False, comment='识别结果分类')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='查询时间')
    status = db.Column(db.SmallInteger, default=0, nullable=False, comment='记录状态 (0: 可查询, 1: 已删除)')

    # 定义与User模型的反向关系
    owner = db.relationship('User', back_populates='histories')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'query_type': self.query_type,
            'query_content': self.query_content,
            'result_category': self.result_category,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'status': self.status
        }


class Reward(db.Model):
    __tablename__ = 'reward'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='奖品ID, 主键, 自增')
    name = db.Column(db.String(100), nullable=False, comment='奖品名称')
    points_cost = db.Column(db.Integer, nullable=False, comment='兑换所需积分')
    stock = db.Column(db.Integer, nullable=False, comment='库存数量')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'points_cost': self.points_cost,
            'stock': self.stock
        }

class RedemptionHistory(db.Model):
    __tablename__ = 'redemptionhistory'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='兑换记录ID, 主键, 自增')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, comment='用户ID, 外键, 关联User(id)')
    reward_id = db.Column(db.Integer, db.ForeignKey('reward.id'), nullable=False, comment='奖品ID, 外键, 关联Reward(id)')
    points_spent = db.Column(db.Integer, nullable=False, comment='消耗积分')
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False, comment='兑换时间')
    phone_number = db.Column(db.String(50), nullable=False, comment='收货手机号')
    address = db.Column(db.String(255), nullable=False, comment='收货地址')

    # 关系
    reward = db.relationship('Reward', backref='redemption_history', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'reward_id': self.reward_id,
            'reward_name': self.reward.name if self.reward else None,
            'points_spent': self.points_spent,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'phone_number': self.phone_number,
            'address': self.address
        }