# my_app/history/routes.py
from flask import Blueprint, jsonify, g
from ..models import db, QueryHistory, User
from ..decorators import login_required, admin_required

history_bp = Blueprint('history', __name__, url_prefix='/api/history')


@history_bp.route('/my', methods=['GET'])
@login_required
def get_my_history():
    """(用户)查询自己的识别历史记录"""
    user_id = g.user.id
    # 只查询 status 为 0 的正常记录
    histories = QueryHistory.query.filter_by(user_id=user_id, status=0).order_by(QueryHistory.created_at.desc()).all()
    return jsonify([h.to_dict() for h in histories]), 200


@history_bp.route('/user/<int:user_id>', methods=['GET'])
@admin_required
def get_user_history(user_id):
    """(管理员)查看指定用户的识别历史记录"""
    # 验证用户是否存在
    user = User.query.get_or_404(user_id)
    # 管理员可以查看所有记录，包括已删除的
    histories = QueryHistory.query.filter_by(user_id=user_id).order_by(QueryHistory.created_at.desc()).all()
    return jsonify([h.to_dict() for h in histories]), 200


@history_bp.route('/delete/<int:history_id>', methods=['DELETE'])
@login_required
def delete_history(history_id):
    """(用户)逻辑删除自己的识别历史记录"""
    history_record = QueryHistory.query.get_or_404(history_id)

    # 权限验证：确保用户只能删除自己的记录
    if history_record.user_id != g.user.id:
        return jsonify({'message': '无权操作此记录'}), 403

    # 逻辑删除：将 status 设置为 1
    history_record.status = 1
    db.session.commit()

    return jsonify({'message': '历史记录已删除'}), 200