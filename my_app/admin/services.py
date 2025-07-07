# my_app/admin/services.py
from ..models import db, User, bcrypt


def get_all_users_service():
    """获取所有用户的业务逻辑"""
    return User.query.all()


def get_user_by_id_service(user_id):
    """根据ID获取单个用户的业务逻辑"""
    return User.query.get_or_404(user_id)


def search_users_by_username_service(username_query):
    """根据用户名模糊搜索用户的业务逻辑"""
    search_term = f"%{username_query}%"
    return User.query.filter(User.username.ilike(search_term)).all()


def update_user_status_service(user_id, new_status):
    """更新用户状态的业务逻辑"""
    user = get_user_by_id_service(user_id)
    if new_status not in [0, 1]:
        # 在服务层可以返回错误信息或抛出异常
        return None, "无效的状态值"
    user.status = new_status
    db.session.commit()
    return user, "用户状态已更新"


def create_admin_user_service(username, password):
    """创建管理员账户的业务逻辑"""
    if User.query.filter_by(username=username).first():
        return None, "用户名已存在"

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_admin = User(username=username, password=hashed_password, role=1)

    db.session.add(new_admin)
    db.session.commit()
    return new_admin, "管理员账户创建成功"


def set_user_password_service(user_id, new_password):
    """(管理员)重置用户密码的业务逻辑"""
    if not new_password:
        return None, "缺少新密码"

    user = get_user_by_id_service(user_id)
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    user.password = hashed_password
    db.session.commit()
    return user, f"用户 '{user.username}' 的密码已更新"