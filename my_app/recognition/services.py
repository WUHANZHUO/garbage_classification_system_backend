# my_app/recognition/services.py
import os
import uuid
from flask import current_app, url_for
from werkzeug.utils import secure_filename
from .image_model import classify_image
from ..models import db, GarbageItem, QueryHistory


def recognize_text_service(query, user):
    """文字识别及记录历史的业务逻辑"""
    search_term = f"%{query}%"
    result = GarbageItem.query.filter(GarbageItem.name.ilike(search_term)).first()

    result_category = result.category if result else '未找到'

    # 增加积分并记录历史
    user.points += 1
    new_history = QueryHistory(
        user_id=user.id,
        query_type='text',
        query_content=query,
        result_category=result_category
    )
    db.session.add(new_history)
    db.session.commit()

    return result


def recognize_image_service(file, user):
    """图片识别、保存、记录历史的业务逻辑"""
    if not file or file.filename == '':
        return None, None, "缺少或未选择文件"

    try:
        # 1. 保存图片
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'
        unique_filename = f"{uuid.uuid4()}.{ext}"

        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        upload_path = os.path.join(upload_folder, unique_filename)
        file.save(upload_path)

        # 2. 调用模型分类
        category, probability = classify_image(upload_path)

        if category is None:
            return None, None, "图片文件无效或无法处理"

        # 3. 增加积分并记录历史
        user.points += 1
        image_url = url_for('static', filename=f'uploads/{unique_filename}', _external=True)
        new_history = QueryHistory(
            user_id=user.id,
            query_type='image',
            query_content=image_url,  # 存储可访问的URL
            result_category=category
        )
        db.session.add(new_history)
        db.session.commit()

        return category, probability, "识别成功"
    except Exception as e:
        # 可以添加日志记录
        print(f"Error in recognize_image_service: {e}")
        return None, None, "服务器端发生未知错误"