# my_app/decorators.py
from functools import wraps
from flask import request, jsonify, g, current_app
import jwt
from .models import User

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': '令牌格式错误，应为 "Bearer <token>"'}), 401

        if not token:
            return jsonify({'message': '缺少认证令牌'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(int(data['sub']))

            if not current_user:
                return jsonify({'message': '无效的用户'}), 401

            # 检查账户是否被封禁
            if current_user.status == 1:
                return jsonify({'message': '该账户已被封禁'}), 403

            g.user = current_user

        except jwt.ExpiredSignatureError:
            return jsonify({'message': '令牌已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': '无效的令牌'}), 401

        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None

        # 1. 检查并打印原始请求头
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']

            # 诊断：打印出收到的完整原始请求头
            # print(f"--- 诊断: 收到的原始Header是 -> '{auth_header}'")

            # 2. 尝试解析Token
            try:
                token = auth_header.split(" ")[1]
                # 诊断：打印出解析后准备用于解码的token
                # print(f"--- 诊断: 解析出的Token是 -> '{token}'")
            except IndexError:
                # print("--- 诊断错误: Header格式不正确，无法用空格分割出Token ---")
                return jsonify({'message': '令牌格式错误，应为 "Bearer <token>"'}), 401

        if not token:
            return jsonify({'message': '缺少认证令牌'}), 401

        # 3. 尝试解码Token
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(int(data['sub']))

            if not current_user:
                return jsonify({'message': '无效的用户'}), 401

            if current_user.role != 1:
                return jsonify({'message': '需要管理员权限'}), 403

            g.user = current_user

        except jwt.ExpiredSignatureError:
            return jsonify({'message': '令牌已过期'}), 401
        except jwt.InvalidTokenError:
            # print(f"--- 诊断失败: jwt.decode 验证签名失败！请仔细对比上方解析出的Token与你复制的是否逐字一致。---")
            return jsonify({'message': '无效的令牌'}), 401
        #except jwt.InvalidTokenError as e:
        #    print(f"解码失败详细错误: {type(e).__name__}: {str(e)}")
        #    print(f"错误类型: {type(e)}")
        #    return jsonify({'message': '无效的令牌'}), 401

        return f(*args, **kwargs)

    return decorated_function