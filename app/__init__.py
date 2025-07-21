import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from .extensions import db, migrate, pages, login_manager
from .auth.routes import auth_bp
from .main.routes import main_bp
from .shop.routes import shop_bp

def create_app():
    app = Flask(__name__, template_folder='../templates')
    
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Security configuration
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Configuration
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
    app.config['SECRET_KEY'] = app.secret_key
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config['FLATPAGES_ROOT'] = 'content'
    app.config['FLATPAGES_EXTENSION'] = '.md'
    app.config['STRIPE_PUBLISHABLE_KEY'] = os.getenv('STRIPE_PUBLISHABLE_KEY')
    app.config['STRIPE_SECRET_KEY'] = os.getenv('STRIPE_SECRET_KEY')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    pages.init_app(app)
    login_manager.init_app(app)
    # Security headers disabled for development
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(shop_bp)
    
    # Register FlowMatic Blueprint
    from flowmatic import flowmatic_bp
    app.register_blueprint(flowmatic_bp, url_prefix="/flowmatic")
    
    # Register Spotlight Blueprint
    from spotlight import spotlight_bp
    app.register_blueprint(spotlight_bp, url_prefix="/spotlight")
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create sample tools if they don't exist
        from .models import Tool
        if not Tool.query.first():
            sample_tool = Tool()
            sample_tool.slug = 'example-tool'
            sample_tool.name = 'Example Tool'
            sample_tool.price = 1000  # $10.00 in cents
            db.session.add(sample_tool)
            db.session.commit()
            logging.info("Created sample tool")
    
    return app
