# -*- coding: utf-8 -*-

"""
Contains all Resources to manage crud operations of user shopping lists
and shopping items.
"""

from flask import jsonify, make_response, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from webargs import validate
from webargs.flaskparser import use_args

from .utils import \
    (prep_keyword, search_args, shoppinglist_args, shoppinglist_update_args, shoppingitem_create_args,
     shoppingitem_update_args, urlmaker)
from ..conf.settings import MAX_ITEMS_PER_PAGE
from ..core.loggers import AppLogger
from ..messages import \
    (shoppingitem_created, shoppingitem_exists, shoppingitem_not_found, shoppingitem_updated,
     shoppinglist_created, shoppinglist_not_found, shoppinglist_name_exists,
     shoppinglist_updated, invalid_limit, invalid_page, negative_page, negative_limit, search_not_found)
from ..models import User, ShoppingList, ShoppingItem


class ShoppingListsApi(Resource):
    """
    Resource to handle fetching of specific user shopping lists.
    """

    @jwt_required
    def get(self):
        """
        Handle GET request and takes user authentication token.
        """
        response = {}

        has_page = False
        has_limit = False

        page = None
        limit = None

        prev_page_url = None
        next_page_url = None

        def params_error(error):
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=error
                )), 400
            )

        current_user = get_jwt_identity()

        user = User.query.filter_by(username=current_user).first()

        args = request.args

        if 'page' in args:
            has_page = True
            page = args.get('page', 1)

            try:
                page = int(page)

            except ValueError:
                return params_error(invalid_page)

            if page < 0:
                return params_error(negative_page)

        if 'limit' in args:
            limit = args.get('limit')
            has_limit = True

            try:
                limit = int(limit)

            except ValueError:
                return params_error(invalid_limit)

            if limit < 0:
                return params_error(negative_limit)

        if any([has_limit, has_page]):

            if not limit:
                limit = MAX_ITEMS_PER_PAGE

            paginated = user.shopping_lists.paginate(page=page, per_page=limit, error_out=False)

            if paginated.has_prev:
                prev_page_url = urlmaker(request, paginated.prev_num, limit).make_url()

            if paginated.has_next:
                next_page_url = urlmaker(request, paginated.next_num, limit).make_url()

            output = [{
                'id': shl.id,
                'name': shl.name,
                'is_active': shl.is_active} for shl in paginated.items]

            response.setdefault('total_pages', paginated.pages)

            response.setdefault('shopping_lists', output)

            if prev_page_url:
                response.setdefault('previous page', prev_page_url)

            if next_page_url:
                response.setdefault('next page', next_page_url)

        else:
            shoppinglists = user.shopping_lists.all()

            output = [{
                'id': shl.id,
                'name': shl.name,
                'is_active': shl.is_active} for shl in shoppinglists]

            response.setdefault('shopping_lists', output)

        return make_response(
            jsonify(dict(
                status='success',
                message=response
            )), 200
        )

    @use_args(shoppinglist_args)
    @jwt_required
    def post(self, data):
        """
        Method to handle POST request.
        """

        current_user = get_jwt_identity()

        shl_name = data.get('name')

        # check if shopping list exists
        old_shl = ShoppingList.query.filter_by(name=shl_name).first()

        # if shopping list exists return bad request response.
        if old_shl:

            return make_response(
                jsonify(dict(
                    status='fail',
                    message=shoppinglist_name_exists
                )), 400
            )

        # get user instance.
        user = User.query.filter_by(username=current_user).first()

        # save shopping list.
        ShoppingList(name=shl_name, owner_id=user.id).save()

        # get saved shopping list instance and use in response sent to client.
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


class ShoppingListDetailApi(Resource):
    """
    Resource that handles specific user shopping list and accepts
    http methods GET, PUT and DELETE only. This resource also accepts
    an integer id in associated urls.
    """

    @jwt_required
    def get(self, id):
        """
        Handles GET request to fetch specific shopping list requested by client.
        :param id: id of shopping list.
        :return: json data.
        """

        data = {}

        has_page = False
        has_limit = False

        page = None
        limit = None

        prev_page_url = None
        next_page_url = None

        def params_error(error):
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=error
                )), 400
            )

        current_user = get_jwt_identity()

        # get user instance.
        user = User.query.filter_by(username=current_user).first()

        # get shopping list using provided id, if not found raise error 404 and
        # return response to client.
        try:
            shoppinglist = user.shopping_lists.filter_by(id=int(id)).first_or_404()

        except Exception as e:
            AppLogger(self.__class__.__name__).logger.warning(e)
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=shoppinglist_not_found
                )), 404
            )

        args = request.args

        if 'page' in args:
            has_page = True
            page = args.get('page', 1)

            try:
                page = int(page)

            except ValueError:
                return params_error(invalid_page)

            if page < 0:
                return params_error(negative_page)

        if 'limit' in args:
            limit = args.get('limit')
            has_limit = True

            try:
                limit = int(limit)

            except ValueError:
                return params_error(invalid_limit)

            if limit < 0:
                return params_error(negative_limit)

        if any([has_limit, has_page]):

            if not limit:
                limit = MAX_ITEMS_PER_PAGE

            paginated = shoppinglist.shopping_items.paginate(page=page, per_page=limit, error_out=False)

            if paginated.has_prev:
                prev_page_url = urlmaker(request, paginated.prev_num, limit).make_url()

            if paginated.has_next:
                next_page_url = urlmaker(request, paginated.next_num, limit).make_url()

            output = [{'name': item.name} for item in paginated.items]

            data.setdefault('total pages', paginated.pages)

            data.setdefault('shopping items', output)

            if prev_page_url:
                data.setdefault('previous page', prev_page_url)

            if next_page_url:
                data.setdefault('next page', next_page_url)

        else:
            items = [item.name for item in shoppinglist.shopping_items.all()]
            data.setdefault('shopping items', items)

        data.setdefault('id', shoppinglist.id)
        data.setdefault('name', shoppinglist.name)
        data.setdefault('created_on', shoppinglist.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        data.setdefault('updated_on', shoppinglist.updated.strftime("%Y-%m-%d %H:%M:%S"))
        return make_response(
            jsonify(dict(
                status='success',
                message=data
            )), 200
        )

    @use_args(shoppinglist_update_args)
    @jwt_required
    def put(self, args, id):
        """
        Handles PUT request to update user shopping list.
        :param args: new name to be updated.
        :param id: shopping list id
        :return: response
        """
        current_user = get_jwt_identity()

        # get user instance
        user = User.query.filter_by(username=current_user).first()

        # new name provided by client
        new_name = args.get('new_name', None)
        is_active = args.get('is_active', None)

        # if name is none there is no need to modify client resource.
        if not new_name and is_active is None:
            return make_response(
                jsonify(dict(
                    status='success',
                )), 304
            )

        # check if shopping list exists, if not, return 404 response to client.
        shopping_list = user.shopping_lists.filter_by(id=int(id)).first()

        if not shopping_list:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=shoppinglist_not_found
                )), 404
            )

        def response():
            return make_response(
                jsonify(dict(
                    status='success',
                    message=shoppinglist_updated,
                    data=dict(
                        name=shopping_list.name,
                        is_active=shopping_list.is_active,
                        created_on=shopping_list.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        updated_on=shopping_list.updated.strftime("%Y-%m-%d %H:%M:%S")
                    )
                )), 200
            )

        # client may just want to update shoppinglist active status but
        # not the name therefore we only make changes to what is required and return
        # the response.
        if is_active and not new_name:
            shopping_list.is_active = True
            shopping_list.save()
            return response()

        elif not is_active and not new_name:
            shopping_list.is_active = False
            shopping_list.save()
            return response()

        # check if shopping list with the same name exists.
        shl = ShoppingList.query.filter_by(name=new_name).first()

        # if shopping list exists and it is not owned by the client return bad request.
        if shl and shl.owner_id is not user.id:
            msg = shoppinglist_name_exists
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=msg
                )), 400
            )

        # make changes and save
        shopping_list.name = new_name
        shopping_list.save()

        return response()

    @jwt_required
    def delete(self, id):
        """
        Handles DELETE request to delete shopping list using its id.
        :param id: shopping list id
        :return: response
        """

        current_user = get_jwt_identity()

        # get user instance.
        user = User.query.filter_by(username=current_user).first()

        # delete shopping list from database block.
        try:
            instance = user.shopping_lists.filter_by(id=int(id)).first_or_404()
            instance.delete()
            return make_response(
                jsonify(dict(
                    status="success"
                )), 204
            )

        except Exception as e:
            AppLogger(self.__class__.__name__).logger.warning(e)
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=shoppinglist_not_found
                )), 404
            )


class ShoppingItemDetailApi(Resource):
    """
    Handles CRUD functionality for a single shopping item for a specific user.
    """

    @jwt_required
    def get(self, shoppinglistId):
        """
        Method to handle GET request from client and retun client shoppingitems.
        :param shoppinglistId: shoppinglist id.
        :return: response.
        """

        current_user = get_jwt_identity()

        # user instance
        user = User.query.filter_by(username=current_user).first()

        shoppinglistId = shoppinglistId

        # get shoppinglist instance
        shoppinglist = ShoppingList.get(shoppinglistId, user.id)

        if not shoppinglist:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=shoppinglist_not_found
                )), 404
            )

        shoppingitems = [{'id': item.id, 'name': item.name}
                         for item in shoppinglist.shopping_items.all()]

        return make_response(
            jsonify(dict(
                status='success',
                message='Total items %(count)s' % dict(count=len(shoppingitems)),
                data=dict(
                    shoppinglist=shoppinglist.name,
                    shoppingitems=shoppingitems
                )
            )), 200
        )

    @use_args(shoppingitem_create_args)
    @jwt_required
    def post(self, args, shoppinglistId):
        """
        Handles post request to create shoppingitem.
        :return:
        """

        current_user = get_jwt_identity()

        # get user instance.
        user = User.query.filter_by(username=current_user).first()

        # get shoppinglist id.
        shl_id = shoppinglistId

        # get shoppingitems data.
        name = args.get('name')
        price = args.get('price')
        bought = args.get('bought')

        # check if item with similar name exists within the shoppinglist itself.
        status = ShoppingItem.exists(shl_id, name)

        if status:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=shoppingitem_exists
                )), 400
            )

        # get shoppinglist instance.
        instance = ShoppingList.get(shoppinglistId=shl_id, ownerId=user.id)

        # create shoppingitem instance.
        item = ShoppingItem(name=name, price=price, bought=bought)

        # save item
        item.save()

        # add item to shopping_items list and save
        instance.shopping_items.append(item)
        instance.save()

        return make_response(
            jsonify(dict(
                status='success',
                message=shoppingitem_created,
                data=dict(
                    id=item.id,
                    name=item.name,
                    price=item.price,
                    bought=item.bought
                )
            )), 201
        )

    @use_args(shoppingitem_update_args)
    @jwt_required
    def put(self, args, shoppinglistId, shoppingitemId):
        """
        Handles PUT request from client and updates specified shoppingitem.
        :param args: new data.
        :param shoppinglistId: shopping list id.
        :param shoppingitemId: shopping item id.
        :return: response.
        """

        current_user = get_jwt_identity()

        # get user instance.
        user = User.get_user(current_user)

        # get shoppinglist instance.
        shoppinglist = user.shopping_lists.filter_by(id=shoppinglistId).first()

        # check if it exists.
        if not shoppinglist:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=shoppinglist_not_found
                )), 404
            )

        # get shoppingitem instance.
        shoppingitem = shoppinglist.shopping_items.filter_by(id=shoppingitemId).first()

        # check if it exists.
        if not shoppingitem:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=shoppingitem_not_found
                )), 404
            )

        name = args.get('name')
        price = args.get('price')
        bought = args.get('bought')

        # make sure that if name is provided then it should
        # not have a minimum of 3 characters.
        if name:
            _validate = validate.Length(min=3)

            try:
                _validate(name)

            except Exception as e:
                return make_response(
                    jsonify(dict(
                        status='fail',
                        message=dict(
                            name=e.args
                        )
                    )), 422
                )

            # check if shoppingitem with suggested name exists.
            if name != shoppingitem.name:
                status = ShoppingItem.exists(shoppinglistId, name)

                if status:
                    return make_response(
                        jsonify(dict(
                            status='fail',
                            message=shoppingitem_exists
                        )), 400
                    )

                # if it doesn't then assign new name to shoppingitem.
                shoppingitem.name = name

        # assign new price.
        if price:
            shoppingitem.price = price

        # set new bought flag
        if bought:
            shoppingitem.bought = bought

        # finally save changes.
        shoppingitem.save()

        # return response to client.
        return make_response(
            jsonify(dict(
                status='success',
                message=shoppingitem_updated,
                data=dict(
                    name=shoppingitem.name,
                    price=shoppingitem.price,
                    bought=shoppingitem.bought,
                    updated_on=shoppingitem.updated.strftime("%Y-%m-%d %H:%M:%S")
                )
            )), 200)

    @jwt_required
    def delete(self, shoppinglistId, shoppingitemId):
        """
        Handles DELETE request from client to delete a single shoppingitem identified by
        its id.
        :param shoppinglistId: shoppinglist id.
        :param shoppingitemId: shoppingitem id.
        :return: response.
        """

        current_user = get_jwt_identity()

        user = User.get_user(current_user)

        # get shoppinglist
        shoppinglist = user.shopping_lists.filter_by(id=shoppinglistId).first()

        # check if shoppinglist exists.
        if not shoppinglist:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=shoppinglist_not_found
                )), 404
            )

        # get shoppingitem.
        shoppingitem = shoppinglist.shopping_items.filter_by(id=shoppingitemId).first()

        # check if shoppingitem exists.
        if not shoppingitem:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=shoppingitem_not_found
                )), 404
            )

        # delete shoppingitem.
        shoppingitem.delete()

        # return response to client.
        return {}, 204


class SearchShoppingListApi(Resource):
    """
    Search shopping lists names using provided keywords
    """

    @use_args(search_args)
    @jwt_required
    def get(self, args):
        """
        Handles GET request to search for shoppinglist.
        """

        response = {}

        page = args.get('page', 1)
        limit = args.get('limit', MAX_ITEMS_PER_PAGE)

        current_user = get_jwt_identity()

        user = User.get_user(current_user)

        _term = args.get('q')

        term = prep_keyword(_term)

        shoppinglists = user.shopping_lists.filter(ShoppingList.name.ilike(term)).paginate(page, limit)

        if any(shoppinglists.items):
            response.setdefault('total_pages', shoppinglists.pages)
            results = [shl.name for shl in shoppinglists.items]
            response.setdefault('results', results)

            if shoppinglists.has_prev:
                previous_page = urlmaker(request, shoppinglists.prev_num, limit)
                response.setdefault('previous_page', previous_page)

            if shoppinglists.has_next:
                next_page = urlmaker(request, shoppinglists.next_num, limit)
                response.setdefault('next_page', next_page)

        else:
            response.setdefault('message', search_not_found)
            response.setdefault('results', [])

        return make_response(jsonify(response), 200)
