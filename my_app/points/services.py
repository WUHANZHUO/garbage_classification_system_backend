# my_app/points/services.py
from ..models import db, Reward, RedemptionHistory, User


def get_rewards_service():
    """获取所有可兑换奖品的业务逻辑"""
    return Reward.query.filter(Reward.stock > 0).all()


def redeem_reward_service(user, reward_id, phone_number, address):
    """用户兑换奖品的业务逻辑"""
    reward = Reward.query.get(reward_id)

    if not reward:
        return None, "奖品不存在"
    if reward.stock <= 0:
        return None, "奖品库存不足"
    if user.points < reward.points_cost:
        return None, "用户积分不足"

    try:
        user.points -= reward.points_cost
        reward.stock -= 1
        new_redemption = RedemptionHistory(
            user_id=user.id,
            reward_id=reward.id,
            points_spent=reward.points_cost,
            phone_number=phone_number,
            address=address
        )
        db.session.add(new_redemption)
        db.session.commit()
        return user, "兑换成功"
    except Exception as e:
        db.session.rollback()
        return None, f"处理兑换时发生错误: {e}"


def get_redemption_history_service(user_id):
    """获取指定用户兑换历史的业务逻辑"""
    User.query.get_or_404(user_id) # 确保用户存在
    return RedemptionHistory.query.filter_by(user_id=user_id).order_by(RedemptionHistory.created_at.desc()).all()