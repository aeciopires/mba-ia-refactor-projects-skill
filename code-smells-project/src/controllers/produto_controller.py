from models import produto_model
from config.settings import VALID_CATEGORIES


def listar():
    return produto_model.get_todos()


def buscar_por_id(produto_id):
    produto = produto_model.get_por_id(produto_id)
    if not produto:
        return None, "Produto não encontrado"
    return produto, None


def buscar(termo, categoria, preco_min, preco_max):
    return produto_model.buscar(termo, categoria, preco_min, preco_max)


def criar(dados):
    nome = dados.get("nome", "")
    if not nome:
        return None, "Nome é obrigatório"
    if len(nome) < 2:
        return None, "Nome muito curto"
    if len(nome) > 200:
        return None, "Nome muito longo"
    if "preco" not in dados:
        return None, "Preço é obrigatório"
    if "estoque" not in dados:
        return None, "Estoque é obrigatório"
    preco = dados["preco"]
    estoque = dados["estoque"]
    if preco < 0:
        return None, "Preço não pode ser negativo"
    if estoque < 0:
        return None, "Estoque não pode ser negativo"
    categoria = dados.get("categoria", "geral")
    if categoria not in VALID_CATEGORIES:
        return None, f"Categoria inválida. Válidas: {VALID_CATEGORIES}"
    descricao = dados.get("descricao", "")
    novo_id = produto_model.criar(nome, descricao, preco, estoque, categoria)
    return {"id": novo_id}, None


def atualizar(produto_id, dados):
    existente, err = buscar_por_id(produto_id)
    if err:
        return None, err
    if not dados:
        return None, "Dados inválidos"
    for campo in ("nome", "preco", "estoque"):
        if campo not in dados:
            return None, f"{campo.capitalize()} é obrigatório"
    preco = dados["preco"]
    estoque = dados["estoque"]
    if preco < 0:
        return None, "Preço não pode ser negativo"
    if estoque < 0:
        return None, "Estoque não pode ser negativo"
    produto_model.atualizar(
        produto_id,
        dados["nome"],
        dados.get("descricao", ""),
        preco,
        estoque,
        dados.get("categoria", "geral"),
    )
    return {"mensagem": "Produto atualizado"}, None


def deletar(produto_id):
    existente, err = buscar_por_id(produto_id)
    if err:
        return None, err
    produto_model.deletar(produto_id)
    return {"mensagem": "Produto deletado"}, None
