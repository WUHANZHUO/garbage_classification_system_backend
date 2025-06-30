# my_app/__init__.py
from flask import Flask
from config import Config
# 将 db 和 bcrypt 的导入移到这里，方便其他模块引用
from .models import db, bcrypt

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化 db 和 bcrypt
    db.init_app(app)
    bcrypt.init_app(app)

    # --- 注册蓝图 ---
    from .auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    # 新增：注册管理员和文章蓝图
    from .admin.routes import admin_bp
    app.register_blueprint(admin_bp)

    from .articles.routes import articles_bp
    app.register_blueprint(articles_bp)

    @app.route('/')
    def index():
        return "<h1>垃圾分类系统 API</h1>"

    return app