import logging
from flask import jsonify

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"erro": str(e), "sucesso": False}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"erro": "Não autorizado", "sucesso": False}), 401

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        logger.exception("Erro não tratado: %s", e)
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
