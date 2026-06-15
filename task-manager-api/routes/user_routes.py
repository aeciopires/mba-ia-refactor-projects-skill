from flask import Blueprint, request, jsonify
from controllers import user_controller

user_bp = Blueprint('users', __name__)


@user_bp.route('/users', methods=['GET'])
def get_users():
    return jsonify(user_controller.get_all()), 200


@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    data, err = user_controller.get_by_id(user_id)
    if err:
        return jsonify({'error': err}), 404
    return jsonify(data), 200


@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    result, err = user_controller.create(data)
    if err:
        status = 409 if 'cadastrado' in err else 400
        return jsonify({'error': err}), status
    return jsonify(result), 201


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json() or {}
    result, err = user_controller.update(user_id, data)
    if err:
        status = 404 if 'encontrado' in err else (409 if 'cadastrado' in err else 400)
        return jsonify({'error': err}), status
    return jsonify(result), 200


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    result, err = user_controller.delete(user_id)
    if err:
        return jsonify({'error': err}), 404
    return jsonify(result), 200


@user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    result, err = user_controller.get_tasks(user_id)
    if err:
        return jsonify({'error': err}), 404
    return jsonify(result), 200


@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    result, err = user_controller.login(data)
    if err:
        return jsonify({'error': err}), 401
    return jsonify({'message': 'Login realizado com sucesso', **result}), 200
