# my_app/admin/routes.py
from flask import Blueprint, jsonify, request, g
from ..models import db, User, bcrypt
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


@admin_bp.route('/users/search', methods=['GET'])
@admin_required
def search_users_by_username():
    """(管理员)根据用户名模糊搜索用户"""
    username_query = request.args.get('username')

    if not username_query:
        return jsonify({'message': '缺少用户名查询参数 "username"'}), 400

    # 模糊查询
    search_term = f"%{username_query}%"
    users = User.query.filter(User.username.ilike(search_term)).all()

    if not users:
        return jsonify({'message': '未找到匹配的用户', 'users': []}), 200

    return jsonify([user.to_dict() for user in users]), 200


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


@admin_bp.route('/users/<int:user_id>/set_password', methods=['PUT'])
@admin_required
def set_user_password(user_id):
    """(管理员)重置或修改指定用户的密码"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    new_password = data.get('new_password')

    if not new_password:
        return jsonify({'message': '缺少新密码'}), 400

    # 管理员可以直接设置新密码
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    user.password = hashed_password
    db.session.commit()

    return jsonify({'message': f"用户 '{user.username}' 的密码已更新"}), 200