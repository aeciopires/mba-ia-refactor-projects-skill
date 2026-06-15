from flask import Blueprint, request, jsonify
from controllers import task_controller

task_bp = Blueprint('tasks', __name__)


@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(task_controller.get_all()), 200


@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    data, err = task_controller.get_by_id(task_id)
    if err:
        return jsonify({'error': err}), 404
    return jsonify(data), 200


@task_bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json() or {}
    result, err = task_controller.create(data)
    if err:
        return jsonify({'error': err}), 400
    return jsonify(result), 201


@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json() or {}
    result, err = task_controller.update(task_id, data)
    if err:
        status = 404 if 'encontrada' in err else 400
        return jsonify({'error': err}), status
    return jsonify(result), 200


@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    result, err = task_controller.delete(task_id)
    if err:
        return jsonify({'error': err}), 404
    return jsonify(result), 200


@task_bp.route('/tasks/search', methods=['GET'])
def search_tasks():
    results = task_controller.search(
        request.args.get('q', ''),
        request.args.get('status', ''),
        request.args.get('priority', ''),
        request.args.get('user_id', ''),
    )
    return jsonify(results), 200


@task_bp.route('/tasks/stats', methods=['GET'])
def task_stats():
    return jsonify(task_controller.stats()), 200
