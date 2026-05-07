from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from database import db, Task, Project, ProjectMember, User

dashboard_bp = Blueprint('dashboard', __name__)

def current_user():
    return User.query.get(int(get_jwt_identity()))

@dashboard_bp.route('', methods=['GET'])
@jwt_required()
def dashboard():
    user = current_user()

    if user.role == 'admin':
        all_tasks = Task.query.all()
        all_projects = Project.query.all()
    else:
        memberships = ProjectMember.query.filter_by(user_id=user.id).all()
        pids = [m.project_id for m in memberships]
        owned_pids = [p.id for p in Project.query.filter_by(owner_id=user.id).all()]
        all_pids = list(set(pids + owned_pids))
        all_tasks = Task.query.filter(Task.project_id.in_(all_pids)).all()
        all_projects = Project.query.filter(Project.id.in_(all_pids)).all()

    now = datetime.utcnow()

    stats = {
        'total_tasks': len(all_tasks),
        'todo': sum(1 for t in all_tasks if t.status == 'todo'),
        'in_progress': sum(1 for t in all_tasks if t.status == 'in_progress'),
        'review': sum(1 for t in all_tasks if t.status == 'review'),
        'done': sum(1 for t in all_tasks if t.status == 'done'),
        'overdue': sum(1 for t in all_tasks if t.due_date and t.due_date < now and t.status != 'done'),
        'total_projects': len(all_projects),
        'active_projects': sum(1 for p in all_projects if p.status == 'active'),
        'my_tasks': sum(1 for t in all_tasks if t.assignee_id == user.id),
    }

    recent_tasks = sorted(all_tasks, key=lambda t: t.created_at, reverse=True)[:5]
    overdue_tasks = [t for t in all_tasks if t.due_date and t.due_date < now and t.status != 'done']
    overdue_tasks.sort(key=lambda t: t.due_date)

    return jsonify({
        'stats': stats,
        'recent_tasks': [t.to_dict() for t in recent_tasks],
        'overdue_tasks': [t.to_dict() for t in overdue_tasks[:5]],
        'projects': [p.to_dict() for p in all_projects[:6]],
    }), 200