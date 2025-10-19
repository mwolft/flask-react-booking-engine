from flask import Blueprint, jsonify

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/ping', methods=['GET'])
def ping_user():
    return jsonify({"message": "User routes working ✅"}), 200
