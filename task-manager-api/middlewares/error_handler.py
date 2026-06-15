import logging
from flask import jsonify

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Recurso não encontrado'}), 404

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        logger.exception("Erro não tratado: %s", e)
        return jsonify({'error': 'Erro interno do servidor'}), 500
