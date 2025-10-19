from flask import Blueprint
from .hotel_routes import hotel_bp
from .user_routes import user_bp

api = Blueprint('api', __name__)

# Registro de subrutas
api.register_blueprint(hotel_bp, url_prefix='/hotel')
api.register_blueprint(user_bp, url_prefix='/user')
