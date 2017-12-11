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

from .utils import *
from ..conf.settings import MAX_ITEMS_PER_PAGE
from ..core.loggers import AppLogger
from ..core.validators import validate
from ..messages import *
from ..models import User, ShoppingList, ShoppingItem


class ShoppingListsApi(Resource):
    @use_args(pagination_args)
    @jwt_required
    def get(self, args):
        """
        Retrieve all shopping lists.
        """

        def params_error(error):
            """
            A function to return errors found in query parameters.
            :param error: error message.
            :return: error response.
            """

            return make_response(
                jsonify(dict(
                    status='fail',
                    message=error
                )), 422
            )

        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()

        response = {}

        response.setdefault('status', 'success')
        response.setdefault('total_shoppinglist', user.shopping_lists.count())

        page = args.get('page', 1)
        limit = args.get('limit', MAX_ITEMS_PER_PAGE)

        # if the values are default, then no need for pagination.
        if any([page != 1, limit != MAX_ITEMS_PER_PAGE]):
            if page < 0:
                return params_error(negative_page)

            if limit < 0:
                return params_error(negative_limit)

            paginated = user.shopping_lists.paginate(page=page, per_page=limit, error_out=False)

            response.setdefault('current_page', paginated.page)
            response.setdefault('total_pages', paginated.pages)
            response.setdefault('total_items', paginated.total)

            if paginated.has_prev:
                prev_page_url = urlmaker(request, paginated.prev_num, limit).make_url()
                response.setdefault('previous_page', paginated.prev_num)
                response.setdefault('previous_page_url', prev_page_url)

            if paginated.has_next:
                next_page_url = urlmaker(request, paginated.next_num, limit).make_url()
                response.setdefault('next_page', paginated.next_num)
                response.setdefault('next_page_url', next_page_url)

            output = [{
                'id': shl.id,
                'name': shl.name,
                'description': shl.description} for shl in paginated.items]

            response.setdefault('data', output)

        else:
            shoppinglists = user.shopping_lists.all()

            output = [{
                'id': shl.id,
                'name': shl.name,
                'description': shl.description} for shl in shoppinglists]

            response.setdefault('shopping_lists', output)

        return make_response(
            jsonify(response), 200
        )

    @use_args(create_args)
    @jwt_required
    def post(self, data):
        """
        Handles creation of shoppinglist objects.
        """

        current_user = get_jwt_identity()

        name = data.get('name')
        description = data.get('description')

        user = User.query.filter_by(username=current_user).first()

        try:
            validate(value=name, allow_spaces=True)

        except Exception as e:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message="Shoppinglist name value %(err)s" % dict(err=e.args[0])
                )), 422
            )

        # check if shopping list exists
        old_shl = ShoppingList.query.filter_by(name=name, owner_id=user.id).first()

        # if shopping list exists return bad request response.
        if old_shl:

            return make_response(
                jsonify(dict(
                    status='fail',
                    message=shoppinglist_name_exists
                )), 409
            )

        # get user instance.
        user = User.query.filter_by(username=current_user).first()

        # save shopping list.
        shl = ShoppingList(name=name, owner_id=user.id, description=description)
        shl.save()

        return make_response(
            jsonify(dict(
                status='success',
                message=shoppinglist_created,
                data=dict(
                    id=shl.id,
                    name=shl.name,
                    created_on=shl.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
            )), 201)


class ShoppingListDetailApi(Resource):
    """
    Resource that handles specific user shoppinglist and accepts
    http methods GET, PUT and DELETE only. This resource also accepts
    an integer ID in url path.
    """

    @jwt_required
    def get(self, id=None):
        """
        Handles GET request to fetch specific shopping list requested by client.

        :param id: id of shopping list.
        :return: response.
        """
        current_user = get_jwt_identity()

        # get user instance.
        user = User.query.filter_by(username=current_user).first()

        data = {}

        # get shoppinglist using provided id, if not found raise error 404 and
        # return response to client.
        try:
            shoppinglist = user.shopping_lists.filter_by(
                id=int(id)).first_or_404()

        except Exception as e:
            AppLogger(self.__class__.__name__).logger.warning(e)
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=shoppinglist_not_found
                )), 404
            )

        # filter bought items and those not bought.
        bought = shoppinglist.shopping_items.filter_by(bought=True).count()
        not_bought = shoppinglist.shopping_items.filter_by(bought=False).count()

        data.setdefault('id', shoppinglist.id)
        data.setdefault('name', shoppinglist.name)
        data.setdefault('description', shoppinglist.description)
        data.setdefault('total_items', shoppinglist.shopping_items.count())
        data.setdefault('bought_items', bought)
        data.setdefault('items_not_bought', not_bought)
        data.setdefault('total', shoppinglist.cost())
        data.setdefault('created_on', shoppinglist.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        data.setdefault('updated_on', shoppinglist.updated.strftime("%Y-%m-%d %H:%M:%S"))

        return make_response(
            jsonify(dict(
                status='success',
                data=data
            )), 200
        )

    @use_args(update_args)
    @jwt_required
    def put(self, args, id):
        """
        Handles PUT request to update user shopping list.

        :param args: new name to be updated.
        :param id: shopping list id
        :return: response
        """
        current_user = get_jwt_identity()

        def response():
            return make_response(
                jsonify(dict(
                    status='success',
                    message=shoppinglist_updated,
                    data=dict(
                        name=shoppinglist.name,
                        description=shoppinglist.description,
                        updated_on=shoppinglist.updated.strftime("%Y-%m-%d %H:%M:%S"))
                )), 200)

        # get user instance
        user = User.query.filter_by(username=current_user).first()

        # new name provided by client
        name = args.get('name', None)
        description = args.get('description', None)

        # check if shopping list exists, if not, return 404 response to client.
        shoppinglist = user.shopping_lists.filter_by(id=int(id)).first()

        if not shoppinglist:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=shoppinglist_not_found
                )), 404)

        # if name is none then there is no need to modify client resource.
        if any([name, description]):
            if name:

                try:
                    validate(value=name, allow_spaces=True)

                except Exception as e:
                    return make_response(
                        jsonify(dict(
                            status='fail',
                            message="Shoppinglist name value %(err)s" % dict(err=e.args[0])
                        )), 422
                    )

                # check if shopping list with the same name exists.
                shl = ShoppingList.query.filter_by(name=name, owner_id=user.id).first()

                # if shopping list exists and it is not owned by the client return bad request.
                if shl:
                    msg = shoppinglist_name_exists
                    return make_response(
                        jsonify(dict(
                            status='fail',
                            message=msg
                        )), 409)

                if description:
                    shoppinglist.description = description

                shoppinglist.name = name
                shoppinglist.save()
                return response()

        return make_response(
            jsonify(dict(
                status='success',
                message=shoppinglist_not_updated
            )), 200)


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
                    status="success",
                    message=shoppinglist_deleted
                )), 200)

        except Exception as e:
            AppLogger(self.__class__.__name__).logger.warning(e)
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=shoppinglist_not_found
                )), 404)


class ShoppingItemListApi(Resource):
    """
    Handles retrieving of client shoppingitems list.
    """

    @use_args(pagination_args)
    @jwt_required
    def get(self, query_args, shl_id=None):
        """
        Method to handle GET request from client and retun client shoppingitems.
        :param query_args: limit and page arguments.
        :param shl_id: shoppinglist id.
        :return: response.
        """

        def params_error(error):
            """
            A function to return errors found in query parameters.

            :param error: error message.
            :return: error response.
            """

            return make_response(
                jsonify(dict(
                    status='fail',
                    message=error
                )), 422)

        data = {}

        current_user = get_jwt_identity()

        # user instance
        user = User.query.filter_by(username=current_user).first()

        # get shoppinglist instance
        shoppinglist = ShoppingList.get(shl_id, user.id)

        if not shoppinglist:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=shoppinglist_not_found
                )), 404)

        data.setdefault('status', 'success')
        data.setdefault('total_items', shoppinglist.shopping_items.count())

        page = query_args.get('page', 1)
        limit = query_args.get('limit', MAX_ITEMS_PER_PAGE)

        if any([page != 1, limit != MAX_ITEMS_PER_PAGE]):

            if page < 0:
                return params_error(negative_page)

            if limit < 0:
                return params_error(negative_limit)

            paginated = shoppinglist.shopping_items.paginate(page, limit, False)

            data.setdefault('current_page', paginated.page)
            data.setdefault('total_pages', paginated.pages)
            data.setdefault('total_items', paginated.total)

            if paginated.has_prev:
                prev_page_url = urlmaker(request, paginated.prev_num, limit).make_url()
                data.setdefault('previous_page', paginated.prev_num)
                data.setdefault('previous_page_url', prev_page_url)

            if paginated.has_next:
                next_page_url = urlmaker(request, paginated.next_num, limit).make_url()
                data.setdefault('next_page', paginated.next_num)
                data.setdefault('next_page_url', next_page_url)

            output = [
                {'name': item.name,
                 'price': item.price,
                 'bought': item.bought} for item in paginated.items]

            data.setdefault('total_pages', paginated.pages)
            data.setdefault('shopping_items', output)

        else:
            items = [
                {'id': item.id,
                 'name': item.name} for item in shoppinglist.shopping_items.all()]
            data.setdefault('shopping_items', items)

        return make_response(jsonify(data), 200)


class ShoppingItemDetailApi(Resource):
    """
    Handles CRUD functionality for a single shopping item for a specific user.
    """

    @use_args(pagination_args)
    @jwt_required
    def get(self, query_args, shl_id, item_id=None):
        """
        Method to handle GET request from client and retun client shoppingitems.

        """

        data = {}

        current_user = get_jwt_identity()

        # user instance
        user = User.query.filter_by(username=current_user).first()

        # get shoppinglist instance.
        shoppinglist = ShoppingList.get(shl_id, user.id)

        if not shoppinglist:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=shoppinglist_not_found
                )), 404)

        shoppingitem = shoppinglist.shopping_items.filter_by(id=item_id).first()

        if not shoppingitem:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=shoppingitem_not_found
                )), 404)

        data.setdefault('id', shoppingitem.id)
        data.setdefault('name', shoppingitem.name)
        data.setdefault('price', shoppingitem.price)
        data.setdefault('bought', shoppingitem.bought)
        data.setdefault('quantity_description', shoppingitem.quantity_description)
        data.setdefault('created_on', shoppingitem.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        data.setdefault('updated_on', shoppingitem.updated.strftime("%Y-%m-%d %H:%M:%S"))
        return make_response(
            jsonify(dict(
                status='success',
                data=data
            )), 200)

    @use_args(item_create_args)
    @jwt_required
    def post(self, args, shl_id):
        """
        Handles post request to create shoppingitem object.
        """

        current_user = get_jwt_identity()

        # get user instance.
        user = User.query.filter_by(username=current_user).first()

        # get shoppingitems data.
        name = args.get('name')
        price = args.get('price')
        quantity = args.get('quantity_description')

        try:
            validate(value=name, allow_spaces=True)

        except Exception as e:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message="Shoppingitem name value %(err)s" % dict(err=e.args[0])
                )), 422
            )

        # get shoppinglist instance.
        instance = ShoppingList.get(shoppinglistId=shl_id, ownerId=user.id)

        if not instance:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=shoppinglist_not_found
                )), 404)

        # check if quantity description are similar.
        exists = instance.shopping_items.filter_by(name=name, quantity_description=quantity).first()
        if exists:
            return make_response(jsonify(dict(
                status='fail',
                message=shoppingitem_exists
            )), 404)

        # create shoppingitem instance.
        item = ShoppingItem(name=name, price=price, quantity_description=quantity)

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
                    quantity_description=item.quantity_description,
                    bought=item.bought
                )
            )), 201
        )

    @use_args(item_update_args)
    @jwt_required
    def put(self, args, shl_id, item_id=None):
        """
        Handles PUT request from client and updates specified shoppingitem.
        :param args: new data.
        :param shl_id: shopping list id.
        :param item_id: shopping item id.
        :return: response.
        """

        current_user = get_jwt_identity()

        # get user instance.
        user = User.get_by_username(current_user)

        # get shoppinglist instance.
        shoppinglist = user.shopping_lists.filter_by(id=shl_id).first()

        # check if it exists.
        if not shoppinglist:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=shoppinglist_not_found
                )), 404
            )

        # get shoppingitem instance.
        shoppingitem = shoppinglist.shopping_items.filter_by(id=item_id).first()

        # check if it exists.
        if not shoppingitem:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=shoppingitem_not_found
                )), 404
            )

        name = args.get('name', None)
        price = args.get('price', None)
        quantity = args.get('quantity_description', None)
        bought = args.get('bought', None)

        if any([name, price, quantity, bought]):
            try:
                validate(value=name, allow_spaces=True)

            except Exception as e:
                return make_response(
                    jsonify(dict(
                        status='fail',
                        message="Shoppingitem name value %(err)s" % dict(err=e.args[0])
                    )), 422
                )

            if not name:
                name = shoppingitem.name

            shoppingitem.name = name

            # assign new price.
            if price:
                shoppingitem.price = price

            if quantity:
                # quantity description should not be similar.
                shoppingitem.quantity_description = quantity

            # set new bought flag
            if bought:
                if not(bought == '0' or bought == '1'):
                    bought = shoppingitem.bought

                if bought == '1':
                    bought = True

                if bought == '0':
                    bought = False

                shoppingitem.bought = bought

            # finally save changes.
            shoppingitem.save()

            # return response to client.
            return make_response(
                jsonify(dict(
                    status='success',
                    message=shoppingitem_updated,
                    data=dict(
                        id=shoppingitem.id,
                        name=shoppingitem.name,
                        price=shoppingitem.price,
                        quantity_description=shoppingitem.quantity_description,
                        bought=shoppingitem.bought,
                        updated_on=shoppingitem.updated.strftime("%Y-%m-%d %H:%M:%S")
                    )
                )), 200)

        return make_response(
            jsonify(dict(
                status='fail',
                message=shoppingitem_not_updated,
                data=dict(
                        id=shoppingitem.id,
                        name=shoppingitem.name,
                        price=shoppingitem.price,
                        quantity_description=shoppingitem.quantity_description,
                        bought=shoppingitem.bought,
                        updated_on=shoppingitem.updated.strftime("%Y-%m-%d %H:%M:%S")
                    )
            )), 200)

    @jwt_required
    def delete(self, shl_id, item_id):
        """
        Handles DELETE request from client to delete a single shoppingitem identified by
        its id.
        :param shoppinglistId: shoppinglist id.
        :param shoppingitemId: shoppingitem id.
        :return: response.
        """

        current_user = get_jwt_identity()

        user = User.get_by_username(current_user)

        # get shoppinglist
        shoppinglist = user.shopping_lists.filter_by(id=shl_id).first()

        # check if shoppinglist exists.
        if not shoppinglist:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=shoppinglist_not_found
                )), 404)

        # get shoppingitem.
        shoppingitem = shoppinglist.shopping_items.filter_by(id=item_id).first()

        # check if shoppingitem exists.
        if not shoppingitem:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=shoppingitem_not_found
                )), 404)

        # delete shoppingitem.
        shoppingitem.delete()

        # return response to client.
        return make_response(jsonify(dict(
            status='success',
            message=shoppingitem_deleted)), 200)


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

        user = User.get_by_username(current_user)

        _term = args.get('q')

        if _term == '':
            return make_response(
                jsonify(dict(
                    status='fail',
                    message="please provide query value"
                )), 422)

        term = prep_keyword(_term)
        shoppinglists = user.\
            shopping_lists.filter(ShoppingList.name.ilike(term)).paginate(page, limit)

        if any(shoppinglists.items):
            response.setdefault('total_pages', shoppinglists.pages)
            results = [
                {shl.name:
                     {'shoppingitems':
                          [item.name for item in shl.shopping_items.all()]
                      }
                 } for shl in shoppinglists.items]
            response.setdefault('shoppinglists', results)

            if shoppinglists.has_prev:
                previous_page = urlmaker(request, shoppinglists.prev_num, limit).make_url()
                response.setdefault('previous_page', previous_page)

            if shoppinglists.has_next:
                next_page = urlmaker(request, shoppinglists.next_num, limit).make_url()
                response.setdefault('next_page', next_page)

        else:
            response.setdefault('message', search_not_found)
            response.setdefault('results', [])

        response.setdefault('items_in_page', len(shoppinglists.items))
        return make_response(jsonify(response), 200)
