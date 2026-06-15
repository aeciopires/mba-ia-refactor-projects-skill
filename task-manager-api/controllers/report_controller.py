from database import db
from models.task import Task
from models.user import User
from models.category import Category
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def summary():
    total_tasks = Task.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()

    pending = Task.query.filter_by(status='pending').count()
    in_progress = Task.query.filter_by(status='in_progress').count()
    done = Task.query.filter_by(status='done').count()
    cancelled = Task.query.filter_by(status='cancelled').count()

    priority_counts = {
        'critical': Task.query.filter_by(priority=1).count(),
        'high':     Task.query.filter_by(priority=2).count(),
        'medium':   Task.query.filter_by(priority=3).count(),
        'low':      Task.query.filter_by(priority=4).count(),
        'minimal':  Task.query.filter_by(priority=5).count(),
    }

    overdue_list = [
        {
            'id': t.id,
            'title': t.title,
            'due_date': str(t.due_date),
            'days_overdue': (datetime.utcnow() - t.due_date).days,
        }
        for t in Task.query.all() if t.is_overdue()
    ]

    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
    recent_done = Task.query.filter(
        Task.status == 'done', Task.updated_at >= seven_days_ago
    ).count()

    user_stats = []
    for u in User.query.all():
        user_tasks = Task.query.filter_by(user_id=u.id).all()
        total = len(user_tasks)
        completed = sum(1 for t in user_tasks if t.status == 'done')
        user_stats.append({
            'user_id': u.id,
            'user_name': u.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': round((completed / total) * 100, 2) if total > 0 else 0,
        })

    return {
        'generated_at': str(datetime.utcnow()),
        'overview': {
            'total_tasks': total_tasks,
            'total_users': total_users,
            'total_categories': total_categories,
        },
        'tasks_by_status': {
            'pending': pending,
            'in_progress': in_progress,
            'done': done,
            'cancelled': cancelled,
        },
        'tasks_by_priority': priority_counts,
        'overdue': {'count': len(overdue_list), 'tasks': overdue_list},
        'recent_activity': {
            'tasks_created_last_7_days': recent_tasks,
            'tasks_completed_last_7_days': recent_done,
        },
        'user_productivity': user_stats,
    }


def user_report(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return None, "Usuário não encontrado"
    tasks = Task.query.filter_by(user_id=user_id).all()
    total = len(tasks)
    by_status = {'done': 0, 'pending': 0, 'in_progress': 0, 'cancelled': 0}
    overdue = 0
    high_priority = 0
    for t in tasks:
        if t.status in by_status:
            by_status[t.status] += 1
        if t.priority <= 2:
            high_priority += 1
        if t.is_overdue():
            overdue += 1
    return {
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
        'statistics': {
            'total_tasks': total,
            **by_status,
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': round((by_status['done'] / total) * 100, 2) if total > 0 else 0,
        },
    }, None
