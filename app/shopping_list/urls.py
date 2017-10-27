import collections

from flask import Blueprint

from app import API

shopping_list_blueprint = Blueprint('shopping_list', __name__)


from .views import CreateShoppingListApi

url = collections.namedtuple('url', ['route', 'resource'])

shopping_list_urls = [
    url('shopping-list/create', CreateShoppingListApi),
]

for url in shopping_list_urls:
    API.add_resource(url.resource, url.route)


