from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
# 初始化 SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_key'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy()
migrate = Migrate()

bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # 加載配置
    app.config.from_object('config.Config')
    
    # 設定 SQLAlchemy 資料庫路徑
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 初始化套件
    db.init_app(app)
    migrate.init_app(app, db)
    with app.app_context():
        db.create_all()  # 確保資料庫和表格已經創建
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'  # 指定未登入時重定向的登入頁面
    # 設置藍圖路由
    from .routes import main
    app.register_blueprint(main)

    return app