# my_app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from config import Config

# 创建扩展实例，但不与app关联
db = SQLAlchemy()
bcrypt = Bcrypt()

def create_app(config_class=Config):
    """
    应用工厂函数
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 将扩展实例与app关联
    db.init_app(app)
    bcrypt.init_app(app)
    CORS(app) # 为整个应用启用CORS，方便前后端分离调试

    # 导入蓝图
    from .auth.routes import auth_bp
    from .admin.routes import admin_bp
    from .articles.routes import articles_bp
    from .recognition.routes import recognition_bp
    from .history.routes import history_bp
    from .points.routes import points_bp

    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(articles_bp)
    app.register_blueprint(recognition_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(points_bp)

    return app