from collections import OrderedDict

from flask import jsonify, make_response
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from webargs.flaskparser import use_args

from .utils import shoppinglist_args, shoppinglist_update_args
from ..core.loggers import AppLogger
from ..messages import \
    (server_error, shoppinglist_created, shoppinglist_not_found,
     shoppinglist_name_exists, shoppinglist_updated, valid_integer_required)
from ..models import User, ShoppingList


class CreateShoppingListApi(Resource):
    """
    Resource to create user shopping list.
    """

    @use_args(shoppinglist_args)
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
                        message=shoppinglist_created,
                        data=dict(
                            id=shl.id,
                            name=shl.name,
                            created_on=shl.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                        )
                    )), 201
                )

        except Exception as e:
            AppLogger(self.__class__.__name__).logger.warning(e)
            return make_response(
                jsonify(
                    dict(
                        status='fail',
                        message='server error, try again'
                    )), 500
            )


class UserShoppingListsApi(Resource):
    """
    Resource to handle fetching of specific user shopping lists.
    """

    @jwt_required
    def get(self):
        """
        Handle GET request and takes user authentication token.
        """

        try:
            current_user = get_jwt_identity()

            user = User.query.filter_by(username=current_user).first()

            # create a list which contains shopping list id and shopping list name/
            user_shopping_list = [{'id': shl.id, 'name': shl.name} for shl in user.shopping_lists.all()]

            return make_response(
                jsonify(dict(
                    status='success',
                    message=dict(
                        shopping_lists=user_shopping_list
                    )
                ))
            )

        except Exception as e:
            AppLogger(self.__class__.__name__).logger.warning(e)
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=server_error
                )), 500
            )


class UserShoppingListDetailApi(Resource):
    """
    Resource to fetch a single shopping list.
    """

    @jwt_required
    def get(self, id):
        try:
            current_user = get_jwt_identity()
            try:
                int(id)

            except ValueError as e:
                AppLogger(self.__class__.__name__).logger.warning(e)
                return make_response(
                    jsonify(dict(
                        status='fail',
                        message=valid_integer_required
                    )), 400
                )

            user = User.query.filter_by(username=current_user).first()

            try:
                shopping_list = user.shopping_lists.filter_by(id=int(id)).first_or_404()

            except Exception as e:
                AppLogger(self.__class__.__name__).logger.warning(e)
                return make_response(
                    jsonify(dict(
                        status='fail',
                        message=shoppinglist_not_found
                    )), 404
                )

            response = OrderedDict(
                [
                    ('status', 'success'),
                    ('message', OrderedDict(
                        [
                            ('id', shopping_list.id),
                            ('owner_id', shopping_list.owner_id),
                            ('name', shopping_list.name),
                            ('created_on', shopping_list.timestamp.strftime("%Y-%m-%d %H:%M:%S")),
                            ('updated_on', shopping_list.updated.strftime("%Y-%m-%d %H:%M:%S"))
                        ]
                    )),
                ]
            )

            return make_response(
                jsonify(response), 200
            )

        except Exception as e:
            AppLogger(self.__class__.__name__).logger.warning(e)
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=server_error
                )), 500
            )

    @use_args(shoppinglist_update_args)
    @jwt_required
    def put(self, args, id):
        try:
            current_user = get_jwt_identity()
            try:
                # make sure provided id can be converted to an integer.
                int(id)

            except ValueError as e:
                AppLogger(self.__class__.__name__).logger.warning(e)
                return make_response(
                    jsonify(dict(
                        status='fail',
                        message=valid_integer_required
                    )), 400
                )

            # new name provided by client
            new_name = args.get('new_name', None)

            # if name is none there is no need to modify client resource.
            if not new_name:
                return make_response(
                    jsonify(dict(
                        status='success',
                    )), 304
                )

            # check if shopping list with the same name exists.
            shl = ShoppingList.query.filter_by(name=new_name).first()

            if shl:
                return make_response(
                    jsonify(dict(
                        status='fail',
                        message=shoppinglist_name_exists
                    ))
                )

            # get user instance
            user = User.query.filter_by(username=current_user).first()

            try:
                # now update the resource.
                shopping_list = user.shopping_lists.filter_by(id=int(id)).first_or_404()
                shopping_list.name = new_name
                shopping_list.save()

                return make_response(
                    jsonify(dict(
                        status='success',
                        message=shoppinglist_updated,
                        data=dict(
                            name=shopping_list.name,
                            created_on=shopping_list.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                            updated_on=shopping_list.updated.strftime("%Y-%m-%d %H:%M:%S")
                        )
                    )), 200
                )

            except Exception as e:
                AppLogger(self.__class__.__name__).logger.warning(e)
                return make_response(
                    jsonify(dict(
                        status='fail',
                        message=shoppinglist_not_found
                    )), 404
                )

        except Exception as e:
            AppLogger(self.__class__.__name__).logger.warning(e)
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=server_error
                )), 500
            )