from models import pedido_model
from config.settings import (
    VALID_ORDER_STATUSES,
    DISCOUNT_THRESHOLD_HIGH, DISCOUNT_RATE_HIGH,
    DISCOUNT_THRESHOLD_MID,  DISCOUNT_RATE_MID,
    DISCOUNT_THRESHOLD_LOW,  DISCOUNT_RATE_LOW,
)


def criar(dados):
    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])
    if not usuario_id:
        return None, "Usuario ID é obrigatório"
    if not itens:
        return None, "Pedido deve ter pelo menos 1 item"
    resultado = pedido_model.criar(usuario_id, itens)
    if "erro" in resultado:
        return None, resultado["erro"]
    return resultado, None


def listar_por_usuario(usuario_id):
    return pedido_model.get_por_usuario(usuario_id)


def listar_todos():
    return pedido_model.get_todos()


def atualizar_status(pedido_id, dados):
    novo_status = dados.get("status", "")
    if novo_status not in VALID_ORDER_STATUSES:
        return None, "Status inválido"
    pedido_model.atualizar_status(pedido_id, novo_status)
    return {"mensagem": "Status atualizado"}, None


def relatorio_vendas():
    dados = pedido_model.relatorio_vendas()
    faturamento = dados["faturamento_bruto"]
    if faturamento > DISCOUNT_THRESHOLD_HIGH:
        desconto = faturamento * DISCOUNT_RATE_HIGH
    elif faturamento > DISCOUNT_THRESHOLD_MID:
        desconto = faturamento * DISCOUNT_RATE_MID
    elif faturamento > DISCOUNT_THRESHOLD_LOW:
        desconto = faturamento * DISCOUNT_RATE_LOW
    else:
        desconto = 0.0
    dados["desconto_aplicavel"] = round(desconto, 2)
    dados["faturamento_liquido"] = round(faturamento - desconto, 2)
    return dados
