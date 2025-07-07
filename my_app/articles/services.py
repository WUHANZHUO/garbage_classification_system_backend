# my_app/articles/services.py
from ..models import db, KnowledgeArticle, User


def get_published_articles_service():
    """获取所有已发布的文章"""
    return KnowledgeArticle.query.order_by(KnowledgeArticle.updated_time.desc()).all()


def search_articles_by_title_service(title_query):
    """根据标题模糊搜索文章"""
    search_term = f"%{title_query}%"
    return KnowledgeArticle.query.filter(KnowledgeArticle.title.ilike(search_term)).all()


def get_published_article_detail_service(article_id):
    """获取单篇已发布的文章详情"""
    return KnowledgeArticle.query.filter_by(id=article_id, status=0).first_or_404()


def create_article_service(title, content, author_id):
    """创建新文章的业务逻辑"""
    new_article = KnowledgeArticle(
        title=title,
        content=content,
        author_id=author_id
    )
    db.session.add(new_article)
    db.session.commit()
    return new_article


def update_article_service(article_id, data):
    """修改文章的业务逻辑"""
    article = KnowledgeArticle.query.get_or_404(article_id)
    article.title = data.get('title', article.title)
    article.content = data.get('content', article.content)
    db.session.commit()
    return article


def delete_article_service(article_id):
    """逻辑删除文章的业务逻辑"""
    article = KnowledgeArticle.query.get_or_404(article_id)
    article.status = 1  # 逻辑删除
    db.session.commit()
    return article