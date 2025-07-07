# my_app/history/routes.py
from flask import Blueprint, jsonify, g
from ..decorators import login_required, admin_required
from .services import get_history_by_user_id_service, delete_history_service

history_bp = Blueprint('history', __name__, url_prefix='/api/history')


@history_bp.route('/my', methods=['GET'])
@login_required
def get_my_history():
    """(用户)查询自己的识别历史记录"""
    user_id = g.user.id
    histories = get_history_by_user_id_service(user_id, is_admin=False)
    return jsonify([h.to_dict() for h in histories]), 200


@history_bp.route('/user/<int:user_id>', methods=['GET'])
@admin_required
def get_user_history(user_id):
    """(管理员)查看指定用户的识别历史记录"""
    histories = get_history_by_user_id_service(user_id, is_admin=True)
    return jsonify([h.to_dict() for h in histories]), 200


@history_bp.route('/delete/<int:history_id>', methods=['DELETE'])
@login_required
def delete_history(history_id):
    """(用户)逻辑删除自己的识别历史记录"""
    success, message = delete_history_service(history_id, g.user.id)

    if not success:
        return jsonify({'message': message}), 403  # 403 Forbidden

    return jsonify({'message': message}), 200