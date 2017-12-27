# -*- coding: utf-8 -*-

"""
This module tests for errors in shoppinglists endpoints functionalities.
"""

from flask import json
from app import messages as msg
from app.models import ShoppingList, User
from .shopping_base import TestShoppingListBaseCase


class TestShoppingListCase(TestShoppingListBaseCase):
    """
    Test all CRUD functionalities of shopping list model.
    """

    def test_user_can_create_shopping_list(self):
        self.register_user()
        login_response = self.login_user()

        # get auth token
        auth_token = json.loads(login_response.get_data(as_text=True))['data']['auth_token']

        obj = {
            'name': self.shopping_list.name,
            'description': self.shopping_list.description}

        # use auth_token to create shopping list.
        create_shl_response = self.create_shoppinglist(token=auth_token, details=obj)

        # assert create shopping list response.
        self.assertStatus(create_shl_response, 201)

        # data returned with create shopping list response.
        create_shl_response_data = json.loads(create_shl_response.get_data(as_text=True))

        # query user so that we can confirm owner_id
        user = User.query.filter_by(username=self.test_user.username).first()

        # query created shopping list.
        shl = ShoppingList.query.filter_by(name=self.shopping_list.name).first()

        # assertions.
        self.assertStatus(create_shl_response, 201)
        self.assertEqual(create_shl_response_data['message'], msg.shoppinglist_created)
        self.assertEqual(create_shl_response_data['data']['name'], shl.name)
        self.assertEqual(create_shl_response_data['data']['created_on'],
                         shl.timestamp.strftime('%Y-%m-%d %H:%M:%S'))
        self.assertEqual(user.id, shl.owner_id)

    def test_user_can_view_all_shoppinglists(self):
        self.register_user()
        login_response = self.login_user()

        # get auth token
        auth_token = json.loads(login_response.get_data(as_text=True))['data']['auth_token']

        # shopping list name
        shl_list = {
            'first list': 'first shoppinglist',
            'second list': 'second shoppinglist',
            'third list': 'third shoppinglist'}

        for k, v in shl_list.items():
            det = {'name': k, 'description': v}
            self.create_shoppinglist(token=auth_token, details=det)

        # make a get request to retrieve shopping list.
        res = self.get_shoppinglists(token=auth_token)

        # data returned with the response
        data = json.loads(res.get_data(as_text=True))

        # assertions
        self.assertEqual(len(data['shopping_lists']), len(shl_list))

    def test_user_can_retrieve_specific_shoppinglist_using_id(self):
        self.register_user()
        login_response = self.login_user()

        # get auth token
        auth_token = json.loads(login_response.get_data(as_text=True))['data']['auth_token']

        # shopping list name
        shl_list = {
            'first list': 'first shoppinglist',
            'second list': 'second shoppinglist',
            'third list': 'third shoppinglist'}

        for key, val in shl_list.items():
            det = {'name': key, 'description': val}
            self.create_shoppinglist(token=auth_token, details=det)

        # make a get request to retrieve shopping list.
        get_shoppinglists_response = self.get_shoppinglists(token=auth_token)

        # data returned with the response
        get_shoppinglists_response_data = json.loads(
            get_shoppinglists_response.get_data(as_text=True))

        # extract shoppinglist id.
        shl_id = get_shoppinglists_response_data['shopping_lists'][0].get('id')

        # query shopping list in db and use it to assert returned response
        shl = ShoppingList.query.filter_by(id=shl_id).first()

        # make a GET request to retrieve shoppinglist detail.
        response = self.get_shoppinglist_detail(auth_token, shl_id)

        # data returned
        response_data = json.loads(response.get_data(as_text=True))

        # assert responses.
        self.assert200(response)
        self.assertEqual(response_data['data']['id'], shl.id)
        self.assertEqual(response_data['data']['name'], shl.name)
        self.assertEqual(response_data['data']['description'], shl.description)
        self.assertEqual(response_data['data']['created_on'],
                         shl.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        self.assertEqual(response_data['data']['updated_on'],
                         shl.updated.strftime("%Y-%m-%d %H:%M:%S"))

    def test_user_can_update_shoppinglist(self):
        self.register_user()
        login_response = self.login_user()

        # get auth token
        auth_token = json.loads(login_response.get_data(as_text=True))['data']['auth_token']

        # new shoppinglist info.
        details = {
            'name': 'New Shoppinglist',
            'description': 'New Shoppinglist description.'}

        # new info
        new_info = dict(
            name='updated first list',
            description='this shoppinglist was updated')

        # use auth_token to create shopping list.
        create_response = self.create_shoppinglist(token=auth_token, details=details)

        # get ID of created shoppinglist from response.
        shl_id = json.loads(create_response.get_data(as_text=True))['data']['id']

        update_response = self.update_shoppinglist(auth_token, shl_id, new_info)

        # query shoppinglist object from database.
        obj = ShoppingList.query.filter_by(id=shl_id).first()

        # get data from response
        response_data = json.loads(update_response.get_data(as_text=True))

        # assert response
        self.assert200(update_response)
        self.assertEqual(msg.shoppinglist_updated, response_data['message'])
        self.assertIsNotNone(obj)
        self.assertEqual(response_data['data']['name'], obj.name)
        self.assertEqual(response_data['data']['description'], obj.description)

    def test_user_can_only_update_shoppinglists_that_he_or_she_created(self):
        self.register_user()
        login_response = self.login_user()

        # get auth token
        auth_token = json.loads(login_response.get_data(as_text=True))['data']['auth_token']

        # use random shoppinglist id that we know it does not exist.
        shl_id = 100009
        new_info = {
            'name': 'invalid',
            'description': 'This will not work'}

        update_response = self.update_shoppinglist(auth_token, shl_id, new_info)

        # get data from response
        response_data = json.loads(update_response.get_data(as_text=True))

        # assert response
        self.assert404(update_response)
        self.assertTrue(response_data['message'] == msg.shoppinglist_not_found)

    def test_shoppinglist_not_modified_if_no_data_is_provided(self):
        self.register_user()
        auth_token = json.loads(self.login_user().get_data(as_text=True))['data']['auth_token']

        details = dict(
            name='Breakfast',
            description='Next week breakfast')

        create_res = self.create_shoppinglist(auth_token, details)

        shl_id = json.loads(create_res.get_data(as_text=True))['data']['id']

        update_res = self.update_shoppinglist(auth_token, shl_id, new_info={})

        obj = ShoppingList.query.filter_by(id=shl_id).first()

        data = json.loads(update_res.get_data(as_text=True))

        self.assert200(update_res)
        self.assertTrue(data['message'] == msg.shoppinglist_not_updated)
        self.assertEqual(details['name'], obj.name)
        self.assertEqual(details['description'], obj.description)

    def test_user_can_delete_shoppinglist(self):
        self.register_user()
        login_response = self.login_user()

        auth_token = json.loads(login_response.get_data(as_text=True))['data']['auth_token']

        # shoppinglist name
        det = {'name': 'School'}

        # use auth_token to create shopping list.
        create_response = self.create_shoppinglist(token=auth_token, details=det)

        # get shoppinglist ID.
        shl_id = json.loads(create_response.get_data(as_text=True))['data']['id']

        # make DELETE request to server
        r = self.delete_shoppinglist(token=auth_token, id=shl_id, name=det.get('name'))

        # query obj from db.
        obj = ShoppingList.query.filter_by(name=det.get('name')).first()

        # assertions.
        self.assertStatus(r, 200)
        assert json.loads(r.get_data(as_text=True))['message'] == msg.shoppinglist_deleted
        self.assertIsNone(obj)

    def test_user_can_delete_all_shoppinglists(self):
        self.register_user()
        login_response = self.login_user()

        auth_token = json.loads(login_response.get_data(as_text=True))['data']['auth_token']

        # create mass shopping lists.

        for shl in self.shoppinglists:
            det = {'name': shl}

            self.create_shoppinglist(token=auth_token, details=det)

        all_shl = json.loads(self.get_shoppinglists(auth_token).get_data(as_text=True))

        # get shoppinglists from database.
        shls = User.get_by_username(self.test_user.username).shopping_lists.count()

        self.assertEqual(len(all_shl['shopping_lists']), len(self.shoppinglists))
        self.assertEqual(len(all_shl['shopping_lists']), shls)

        # delete all shopping lists
        res = self.delete_all_shoppinglists(auth_token, self.test_user.password)

        # assertions.
        shoppinglists = User.get_by_username(self.test_user.username).shopping_lists.count()
        self.assertTrue(shoppinglists == 0)
        self.assert200(res)
