from flask import jsonify, make_response
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from webargs.flaskparser import use_args

from .utils import shopping_list_args
from ..messages import shopping_list_created
from ..models import User, ShoppingList


class CreateShoppingListApi(Resource):
    """
    Resource to create user shopping list.
    """

    @use_args(shopping_list_args)
    @jwt_required
    def post(self, data):
        """
        Method to handle POST request.
        """

        try:
            current_user = get_jwt_identity()
            if current_user:
                user = User.query.filter_by(username=current_user).first()
                shl_name = data.get('name')
                ShoppingList(name=shl_name, owner_id=user.id).save()
                shl = ShoppingList.query.filter_by(name=shl_name).first()

                return make_response(
                    jsonify(dict(
                        status='success',
                        message=shopping_list_created,
                        data=dict(
                            name=shl.name,
                            created_on=shl.timestamp.strftime("%Y-%m-%d")
                        )
                    )), 201
                )

        except Exception as e:
            return make_response(
                jsonify(
                    dict(
                        status='fail',
                        message='server error, try again'
                    )), 500
            )
