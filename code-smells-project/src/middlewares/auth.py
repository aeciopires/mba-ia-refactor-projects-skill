from functools import wraps
from flask import request, jsonify
from config.settings import ADMIN_KEY


def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-Admin-Key", "")
        if key != ADMIN_KEY:
            return jsonify({"erro": "Não autorizado", "sucesso": False}), 401
        return f(*args, **kwargs)
    return decorated
