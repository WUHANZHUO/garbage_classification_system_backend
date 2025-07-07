# my_app/auth/services.py
from flask import current_app
from datetime import datetime, timedelta
import jwt
from ..models import db, User, bcrypt


def register_user_service(username, password):
    """用户注册业务逻辑"""
    if User.query.filter_by(username=username).first():
        return None, "用户名已存在"

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return new_user, "用户注册成功"


def login_user_service(username, password):
    """用户登录业务逻辑"""
    user = User.query.filter_by(username=username).first()

    if not user or not bcrypt.check_password_hash(user.password, password):
        return None, "用户名或密码错误", None

    if user.status == 1:
        return None, "该账户已被封禁，请联系管理员", None

    payload = {
        'sub': str(user.id),
        'iat': datetime.now().astimezone(),
        'exp': datetime.now().astimezone() + timedelta(hours=24)
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

    return user, "登录成功", token


def change_password_service(user, current_password, new_password):
    """用户修改密码业务逻辑"""
    if not current_password or not new_password:
        return False, "请求参数不完整"

    if not bcrypt.check_password_hash(user.password, current_password):
        return False, "当前密码不正确"

    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    user.password = hashed_password
    db.session.commit()
    return True, "密码修改成功"