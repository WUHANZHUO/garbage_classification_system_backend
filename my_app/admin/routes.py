# my_app/admin/routes.py
from flask import Blueprint, jsonify, request, g
from ..models import db, User
from ..decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """获取所有用户列表"""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user_by_id(user_id):
    """获取单个用户详情"""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200


@admin_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@admin_required
def update_user_status(user_id):
    """封禁或解封一个用户"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    new_status = data.get('status')

    if new_status not in [0, 1]:
        return jsonify({'message': '无效的状态值'}), 400

    user.status = new_status
    db.session.commit()
    return jsonify({'message': f'用户 {user.username} 状态已更新', 'user': user.to_dict()}), 200


@admin_bp.route('/users/create_admin', methods=['POST'])
@admin_required
def create_admin_user():
    """创建一个新的管理员账户"""
    # 借用注册逻辑
    data = request.get_json()
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({'message': '用户名已存在'}), 409

    from ..models import bcrypt
    hashed_password = bcrypt.generate_password_hash(data.get('password')).decode('utf-8')
    new_admin = User(username=data.get('username'), password=hashed_password, role=1)

    db.session.add(new_admin)
    db.session.commit()
    return jsonify({'message': '管理员账户创建成功', 'user': new_admin.to_dict()}), 201