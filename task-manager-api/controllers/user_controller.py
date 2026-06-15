import re
import logging
from database import db
from models.user import User
from models.task import Task

logger = logging.getLogger(__name__)
EMAIL_RE = re.compile(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$')


def get_all():
    users = User.query.all()
    result = []
    for u in users:
        data = u.to_dict()
        data['task_count'] = len(u.tasks)
        result.append(data)
    return result


def get_by_id(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return None, "Usuário não encontrado"
    data = user.to_dict()
    data['tasks'] = [t.to_dict() for t in Task.query.filter_by(user_id=user_id).all()]
    return data, None


def create(data):
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')
    if not name:
        return None, "Nome é obrigatório"
    if not email:
        return None, "Email é obrigatório"
    if not password:
        return None, "Senha é obrigatória"
    if not EMAIL_RE.match(email):
        return None, "Email inválido"
    if len(password) < 4:
        return None, "Senha deve ter no mínimo 4 caracteres"
    if User.query.filter_by(email=email).first():
        return None, "Email já cadastrado"
    if role not in ['user', 'admin', 'manager']:
        return None, "Role inválido"
    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role
    try:
        db.session.add(user)
        db.session.commit()
        logger.info("Usuário criado: %s — %s", user.id, user.name)
        return user.to_dict(), None
    except Exception as e:
        db.session.rollback()
        logger.exception("Erro ao criar usuário: %s", e)
        return None, "Erro ao criar usuário"


def update(user_id, data):
    user = db.session.get(User, user_id)
    if not user:
        return None, "Usuário não encontrado"
    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        if not EMAIL_RE.match(data['email']):
            return None, "Email inválido"
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            return None, "Email já cadastrado"
        user.email = data['email']
    if 'password' in data:
        if len(data['password']) < 4:
            return None, "Senha muito curta"
        user.set_password(data['password'])
    if 'role' in data:
        if data['role'] not in ['user', 'admin', 'manager']:
            return None, "Role inválido"
        user.role = data['role']
    if 'active' in data:
        user.active = data['active']
    try:
        db.session.commit()
        return user.to_dict(), None
    except Exception as e:
        db.session.rollback()
        logger.exception("Erro ao atualizar usuário: %s", e)
        return None, "Erro ao atualizar"


def delete(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return None, "Usuário não encontrado"
    try:
        for t in Task.query.filter_by(user_id=user_id).all():
            db.session.delete(t)
        db.session.delete(user)
        db.session.commit()
        logger.info("Usuário deletado: %s", user_id)
        return {"message": "Usuário deletado com sucesso"}, None
    except Exception as e:
        db.session.rollback()
        logger.exception("Erro ao deletar usuário: %s", e)
        return None, "Erro ao deletar"


def get_tasks(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return None, "Usuário não encontrado"
    tasks = Task.query.filter_by(user_id=user_id).all()
    result = []
    for t in tasks:
        data = t.to_dict()
        data['overdue'] = t.is_overdue()
        result.append(data)
    return result, None


def login(data):
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return None, "Email e senha são obrigatórios"
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return None, "Credenciais inválidas"
    if not user.active:
        return None, "Usuário inativo"
    return {'user': user.to_dict()}, None
