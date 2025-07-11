# my_app/articles/routes.py
from flask import Blueprint, jsonify, request, g
from .services import (
    get_published_articles_service,
    search_articles_by_title_service,
    get_published_article_detail_service,
    create_article_service,
    update_article_service,
    delete_article_service
)
from ..decorators import admin_required

articles_bp = Blueprint('articles', __name__, url_prefix='/api/articles')


# (无需登录)
@articles_bp.route('/get', methods=['GET'])
def get_article_list():
    """获取已发布的文章列表"""
    articles = get_published_articles_service()
    return jsonify([article.to_dict() for article in articles]), 200


@articles_bp.route('/search', methods=['GET'])
def search_articles():
    """根据标题模糊搜索知识文章"""
    title_query = request.args.get('title')

    if not title_query:
        return jsonify({'message': '缺少标题查询参数 "title"'}), 400

    articles = search_articles_by_title_service(title_query)
    return jsonify([article.to_dict() for article in articles]), 200


@articles_bp.route('/get/<int:article_id>', methods=['GET'])
def get_article_detail(article_id):
    """获取单篇已发布的文章详情"""
    article = get_published_article_detail_service(article_id)
    return jsonify(article.to_dict()), 200


@articles_bp.route('/create', methods=['POST'])
@admin_required
def create_article():
    """管理员：创建新文章"""
    data = request.get_json()
    author_id = g.user.id  # 作者 ID 就是当前登录的管理员

    new_article = create_article_service(data.get('title'), data.get('content'), author_id)
    return jsonify({'message': '文章创建成功', 'article': new_article.to_dict()}), 201


@articles_bp.route('/revise/<int:article_id>', methods=['PUT'])
@admin_required
def update_article(article_id):
    """管理员：修改文章"""
    data = request.get_json()
    article = update_article_service(article_id, data)
    return jsonify({'message': '文章更新成功', 'article': article.to_dict()}), 200


@articles_bp.route('/delete/<int:article_id>', methods=['DELETE'])
@admin_required
def delete_article(article_id):
    """管理员：逻辑删除文章"""
    delete_article_service(article_id)
    return jsonify({'message': '文章已删除'}), 200