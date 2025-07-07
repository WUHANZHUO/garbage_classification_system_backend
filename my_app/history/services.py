# my_app/history/services.py
from ..models import db, QueryHistory, User


def get_history_by_user_id_service(user_id, is_admin=False):
    """
    根据用户ID获取历史记录的业务逻辑
    :param user_id: 用户ID
    :param is_admin: 是否为管理员查询。管理员可查看所有状态的记录
    :return: 历史记录列表
    """
    # 验证用户是否存在
    user = User.query.get_or_404(user_id)

    query = QueryHistory.query.filter_by(user_id=user_id)

    if not is_admin:
        # 普通用户只能查询 status 为 0 的正常记录
        query = query.filter_by(status=0)

    return query.order_by(QueryHistory.created_at.desc()).all()


def delete_history_service(history_id, current_user_id):
    """
    逻辑删除历史记录的业务逻辑
    :param history_id: 要删除的历史记录ID
    :param current_user_id: 当前操作用户的ID
    :return: (True, "删除成功") 或 (False, "错误信息")
    """
    history_record = QueryHistory.query.get_or_404(history_id)

    # 权限验证：确保用户只能删除自己的记录
    if history_record.user_id != current_user_id:
        return False, "无权操作此记录"

    # 逻辑删除：将 status 设置为 1
    history_record.status = 1
    db.session.commit()

    return True, "历史记录已删除"