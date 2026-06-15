from database import db
from models.task import Task
from models.user import User
from models.category import Category
from datetime import datetime
from config.settings import VALID_TASK_STATUSES, TASK_PRIORITY_MIN, TASK_PRIORITY_MAX
import logging

logger = logging.getLogger(__name__)


def _enrich_with_overdue(task_dict, task):
    task_dict['overdue'] = task.is_overdue()
    return task_dict


def get_all():
    tasks = Task.query.all()
    result = []
    for t in tasks:
        data = t.to_dict()
        if t.user_id:
            user = db.session.get(User, t.user_id)
            data['user_name'] = user.name if user else None
        else:
            data['user_name'] = None
        if t.category_id:
            cat = db.session.get(Category, t.category_id)
            data['category_name'] = cat.name if cat else None
        else:
            data['category_name'] = None
        result.append(_enrich_with_overdue(data, t))
    return result


def get_by_id(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return None, "Task não encontrada"
    data = task.to_dict()
    return _enrich_with_overdue(data, task), None


def create(data):
    title = data.get('title')
    if not title:
        return None, "Título é obrigatório"
    if len(title) < 3:
        return None, "Título muito curto"
    if len(title) > 200:
        return None, "Título muito longo"

    status = data.get('status', 'pending')
    if status not in VALID_TASK_STATUSES:
        return None, "Status inválido"

    priority = data.get('priority', 3)
    if not (TASK_PRIORITY_MIN <= priority <= TASK_PRIORITY_MAX):
        return None, f"Prioridade deve ser entre {TASK_PRIORITY_MIN} e {TASK_PRIORITY_MAX}"

    user_id = data.get('user_id')
    if user_id and not db.session.get(User, user_id):
        return None, "Usuário não encontrado"

    category_id = data.get('category_id')
    if category_id and not db.session.get(Category, category_id):
        return None, "Categoria não encontrada"

    task = Task()
    task.title = title
    task.description = data.get('description', '')
    task.status = status
    task.priority = priority
    task.user_id = user_id
    task.category_id = category_id

    due_date_str = data.get('due_date')
    if due_date_str:
        try:
            task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
        except ValueError:
            return None, "Formato de data inválido. Use YYYY-MM-DD"

    tags = data.get('tags')
    if tags:
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    try:
        db.session.add(task)
        db.session.commit()
        logger.info("Task criada: %s — %s", task.id, task.title)
        return task.to_dict(), None
    except Exception as e:
        db.session.rollback()
        logger.exception("Erro ao criar task: %s", e)
        return None, "Erro ao criar task"


def update(task_id, data):
    task = db.session.get(Task, task_id)
    if not task:
        return None, "Task não encontrada"

    if 'title' in data:
        t = data['title']
        if len(t) < 3:
            return None, "Título muito curto"
        if len(t) > 200:
            return None, "Título muito longo"
        task.title = t

    if 'description' in data:
        task.description = data['description']

    if 'status' in data:
        if data['status'] not in VALID_TASK_STATUSES:
            return None, "Status inválido"
        task.status = data['status']

    if 'priority' in data:
        p = data['priority']
        if not (TASK_PRIORITY_MIN <= p <= TASK_PRIORITY_MAX):
            return None, f"Prioridade deve ser entre {TASK_PRIORITY_MIN} e {TASK_PRIORITY_MAX}"
        task.priority = p

    if 'user_id' in data:
        if data['user_id'] and not db.session.get(User, data['user_id']):
            return None, "Usuário não encontrado"
        task.user_id = data['user_id']

    if 'category_id' in data:
        if data['category_id'] and not db.session.get(Category, data['category_id']):
            return None, "Categoria não encontrada"
        task.category_id = data['category_id']

    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
            except ValueError:
                return None, "Formato de data inválido"
        else:
            task.due_date = None

    if 'tags' in data:
        tags = data['tags']
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    task.updated_at = datetime.utcnow()

    try:
        db.session.commit()
        logger.info("Task atualizada: %s", task.id)
        return task.to_dict(), None
    except Exception as e:
        db.session.rollback()
        logger.exception("Erro ao atualizar task: %s", e)
        return None, "Erro ao atualizar"


def delete(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return None, "Task não encontrada"
    try:
        db.session.delete(task)
        db.session.commit()
        logger.info("Task deletada: %s", task_id)
        return {"message": "Task deletada com sucesso"}, None
    except Exception as e:
        db.session.rollback()
        logger.exception("Erro ao deletar task: %s", e)
        return None, "Erro ao deletar"


def search(query_str, status, priority, user_id):
    q = Task.query
    if query_str:
        q = q.filter(
            db.or_(Task.title.like(f'%{query_str}%'), Task.description.like(f'%{query_str}%'))
        )
    if status:
        q = q.filter(Task.status == status)
    if priority:
        q = q.filter(Task.priority == int(priority))
    if user_id:
        q = q.filter(Task.user_id == int(user_id))
    return [t.to_dict() for t in q.all()]


def stats():
    total = Task.query.count()
    pending = Task.query.filter_by(status='pending').count()
    in_progress = Task.query.filter_by(status='in_progress').count()
    done = Task.query.filter_by(status='done').count()
    cancelled = Task.query.filter_by(status='cancelled').count()
    overdue_count = sum(1 for t in Task.query.all() if t.is_overdue())
    return {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'done': done,
        'cancelled': cancelled,
        'overdue': overdue_count,
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
    }
