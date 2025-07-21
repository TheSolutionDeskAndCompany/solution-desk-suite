from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_flatpages import FlatPages
from flask_login import LoginManager

# Initialize Flask extensions
db = SQLAlchemy()
migrate = Migrate()
pages = FlatPages()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))
