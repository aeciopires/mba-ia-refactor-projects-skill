import bcrypt
from config.database import get_db


def _row_to_public_dict(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def get_todos():
    db = get_db()
    rows = db.execute("SELECT * FROM usuarios").fetchall()
    return [_row_to_public_dict(r) for r in rows]


def get_por_id(usuario_id):
    db = get_db()
    row = db.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
    return _row_to_public_dict(row) if row else None


def criar(nome, email, senha, tipo="cliente"):
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
    db = get_db()
    cursor = db.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha_hash, tipo),
    )
    db.commit()
    return cursor.lastrowid


def autenticar(email, senha):
    db = get_db()
    row = db.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
    if row and bcrypt.checkpw(senha.encode(), row["senha"].encode()):
        return _row_to_public_dict(row)
    return None
