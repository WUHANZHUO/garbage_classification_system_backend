# my_app/articles/routes.py
from flask import Blueprint, jsonify, request, g
from ..models import db, KnowledgeArticle
from ..decorators import admin_required

articles_bp = Blueprint('articles', __name__, url_prefix='/api/articles')


# (无需登录)
@articles_bp.route('/get', methods=['GET'])
def get_article_list():
    """获取已发布的文章列表"""
    # 只查询 status 为 0 (已发布) 的文章
    articles = KnowledgeArticle.query.order_by(KnowledgeArticle.updated_time.desc()).all()
    return jsonify([article.to_dict() for article in articles]), 200


@articles_bp.route('/get/<int:article_id>', methods=['GET'])
def get_article_detail(article_id):
    """获取单篇已发布的文章详情"""
    article = KnowledgeArticle.query.filter_by(id=article_id, status=0).first_or_404()
    return jsonify(article.to_dict()), 200


@articles_bp.route('/create', methods=['POST'])
@admin_required
def create_article():
    """管理员：创建新文章"""
    data = request.get_json()
    # 作者 ID 就是当前登录的管理员
    author_id = g.user.id


    new_article = KnowledgeArticle(
        title=data.get('title'),
        content=data.get('content'),
        author_id=author_id
    )
    db.session.add(new_article)
    db.session.commit()
    return jsonify({'message': '文章创建成功', 'article': new_article.to_dict()}), 201


@articles_bp.route('/revise/<int:article_id>', methods=['PUT'])
@admin_required
def update_article(article_id):
    """管理员：修改文章"""
    article = KnowledgeArticle.query.get_or_404(article_id)
    data = request.get_json()

    article.title = data.get('title', article.title)
    article.content = data.get('content', article.content)

    db.session.commit()
    return jsonify({'message': '文章更新成功', 'article': article.to_dict()}), 200


@articles_bp.route('/delete/<int:article_id>', methods=['DELETE'])
@admin_required
def delete_article(article_id):
    """管理员：逻辑删除文章"""
    article = KnowledgeArticle.query.get_or_404(article_id)
    # 逻辑删除：将 status 设置为 1
    article.status = 1
    db.session.commit()
    return jsonify({'message': '文章已删除'}), 200