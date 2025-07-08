# my_app/recognition/routes.py
import os

from flask import Blueprint, request, jsonify, g, send_from_directory
from .services import recognize_text_service, recognize_image_service
from ..decorators import login_required

recognition_bp = Blueprint('recognition', __name__, url_prefix='/api/recognize')


@recognition_bp.route('/image', methods=['POST'])
@login_required
def recognize_image():
    """图片识别接口"""
    if 'file' not in request.files:
        return jsonify({'message': '缺少图片文件'}), 400

    file = request.files['file']
    category, probability, message = recognize_image_service(file, g.user)

    if category is None:
        if "缺少" in message:
            return jsonify({'message': message}), 400
        if "无效" in message:
             return jsonify({'message': message}), 422
        return jsonify({'message': message}), 500

    return jsonify({
        'message': message,
        'category': category,
        'probability': float(probability)
    }), 200


@recognition_bp.route('/text', methods=['GET'])
@login_required
def recognize_text():
    """文字识别（模糊搜索）接口"""
    query = request.args.get('q', type=str)

    if not query:
        return jsonify({'message': '缺少查询参数 `q`'}), 400

    result = recognize_text_service(query, g.user)

    if not result:
        return jsonify({'message': '未找到匹配的垃圾信息', 'results': []}), 200

    return jsonify(result.to_dict()), 200


@recognition_bp.route('/uploads/<path:filename>')
# @login_required
def get_uploaded_image(filename):
    """
    为 uploads 文件夹中的图片提供访问路由
    """
    upload_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    return send_from_directory(upload_folder, filename)