from config.database import get_db


def _build_pedido(row, itens):
    return {
        "id": row["id"],
        "usuario_id": row["usuario_id"],
        "status": row["status"],
        "total": row["total"],
        "criado_em": row["criado_em"],
        "itens": itens,
    }


def _fetch_itens(db, pedido_id):
    rows = db.execute("""
        SELECT ip.produto_id, ip.quantidade, ip.preco_unitario, pr.nome AS produto_nome
        FROM itens_pedido ip
        JOIN produtos pr ON pr.id = ip.produto_id
        WHERE ip.pedido_id = ?
    """, (pedido_id,)).fetchall()
    return [
        {
            "produto_id": r["produto_id"],
            "produto_nome": r["produto_nome"],
            "quantidade": r["quantidade"],
            "preco_unitario": r["preco_unitario"],
        }
        for r in rows
    ]


def get_por_usuario(usuario_id):
    db = get_db()
    rows = db.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,)).fetchall()
    return [_build_pedido(r, _fetch_itens(db, r["id"])) for r in rows]


def get_todos():
    db = get_db()
    rows = db.execute("SELECT * FROM pedidos").fetchall()
    return [_build_pedido(r, _fetch_itens(db, r["id"])) for r in rows]


def criar(usuario_id, itens):
    db = get_db()
    produto_ids = [item["produto_id"] for item in itens]
    placeholders = ",".join("?" * len(produto_ids))
    produtos_rows = db.execute(
        f"SELECT id, nome, preco, estoque FROM produtos WHERE id IN ({placeholders})",
        produto_ids,
    ).fetchall()
    produtos_map = {r["id"]: r for r in produtos_rows}

    total = 0.0
    for item in itens:
        produto = produtos_map.get(item["produto_id"])
        if produto is None:
            return {"erro": f"Produto {item['produto_id']} não encontrado"}
        if produto["estoque"] < item["quantidade"]:
            return {"erro": f"Estoque insuficiente para {produto['nome']}"}
        total += produto["preco"] * item["quantidade"]

    cursor = db.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
        (usuario_id, total),
    )
    pedido_id = cursor.lastrowid

    for item in itens:
        produto = produtos_map[item["produto_id"]]
        db.execute(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
            (pedido_id, item["produto_id"], item["quantidade"], produto["preco"]),
        )
        db.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            (item["quantidade"], item["produto_id"]),
        )

    db.commit()
    return {"pedido_id": pedido_id, "total": total}


def atualizar_status(pedido_id, novo_status):
    db = get_db()
    db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
    db.commit()


def relatorio_vendas():
    db = get_db()
    total_pedidos = db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    faturamento = db.execute("SELECT COALESCE(SUM(total), 0) FROM pedidos").fetchone()[0]
    pendentes = db.execute("SELECT COUNT(*) FROM pedidos WHERE status='pendente'").fetchone()[0]
    aprovados = db.execute("SELECT COUNT(*) FROM pedidos WHERE status='aprovado'").fetchone()[0]
    cancelados = db.execute("SELECT COUNT(*) FROM pedidos WHERE status='cancelado'").fetchone()[0]
    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "pedidos_pendentes": pendentes,
        "pedidos_aprovados": aprovados,
        "pedidos_cancelados": cancelados,
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }
