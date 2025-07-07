# my_app/auth/routes.py
from flask import request, jsonify, Blueprint, g
from .services import register_user_service, login_user_service, change_password_service
from ..decorators import login_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user, message = register_user_service(data.get('username'), data.get('password'))
    if not user:
        return jsonify({'message': message}), 409
    return jsonify({'message': message}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user, message, token = login_user_service(data.get('username'), data.get('password'))

    if not user:
        # 根据消息内容判断是密码错误还是账户封禁
        if "封禁" in message:
            return jsonify({'message': message}), 403
        else:
            return jsonify({'message': message}), 401

    return jsonify({'message': message, 'token': token, 'role': user.role}), 200


@auth_bp.route('/change_password', methods=['PUT'])
@login_required
def change_password():
    """用户修改自己的密码"""
    user = g.user
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    success, message = change_password_service(user, current_password, new_password)

    if not success:
        if "参数" in message:
            return jsonify({'message': message}), 400
        else:
            return jsonify({'message': message}), 403

    return jsonify({'message': message}), 200


@auth_bp.route('/get_info', methods=['GET'])
@login_required
def get_me():
    """获取当前登录用户的详细信息"""
    user = g.user
    return jsonify(user.to_dict()), 200