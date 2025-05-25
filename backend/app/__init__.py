from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)  # 启用CORS支持跨域请求
    
    # 导入并注册蓝图
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app 