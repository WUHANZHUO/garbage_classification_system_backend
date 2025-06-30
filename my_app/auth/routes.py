# my_app/auth/routes.py

from flask import request, jsonify, Blueprint, current_app
from datetime import datetime, timedelta
import jwt
from ..models import db, User, bcrypt

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({'message': '用户名已存在'}), 409
    hashed_password = bcrypt.generate_password_hash(data.get('password')).decode('utf-8')
    new_user = User(username=data.get('username'), password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': '用户注册成功'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()

    # 1. 首先，验证用户是否存在且密码是否正确
    if user and bcrypt.check_password_hash(user.password, data.get('password')):

        # 2. 新增：在密码验证成功后，检查账户状态
        if user.status == 1:
            # 如果 status 为 1，代表账户被封禁
            return jsonify({'message': '该账户已被封禁，请联系管理员'}), 403  # 403 Forbidden

        # print(f"--- 签发Token的SECRET_KEY: {current_app.config['SECRET_KEY']} ---")

        # 3. 如果账户状态正常 (status == 0)，则正常生成并返回 token
        payload = {
            'sub': user.id,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({'message': '登录成功', 'token': token, 'role':user.role}), 200

    # 如果用户不存在或密码错误，返回 401
    return jsonify({'message': '用户名或密码错误'}), 401