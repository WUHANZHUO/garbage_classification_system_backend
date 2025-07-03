# my_app/auth/routes.py

from flask import request, jsonify, Blueprint, current_app, g
from datetime import datetime, timedelta
import jwt
from ..models import db, User, bcrypt
from ..decorators import login_required

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
            'sub': str(user.id),
            'iat': datetime.now().astimezone(),
            'exp': datetime.now().astimezone() + timedelta(hours=24)
        }
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({'message': '登录成功', 'token': token, 'role':user.role}), 200

    # 如果用户不存在或密码错误，返回 401
    return jsonify({'message': '用户名或密码错误'}), 401

@auth_bp.route('/change_password', methods=['PUT'])
@login_required
def change_password():
    """用户修改自己的密码"""
    user = g.current_user
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not current_password or not new_password:
        return jsonify({'message': '请求参数不完整'}), 400

    # 验证当前密码
    if not bcrypt.check_password_hash(user.password, current_password):
        return jsonify({'message': '当前密码不正确'}), 403

    # 更新密码
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    user.password = hashed_password
    db.session.commit()

    return jsonify({'message': '密码修改成功'}), 200


@auth_bp.route('/get_info', methods=['GET'])
@login_required
def get_me():
    """获取当前登录用户的详细信息"""
    # @login_required 装饰器已将用户信息放入 g.user
    user = g.user
    return jsonify(user.to_dict()), 200