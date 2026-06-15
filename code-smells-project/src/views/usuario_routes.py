from flask import Blueprint, request, jsonify
from controllers import usuario_controller

bp = Blueprint("usuarios", __name__)


@bp.route("/usuarios", methods=["GET"])
def listar():
    return jsonify({"dados": usuario_controller.listar(), "sucesso": True}), 200


@bp.route("/usuarios/<int:usuario_id>", methods=["GET"])
def buscar(usuario_id):
    dado, err = usuario_controller.buscar_por_id(usuario_id)
    if err:
        return jsonify({"erro": err, "sucesso": False}), 404
    return jsonify({"dados": dado, "sucesso": True}), 200


@bp.route("/usuarios", methods=["POST"])
def criar():
    dados = request.get_json() or {}
    resultado, err = usuario_controller.criar(dados)
    if err:
        return jsonify({"erro": err, "sucesso": False}), 400
    return jsonify({"dados": resultado, "sucesso": True}), 201


@bp.route("/login", methods=["POST"])
def login():
    dados = request.get_json() or {}
    usuario, err = usuario_controller.login(dados)
    if err:
        return jsonify({"erro": err, "sucesso": False}), 401
    return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
