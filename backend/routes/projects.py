from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db, Project, ProjectMember, User

projects_bp = Blueprint('projects', __name__)

def current_user():
    return User.query.get(int(get_jwt_identity()))

def is_project_admin(project, user):
    if user.role == 'admin':
        return True
    m = ProjectMember.query.filter_by(project_id=project.id, user_id=user.id).first()
    return m and m.role == 'admin'

def get_user_project(project_id, user):
    project = Project.query.get_or_404(project_id)
    if user.role == 'admin' or project.owner_id == user.id:
        return project
    m = ProjectMember.query.filter_by(project_id=project_id, user_id=user.id).first()
    if not m:
        return None
    return project


@projects_bp.route('', methods=['GET'])
@jwt_required()
def list_projects():
    user = current_user()
    if user.role == 'admin':
        projects = Project.query.all()
    else:
        memberships = ProjectMember.query.filter_by(user_id=user.id).all()
        pids = [m.project_id for m in memberships]
        owned = Project.query.filter_by(owner_id=user.id).all()
        owned_ids = [p.id for p in owned]
        all_ids = list(set(pids + owned_ids))
        projects = Project.query.filter(Project.id.in_(all_ids)).all()
    return jsonify([p.to_dict() for p in projects]), 200


@projects_bp.route('', methods=['POST'])
@jwt_required()
def create_project():
    user = current_user()
    data = request.get_json()
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'Project name is required'}), 400

    project = Project(
        name=name,
        description=data.get('description', ''),
        owner_id=user.id,
        status=data.get('status', 'active')
    )
    db.session.add(project)
    db.session.flush()

    member = ProjectMember(project_id=project.id, user_id=user.id, role='admin')
    db.session.add(member)
    db.session.commit()
    return jsonify(project.to_dict(include_members=True)), 201


@projects_bp.route('/<int:pid>', methods=['GET'])
@jwt_required()
def get_project(pid):
    user = current_user()
    project = get_user_project(pid, user)
    if not project:
        return jsonify({'error': 'Access denied'}), 403
    return jsonify(project.to_dict(include_members=True)), 200


@projects_bp.route('/<int:pid>', methods=['PUT'])
@jwt_required()
def update_project(pid):
    user = current_user()
    project = get_user_project(pid, user)
    if not project:
        return jsonify({'error': 'Access denied'}), 403
    if not is_project_admin(project, user):
        return jsonify({'error': 'Only project admins can update'}), 403

    data = request.get_json()
    if 'name' in data and data['name'].strip():
        project.name = data['name'].strip()
    if 'description' in data:
        project.description = data['description']
    if 'status' in data and data['status'] in ('active', 'completed', 'archived'):
        project.status = data['status']
    db.session.commit()
    return jsonify(project.to_dict(include_members=True)), 200


@projects_bp.route('/<int:pid>', methods=['DELETE'])
@jwt_required()
def delete_project(pid):
    user = current_user()
    project = Project.query.get_or_404(pid)
    if user.role != 'admin' and project.owner_id != user.id:
        return jsonify({'error': 'Only owner or admin can delete'}), 403
    db.session.delete(project)
    db.session.commit()
    return jsonify({'message': 'Project deleted'}), 200


@projects_bp.route('/<int:pid>/members', methods=['POST'])
@jwt_required()
def add_member(pid):
    user = current_user()
    project = get_user_project(pid, user)
    if not project:
        return jsonify({'error': 'Access denied'}), 403
    if not is_project_admin(project, user):
        return jsonify({'error': 'Only project admins can add members'}), 403

    data = request.get_json()
    email = (data.get('email') or '').strip().lower()
    role = data.get('role', 'member')
    if role not in ('admin', 'member'):
        role = 'member'

    target = User.query.filter_by(email=email).first()
    if not target:
        return jsonify({'error': 'User not found'}), 404

    existing = ProjectMember.query.filter_by(project_id=pid, user_id=target.id).first()
    if existing:
        return jsonify({'error': 'User is already a member'}), 409

    m = ProjectMember(project_id=pid, user_id=target.id, role=role)
    db.session.add(m)
    db.session.commit()
    return jsonify(m.to_dict()), 201


@projects_bp.route('/<int:pid>/members/<int:uid>', methods=['DELETE'])
@jwt_required()
def remove_member(pid, uid):
    user = current_user()
    project = get_user_project(pid, user)
    if not project:
        return jsonify({'error': 'Access denied'}), 403
    if not is_project_admin(project, user) and user.id != uid:
        return jsonify({'error': 'Not allowed'}), 403

    m = ProjectMember.query.filter_by(project_id=pid, user_id=uid).first()
    if not m:
        return jsonify({'error': 'Member not found'}), 404
    db.session.delete(m)
    db.session.commit()
    return jsonify({'message': 'Member removed'}), 200