from flask import jsonify
from .auth.urls import auth_blueprint


@auth_blueprint.app_errorhandler(404)
def page_not_found(e):
    return jsonify(dict(message="Page not found")), 404
