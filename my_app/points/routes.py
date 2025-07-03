# my_app/points/routes.py
from flask import Blueprint, jsonify, g, request
from ..models import db, Reward, RedemptionHistory, User
from ..decorators import login_required, admin_required

points_bp = Blueprint('points', __name__, url_prefix='/api/points')


@points_bp.route('/rewards', methods=['GET'])
@login_required
def get_rewards():
    """获取所有可兑换的奖品列表"""
    rewards = Reward.query.filter(Reward.stock >= 0).all()
    return jsonify([reward.to_dict() for reward in rewards]), 200


@points_bp.route('/rewards/get/<int:reward_id>', methods=['POST'])
@login_required
def redeem_reward(reward_id):
    """用户兑换奖品"""
    user = g.user
    reward = Reward.query.get(reward_id)

    if not reward:
        return jsonify({'message': '奖品不存在'}), 404

    if reward.stock <= 0:
        return jsonify({'message': '奖品库存不足'}), 400

    if user.points < reward.points_cost:
        return jsonify({'message': '用户积分不足'}), 400

    try:
        # 扣除用户积分
        user.points -= reward.points_cost
        # 减少奖品库存
        reward.stock -= 1

        # 创建兑换历史记录
        new_redemption = RedemptionHistory(
            user_id=user.id,
            reward_id=reward.id,
            points_spent=reward.points_cost
        )
        db.session.add(new_redemption)

        # 提交事务
        db.session.commit()

        return jsonify({
            'message': '兑换成功',
            'remaining_points': user.points
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'处理兑换时发生错误: {e}'}), 500


@points_bp.route('/rewards/history', methods=['GET'])
@login_required
def get_redemption_history():
    """获取当前用户的兑换历史"""
    user = g.user
    history = RedemptionHistory.query.filter_by(user_id=user.id).order_by(RedemptionHistory.created_at.desc()).all()
    return jsonify([item.to_dict() for item in history]), 200


@points_bp.route('/reward/history/<int:user_id>', methods=['GET'])
@login_required
@admin_required
def get_user_redemption_history(user_id):
    """(管理员) 获取指定用户的兑换历史"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': '用户不存在'}), 404

    history = RedemptionHistory.query.filter_by(user_id=user_id).order_by(RedemptionHistory.created_at.desc()).all()
    return jsonify([item.to_dict() for item in history]), 200
