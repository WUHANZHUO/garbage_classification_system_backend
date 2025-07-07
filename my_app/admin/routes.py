# my_app/admin/routes.py
from flask import Blueprint, jsonify, request
from ..decorators import admin_required
from .services import (
    get_all_users_service, get_user_by_id_service,
    search_users_by_username_service, update_user_status_service,
    create_admin_user_service, set_user_password_service
)

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """获取所有用户列表"""
    users = get_all_users_service()
    return jsonify([user.to_dict() for user in users]), 200


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user_by_id(user_id):
    """获取单个用户详情"""
    user = get_user_by_id_service(user_id)
    return jsonify(user.to_dict()), 200


@admin_bp.route('/users/search', methods=['GET'])
@admin_required
def search_users_by_username():
    """(管理员)根据用户名模糊搜索用户"""
    username_query = request.args.get('username')
    if not username_query:
        return jsonify({'message': '缺少用户名查询参数 "username"'}), 400

    users = search_users_by_username_service(username_query)
    if not users:
        return jsonify({'message': '未找到匹配的用户', 'users': []}), 200

    return jsonify([user.to_dict() for user in users]), 200


@admin_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@admin_required
def update_user_status(user_id):
    """封禁或解封一个用户"""
    data = request.get_json()
    new_status = data.get('status')

    user, message = update_user_status_service(user_id, new_status)
    if not user:
        return jsonify({'message': message}), 400

    return jsonify({'message': message, 'user': user.to_dict()}), 200


@admin_bp.route('/users/create_admin', methods=['POST'])
@admin_required
def create_admin_user():
    """创建一个新的管理员账户"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    new_admin, message = create_admin_user_service(username, password)

    if message == "用户名已存在":
        return jsonify({'message': message}), 409

    return jsonify({'message': message, 'user': new_admin.to_dict()}), 201


@admin_bp.route('/users/<int:user_id>/set_password', methods=['PUT'])
@admin_required
def set_user_password(user_id):
    """(管理员)重置或修改指定用户的密码"""
    data = request.get_json()
    new_password = data.get('new_password')

    user, message = set_user_password_service(user_id, new_password)
    if not user:
        return jsonify({'message': message}), 400

    return jsonify({'message': message}), 200