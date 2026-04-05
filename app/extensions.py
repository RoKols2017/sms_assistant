"""Flask extensions registry."""

from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Войдите в систему, чтобы продолжить."
login_manager.login_message_category = "warning"
bcrypt = Bcrypt()
csrf = CSRFProtect()
