# my_app/recognition/routes.py
from flask import Blueprint, request, jsonify
from .image_model import classify_image
from ..models import GarbageItem

recognition_bp = Blueprint('recognition', __name__, url_prefix='/api/recognize')



@recognition_bp.route('/text', methods=['GET'])
def recognize_text():
    """
    文字识别（模糊搜索）接口
    """
    query = request.args.get('q', type=str)

    if not query:
        return jsonify({'message': '缺少查询参数 q'}), 400

    # 使用 ilike 进行模糊、不区分大小写的搜索
    search_term = f"%{query}%"
    results = GarbageItem.query.filter(GarbageItem.name.ilike(search_term)).limit(10).all()

    if not results:
        return jsonify({'message': '未找到匹配的垃圾信息'}), 404

    return jsonify([item.to_dict() for item in results]), 200