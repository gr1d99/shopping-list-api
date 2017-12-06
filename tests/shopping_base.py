import collections

from flask import json
from flask_restful import url_for
from flask_testing import TestCase

from app import APP, DB
from app.conf import app_config

from .auth_base import TestBase


class TestShoppingListBase(TestBase):

    def create_app(self):
        # update app configuration to testing.
        APP.config.from_object(app_config.TestingConfig)
        return APP

    def setUp(self):
        """
        Prep app for testing.
        """
        super(TestShoppingListBase, self).setUp()

        self.another_test_user = self.model('usertwo', "user_two_password", "user_two@gmail.com")
        self.shoppinglist_model = collections.namedtuple('ShoppingList', ['name', 'description'])
        self.shopping_list = self.shoppinglist_model('testshoppinglist', 'my very first shoppinglist')
        self.shopping_list_two = self.shoppinglist_model('testshoppinglisttwo', "my second shoppinglist")
        self.shoppinglists = ['Birthday', 'School', 'Breakfast', 'Lunch', 'Camping']

    def tearDown(self):
        """
        Called after every test to remove all tables in the database.
        """

        DB.session.remove()
        DB.drop_all()

    def login_user(self, with_header=True, **credentials):
        """
        Helper method to login client.
        """
        credentials.update(
            {'username': self.test_user.username,
             'password': self.test_user.password})

        return super(TestShoppingListBase, self).login_user(with_header=True, **credentials)

    def login_second_user(self):
        """
        Helper method to login another client..

        Makes post request using client information initialized in
        the setUp method.
        """

        credentials = dict(
            username=self.another_test_user.username,
            password=self.another_test_user.password)

        url = url_for('user_login')

        return self.client.post(url, data=credentials)

    def register_user(self):
        """
        Helper method to register client.
        """

        user_info = dict(
            username=self.test_user.username,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        url = url_for('user_register')

        return self.client.post(url, data=user_info)

    def register_second_user(self):
        """
        Helper method to register another client.
        """

        user_info = dict(
            username=self.another_test_user.username,
            email=self.another_test_user.email,
            password=self.another_test_user.password,
            confirm=self.another_test_user.password)

        url = url_for('user_register')

        return self.client.post(url, data=user_info)

    def create_shoppinglist(self, token, details):
        """
        Helper method that creates shoppinglist object.

        :param token: user authentication token.
        :param details: name and description of shoppinglist object.
        :return: response object.
        """

        url = url_for('shoppinglist_list')
        return self.client.post(url, data=details, headers={self.header_name: token})

    def get_shoppinglists(self, token, limit=None, page=None):
        """
        Method to make get request to fetch user shopping lists.
        """

        url = url_for('shoppinglist_list', limit=limit, page=page)

        return self.client.get(url, headers={self.header_name: token})

    def get_shoppinglist_detail(self, token, id):
        """
        Method to make get request and fetch specific shopping list based on provided id.
        """

        # append shoppinglist id at the end of url.
        url = url_for('shoppinglist_detail', id=id)

        return self.client.get(url, headers={self.header_name: token})

    def update_shoppinglist(self, token, id, new_info):
        """
        Method to make PUT request to update user shoppinglist.

        :param token: user auth token
        :param id: shopping list id
        :param new_info: details to update
        :return: response
        """

        url = url_for('shoppinglist_detail', id=id)

        return self.client.put(url, data=new_info, headers={self.header_name: token})

    def delete_shoppinglist(self, token, id):
        """
        Makes a PUT request as client to delete shoppinglist.
        :param token: user auth token.
        :param id: shoppinglist id.
        :return: response from server.
        """

        url = url_for('shoppinglist_detail', id=id)

        return self.client.delete(url, headers={self.header_name: token})


class TestShoppingItemsBase(TestShoppingListBase):
    def setUp(self):
        super(TestShoppingItemsBase, self).setUp()
        _testdata = collections.namedtuple('ShoppingItem',
                                           ['name', 'price', 'quantity_description'])
        self.testdata_1 = _testdata('bread', 90.0, '100 Grams')
        self.testdata_2 = _testdata('blueband', 100.5, '200 Grams')
        self.testdata_3 = _testdata('eggs', 10.5, 'I crate')
        self.testdata_4 = _testdata('sausages', 30, 'One Packet')

        self.shoppingitems = [self.testdata_1, self.testdata_2,
                              self.testdata_3, self.testdata_4]

    def create_shoppingitem(self, token, shl_id, data):
        """
        Makes POST request as client to create shoppingitems.

        :param token: user auth token.
        :param shl_id: shoppinglist id.
        :param data: shoppingitem details
        :return: response.
        """
        
        url = url_for('shoppingitem_create', shoppinglistId=shl_id)

        return self.client.post(url, data=data, headers={self.header_name: token})

    def get_shoppingitems(self, token, shl_id, limit=None, page=None):
        """
        Makes POST request as client to create shoppingitems.

        :param token: user auth token.
        :param shl_id: shoppinglist id.
        :param limit: number of results expected.
        :param page: page number.
        :return: response.
        """

        url = url_for('shoppingitem_detail', shoppinglistId=shl_id, limit=limit, page=page)

        return self.client.get(url, headers={self.header_name: token})

    def get_shoppingitem_detail(self, token, shl_id, item_id):
        """
        Makes GET request as client to retrieve specific shoppingitem.
        :param token: user auth token.
        :param shl_id: ID of shoppinglist..
        :param item_id: ID of shoppingitem.
        :return: response.
        """

        url = url_for('shoppingitem_edit', shoppinglistId=shl_id,
                      shoppingitemId=item_id)

        return self.client.get(url, headers={self.header_name: token})

    def update_shoppingitem(self, token, shoppinglistId, shoppingitemId, data):
        """
        Method to make PUT request as a client and update shoppingitem.
        :param token: user auth token.
        :param shoppinglistId: shopping list id.
        :param shoppingitemId: shopping item id.
        :param data: new data.
        :return: response.
        """

        data = json.dumps(data)
        url = url_for('shoppingitem_edit',
                      shoppinglistId=shoppinglistId, shoppingitemId=shoppingitemId)

        return self.client.put(url, data=data, headers={self.header_name: token})

    def delete_shoppingitem(self, token, shoppinglistId, shoppingitemId):
        """
        Makes DELETE request as a client to delete associated shopping item.
        :param token: user auth token.
        :param id: shopping item id.
        :return: response
        """

        url = url_for('shoppingitem_edit',
                      shoppinglistId=shoppinglistId, shoppingitemId=shoppingitemId)

        return self.client.delete(url, headers={self.header_name: token})


class TestSearchAndPagination(TestShoppingItemsBase):
    """
    Base test case class for testing search functionality and pagination.
    """

    def init_shoppinglists(self):
        # register and authenticate client.
        self.register_user()
        login_resp = self.login_user()

        # get auth token.
        token = json.loads(
            login_resp.get_data(as_text=True))['data']['auth_token']

        # create shoppinglists.
        for shl in self.shoppinglists:
            self.create_shoppinglist(token=token, details=dict(name=shl))

        return token

    def init_shoppingitems(self):
        # register and authenticate client.
        self.register_user()
        login_resp = self.login_user()

        # get auth token.
        token = json.loads(
            login_resp.get_data(as_text=True))['data']['auth_token']

        data = {
            'name': self.shopping_list.name,
            'description': self.shopping_list.description
        }

        # create shoppinglist.
        r = self.create_shoppinglist(token, data)
        shl_id = json.loads(
            r.get_data(as_text=True))['data']['id']

        # create shopping items.
        for item in self.shoppingitems:
            item_det = dict(
                name=item.name,
                price=item.price,
                quantity_description=item.quantity_description)

            self.create_shoppingitem(token, shl_id, item_det)

        return token, shl_id

    def search_shoppinglist(self, token, keyword, limit=None, page=None):
        """
        Method to make search shopping lists.
        :param token: user auth token.
        :param keyword: word used to make search.
        :return: response.
        """

        url = url_for('shoppinglist_search', q=keyword, limit=limit, page=page)
        return self.client.get(url, headers={self.header_name: token})

