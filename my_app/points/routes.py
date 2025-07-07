# my_app/points/routes.py
from flask import Blueprint, jsonify, g
from .services import get_rewards_service, redeem_reward_service, get_redemption_history_service
from ..decorators import login_required, admin_required

points_bp = Blueprint('points', __name__, url_prefix='/api/points')


@points_bp.route('/rewards', methods=['GET'])
@login_required
def get_rewards():
    """获取所有可兑换的奖品列表"""
    rewards = get_rewards_service()
    return jsonify([reward.to_dict() for reward in rewards]), 200


@points_bp.route('/rewards/get/<int:reward_id>', methods=['POST'])
@login_required
def redeem_reward(reward_id):
    """用户兑换奖品"""
    user, message = redeem_reward_service(g.user, reward_id)

    if not user:
        if "不存在" in message:
            return jsonify({'message': message}), 404
        if "不足" in message:
            return jsonify({'message': message}), 400
        # 其他错误
        return jsonify({'message': message}), 500

    return jsonify({
        'message': message,
        'remaining_points': user.points
    }), 200


@points_bp.route('/rewards/history', methods=['GET'])
@login_required
def get_redemption_history():
    """获取当前用户的兑换历史"""
    history = get_redemption_history_service(g.user.id)
    return jsonify([item.to_dict() for item in history]), 200


@points_bp.route('/reward/history/<int:user_id>', methods=['GET'])
@login_required
@admin_required
def get_user_redemption_history(user_id):
    """(管理员) 获取指定用户的兑换历史"""
    history = get_redemption_history_service(user_id)
    return jsonify([item.to_dict() for item in history]), 200