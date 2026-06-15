from models import usuario_model


def listar():
    return usuario_model.get_todos()


def buscar_por_id(usuario_id):
    usuario = usuario_model.get_por_id(usuario_id)
    if not usuario:
        return None, "Usuário não encontrado"
    return usuario, None


def criar(dados):
    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not nome or not email or not senha:
        return None, "Nome, email e senha são obrigatórios"
    novo_id = usuario_model.criar(nome, email, senha)
    return {"id": novo_id}, None


def login(dados):
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not email or not senha:
        return None, "Email e senha são obrigatórios"
    usuario = usuario_model.autenticar(email, senha)
    if not usuario:
        return None, "Email ou senha inválidos"
    return usuario, None
