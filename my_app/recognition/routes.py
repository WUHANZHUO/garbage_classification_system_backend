# my_app/recognition/routes.py
import os
from flask import Blueprint, request, jsonify, current_app, g, url_for
import uuid
from .image_model import classify_image
from ..models import GarbageItem, QueryHistory
from .. import  db
from werkzeug.utils import  secure_filename
from ..decorators import login_required

recognition_bp = Blueprint('recognition', __name__, url_prefix='/api/recognize')


@recognition_bp.route('/image', methods=['POST'])
@login_required
def recognize_image():
    """
    图片识别接口（已恢复并优化，需要登录并记录历史）
    """
    if 'file' not in request.files:
        return jsonify({'message': '缺少图片文件'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'message': '未选择文件'}), 400

    if file:
        # 1. 安全地保存图片文件
        # 使用 secure_filename 过滤掉不安全的文件名
        filename = secure_filename(file.filename)
        # 使用 UUID 生成唯一文件名，防止重名覆盖
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'
        unique_filename = f"{uuid.uuid4()}.{ext}"

        upload_folder = current_app.config['UPLOAD_FOLDER']
        # 确保上传目录存在
        os.makedirs(upload_folder, exist_ok=True)

        upload_path = os.path.join(upload_folder, unique_filename)
        file.save(upload_path)

        # 2. 调用模型进行分类，传入保存后的图片路径
        category, probability = classify_image(upload_path)

        if category and probability is not None:
            # 3. 写入历史记录
            # 生成可供外部访问的图片URL
            image_url = url_for('static', filename=f'uploads/{unique_filename}', _external=True)

            new_history = QueryHistory(
                user_id=g.user.id,
                query_type='image',
                query_content=image_url,
                result_category=category
            )
            db.session.add(new_history)
            db.session.commit()

            return jsonify({
                'message': '识别成功',
                'category': category,
                'probability': float(probability)  # 确保返回的是标准的float类型
            }), 200
        else:
            return jsonify({'message': '图片文件无效或无法处理'}), 422

    return jsonify({'message': '服务器端发生未知错误'}), 500



@recognition_bp.route('/text', methods=['GET'])
@login_required
def recognize_text():
    """
    文字识别（模糊搜索）接口
    """
    query = request.args.get('q', type=str)

    if not query:
        return jsonify({'message': '缺少查询参数 `q`'}), 400

    search_term = f"%{query}%"
    result = GarbageItem.query.filter(GarbageItem.name.ilike(search_term)).first()

    # 2. 直接访问【单个对象】的属性，不再需要 [0]
    result_category = result.category if result else '未找到'

    # 写入历史记录
    new_history = QueryHistory(
        user_id=g.user.id,
        query_type='text',
        query_content=query,
        result_category=result_category
    )
    db.session.add(new_history)
    db.session.commit()

    if not result:
        return jsonify({'message': '未找到匹配的垃圾信息', 'results': []}), 200  # 改为200，因为查询本身是成功的

    return jsonify(result.to_dict()), 200