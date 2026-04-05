from flask import Blueprint


bp = Blueprint("content", __name__, url_prefix="/content")


from app.content import routes  # noqa: E402,F401
