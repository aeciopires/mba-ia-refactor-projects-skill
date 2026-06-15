from flask import Blueprint, request, jsonify
from controllers import produto_controller

bp = Blueprint("produtos", __name__)


@bp.route("/produtos", methods=["GET"])
def listar():
    return jsonify({"dados": produto_controller.listar(), "sucesso": True}), 200


@bp.route("/produtos/busca", methods=["GET"])
def buscar():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria")
    preco_min = request.args.get("preco_min", type=float)
    preco_max = request.args.get("preco_max", type=float)
    resultados = produto_controller.buscar(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200


@bp.route("/produtos/<int:produto_id>", methods=["GET"])
def buscar_por_id(produto_id):
    dado, err = produto_controller.buscar_por_id(produto_id)
    if err:
        return jsonify({"erro": err, "sucesso": False}), 404
    return jsonify({"dados": dado, "sucesso": True}), 200


@bp.route("/produtos", methods=["POST"])
def criar():
    dados = request.get_json() or {}
    resultado, err = produto_controller.criar(dados)
    if err:
        return jsonify({"erro": err, "sucesso": False}), 400
    return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Produto criado"}), 201


@bp.route("/produtos/<int:produto_id>", methods=["PUT"])
def atualizar(produto_id):
    dados = request.get_json() or {}
    resultado, err = produto_controller.atualizar(produto_id, dados)
    if err:
        status = 404 if "encontrado" in err else 400
        return jsonify({"erro": err, "sucesso": False}), status
    return jsonify({"dados": resultado, "sucesso": True}), 200


@bp.route("/produtos/<int:produto_id>", methods=["DELETE"])
def deletar(produto_id):
    resultado, err = produto_controller.deletar(produto_id)
    if err:
        return jsonify({"erro": err, "sucesso": False}), 404
    return jsonify({"dados": resultado, "sucesso": True}), 200
