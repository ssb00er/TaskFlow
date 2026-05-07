from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from database import db, Task, Project, ProjectMember, User

tasks_bp = Blueprint('tasks', __name__)

def current_user():
    return User.query.get(int(get_jwt_identity()))

def can_access_project(pid, user):
    project = Project.query.get(pid)
    if not project:
        return None
    if user.role == 'admin' or project.owner_id == user.id:
        return project
    m = ProjectMember.query.filter_by(project_id=pid, user_id=user.id).first()
    return project if m else None

def is_project_admin(project, user):
    if user.role == 'admin' or project.owner_id == user.id:
        return True
    m = ProjectMember.query.filter_by(project_id=project.id, user_id=user.id).first()
    return m and m.role == 'admin'


@tasks_bp.route('', methods=['GET'])
@jwt_required()
def list_tasks():
    user = current_user()
    project_id = request.args.get('project_id', type=int)
    status = request.args.get('status')
    assignee_id = request.args.get('assignee_id', type=int)
    priority = request.args.get('priority')

    query = Task.query

    if project_id:
        p = can_access_project(project_id, user)
        if not p:
            return jsonify({'error': 'Access denied'}), 403
        query = query.filter_by(project_id=project_id)
    elif user.role != 'admin':
        memberships = ProjectMember.query.filter_by(user_id=user.id).all()
        pids = [m.project_id for m in memberships]
        owned_pids = [p.id for p in Project.query.filter_by(owner_id=user.id).all()]
        all_pids = list(set(pids + owned_pids))
        query = query.filter(Task.project_id.in_(all_pids))

    if status:
        query = query.filter_by(status=status)
    if assignee_id:
        query = query.filter_by(assignee_id=assignee_id)
    if priority:
        query = query.filter_by(priority=priority)

    tasks = query.order_by(Task.created_at.desc()).all()
    return jsonify([t.to_dict() for t in tasks]), 200


@tasks_bp.route('', methods=['POST'])
@jwt_required()
def create_task():
    user = current_user()
    data = request.get_json()
    title = (data.get('title') or '').strip()
    project_id = data.get('project_id')

    if not title:
        return jsonify({'error': 'Task title is required'}), 400
    if not project_id:
        return jsonify({'error': 'project_id is required'}), 400

    project = can_access_project(project_id, user)
    if not project:
        return jsonify({'error': 'Access denied'}), 403

    due_date = None
    if data.get('due_date'):
        try:
            due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        except Exception:
            return jsonify({'error': 'Invalid due_date format'}), 400

    priority = data.get('priority', 'medium')
    if priority not in ('low', 'medium', 'high', 'urgent'):
        priority = 'medium'

    status = data.get('status', 'todo')
    if status not in ('todo', 'in_progress', 'review', 'done'):
        status = 'todo'

    task = Task(
        title=title,
        description=data.get('description', ''),
        project_id=project_id,
        creator_id=user.id,
        assignee_id=data.get('assignee_id'),
        status=status,
        priority=priority,
        due_date=due_date,
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@tasks_bp.route('/<int:tid>', methods=['GET'])
@jwt_required()
def get_task(tid):
    user = current_user()
    task = Task.query.get_or_404(tid)
    if not can_access_project(task.project_id, user):
        return jsonify({'error': 'Access denied'}), 403
    return jsonify(task.to_dict()), 200


@tasks_bp.route('/<int:tid>', methods=['PUT'])
@jwt_required()
def update_task(tid):
    user = current_user()
    task = Task.query.get_or_404(tid)
    project = can_access_project(task.project_id, user)
    if not project:
        return jsonify({'error': 'Access denied'}), 403

    data = request.get_json()
    can_edit_all = is_project_admin(project, user) or task.creator_id == user.id

    if 'status' in data:
        s = data['status']
        if s in ('todo', 'in_progress', 'review', 'done'):
            task.status = s

    if can_edit_all:
        if 'title' in data and data['title'].strip():
            task.title = data['title'].strip()
        if 'description' in data:
            task.description = data['description']
        if 'priority' in data and data['priority'] in ('low', 'medium', 'high', 'urgent'):
            task.priority = data['priority']
        if 'assignee_id' in data:
            task.assignee_id = data['assignee_id']
        if 'due_date' in data:
            if data['due_date']:
                try:
                    task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
                except Exception:
                    return jsonify({'error': 'Invalid due_date format'}), 400
            else:
                task.due_date = None

    task.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(task.to_dict()), 200


@tasks_bp.route('/<int:tid>', methods=['DELETE'])
@jwt_required()
def delete_task(tid):
    user = current_user()
    task = Task.query.get_or_404(tid)
    project = can_access_project(task.project_id, user)
    if not project:
        return jsonify({'error': 'Access denied'}), 403
    if not is_project_admin(project, user) and task.creator_id != user.id:
        return jsonify({'error': 'Not allowed'}), 403

    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted'}), 200