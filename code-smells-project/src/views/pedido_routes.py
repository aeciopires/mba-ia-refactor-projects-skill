from flask import Blueprint, request, jsonify
from controllers import pedido_controller

bp = Blueprint("pedidos", __name__)


@bp.route("/pedidos", methods=["POST"])
def criar():
    dados = request.get_json() or {}
    resultado, err = pedido_controller.criar(dados)
    if err:
        return jsonify({"erro": err, "sucesso": False}), 400
    return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado"}), 201


@bp.route("/pedidos", methods=["GET"])
def listar_todos():
    return jsonify({"dados": pedido_controller.listar_todos(), "sucesso": True}), 200


@bp.route("/pedidos/usuario/<int:usuario_id>", methods=["GET"])
def listar_por_usuario(usuario_id):
    return jsonify({"dados": pedido_controller.listar_por_usuario(usuario_id), "sucesso": True}), 200


@bp.route("/pedidos/<int:pedido_id>/status", methods=["PUT"])
def atualizar_status(pedido_id):
    dados = request.get_json() or {}
    resultado, err = pedido_controller.atualizar_status(pedido_id, dados)
    if err:
        return jsonify({"erro": err, "sucesso": False}), 400
    return jsonify({"dados": resultado, "sucesso": True}), 200


@bp.route("/relatorios/vendas", methods=["GET"])
def relatorio_vendas():
    return jsonify({"dados": pedido_controller.relatorio_vendas(), "sucesso": True}), 200
