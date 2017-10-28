from flask import Blueprint

from app import API

shopping_list_blueprint = Blueprint('shopping_list', __name__)


from .views import CreateShoppingListApi, UserShoppingListsApi, UserShoppingListDetailApi


API.add_resource(UserShoppingListsApi, 'shopping-lists'),
API.add_resource(UserShoppingListDetailApi, 'shopping-lists/<int:id>'),
API.add_resource(CreateShoppingListApi, 'shopping-lists'),
