# -*- coding: utf-8 -*-

"""
This module tests for errors in shoppinglists endpoints functionalities.
"""

from ddt import ddt, data

from flask import json
from app import messages as msg
from app.models import ShoppingList
from .shopping_base import TestShoppingListBaseCase


@ddt
class TestShoppingListErrorsCase(TestShoppingListBaseCase):
    def test_user_cannot_create_shoppinglist_with_duplicate_name(self):
        self.register_user()
        login_response = self.login_user()

        # get auth token
        auth_token = json.loads(login_response.get_data(as_text=True))['data']['auth_token']

        obj = {
            'name': self.shopping_list.name,
            'description': self.shopping_list.description}

        # create first shopping list.
        self.create_shoppinglist(token=auth_token, details=obj)

        second_create_response = self.create_shoppinglist(token=auth_token, details=obj)

        # data returned for second response.
        res_data = json.loads(second_create_response.get_data(as_text=True))

        # assertions.
        self.assertStatus(second_create_response, 409)
        self.assertEquals(res_data['message'], msg.shoppinglist_name_exists)

    @data('12 +344', 'shop1ngl1st---', 'f00d(s)', '""""""#$%&*&%$#@')
    def test_cannot_create_shoppinglist_with_invalid_names(self, name):
        self.register_user()
        login_response = self.login_user()

        # get auth token
        auth_token = json.loads(login_response.get_data(as_text=True))['data']['auth_token']

        obj = {
            'name': name,
            'description': self.shopping_list.description}

        # use auth_token to create shopping list.
        create_shl_response = self.create_shoppinglist(token=auth_token, details=obj)

        # query shoppinglist obj.
        shl = ShoppingList.query.filter_by(name=name).first()

        self.assertStatus(create_shl_response, 422)
        self.assertIsNone(shl)

    def test_cannot_retrieve_shoppinglist_with_id_that_does_not_exist(self):
        # register user.
        self.register_user()

        # login created user.
        login_response = self.login_user()

        # get auth token
        auth_token = json.loads(
            login_response.get_data(as_text=True))['data']['auth_token']

        # make a GET request to retrieve shoppinglist detail with non existing ID.
        shoppinglist_detail_response = self.get_shoppinglist_detail(auth_token, 2000)

        # data returned
        res_data = json.loads(shoppinglist_detail_response.get_data(as_text=True))

        # query db for the shoppinglist object using the random ID.
        obj = ShoppingList.query.filter_by(id=2000).first()

        # assert responses.
        self.assert404(shoppinglist_detail_response)
        self.assertEqual(msg.shoppinglist_not_found, res_data['message'])
        self.assertIsNone(obj)

    @data('"""""', '&&&&&&&&&&', '*!$%$', 'H#l1@y')
    def test_canmot_update_shoppinglist_with_invalid_name(self, name):
        # register user
        self.register_user()

        # login created user.
        login_response = self.login_user()

        # get auth token
        auth_token = json.loads(
            login_response.get_data(as_text=True))['data']['auth_token']

        # new shoppinglist info.
        details = {
            'name': 'New Shoppinglist',
            'description': 'New Shoppinglist description.'}

        # new info
        new_info = dict(
            name=name,
            description='this shoppinglist was updated')

        # use auth_token to create shopping list.
        create_response = self.create_shoppinglist(token=auth_token, details=details)

        # get ID of created shoppinglist from response.
        shl_id = json.loads(
            create_response.get_data(as_text=True))['data']['id']

        update_response = self.update_shoppinglist(auth_token, shl_id, new_info)

        # query shoppinglist object from database.
        obj = ShoppingList.query.filter_by(id=shl_id).first()

        # assert response
        self.assertStatus(update_response, 422)
        self.assertIsNotNone(obj)


    def test_cannot_update_shoppinglist_name_with_a_name_that_exists(self):
        # register first user.
        self.register_user()
        login_response = self.login_user()

        # get auth token of first user.
        auth_token = json.loads(
            login_response.get_data(as_text=True))['data']['auth_token']

        # new shoppinglists info.
        first = {
            'name': 'New Shoppinglist',
            'description': 'New Shoppinglist description.'}

        duplicate = {
            'name': 'New Shoppinglist',
            'description': 'Other new Shoppinglist description.'}

        # use auth_token to create shoppinglist for first user and get id of shoppinglist.
        res = self.create_shoppinglist(token=auth_token, details=first)
        shl_id = json.loads(
            res.get_data(as_text=True))['data']['id']

        response = self.update_shoppinglist(auth_token, shl_id, duplicate)

        # query shoppinglist obj.
        obj = ShoppingList.query.filter_by(name=duplicate.get('name')).all()

        # assert response
        self.assertStatus(response, 409)
        self.assertEqual(len(obj), 1)

        # object from db description should be equal to the details used to
        # create the first shoppinglist.
        self.assertTrue(obj[0].description == first.get('description'))

    def test_cannot_delete_non_existing_shoppinglist(self):
        self.register_user()
        login_response = self.login_user()

        # get auth token.
        token = json.loads(login_response.get_data(as_text=True))['data']['auth_token']

        test_id = 1234567654
        # delete shopping list with a random id that does not exist.
        res = self.delete_shoppinglist(token=token, id=test_id, name='')

        res_data = json.loads(res.get_data(as_text=True))

        # query obj from db.
        obj = ShoppingList.query.filter_by(id=test_id).first()

        # assert response.
        self.assertStatus(res, 404)
        self.assertTrue(msg.shoppinglist_not_found == res_data['message'])
        self.assertIsNone(obj)

    def test_cannot_delete_shoppinglist_using_incorrect_name(self):
        self.register_user()
        login_response = self.login_user()

        auth_token = json.loads(login_response.get_data(as_text=True))['data']['auth_token']

        # shoppinglist name
        det = {
            'name': 'School'}

        # use auth_token to create shopping list.
        create_response = self.create_shoppinglist(token=auth_token, details=det)

        # get shoppinglist ID.
        shl_id = json.loads(create_response.get_data(as_text=True))['data']['id']

        # make DELETE request to server
        res = self.delete_shoppinglist(token=auth_token, id=shl_id, name='incorrect')

        # assertions.
        self.assertStatus(res, 403)

    def test_user_cannot_delete_empty_shoppinglist(self):
        self.register_user()
        login_response = self.login_user()

        auth_token = json.loads(login_response.get_data(as_text=True))['data']['auth_token']

        # delete all shopping lists
        res = self.delete_all_shoppinglists(auth_token, self.test_user.password)

        # assertions.
        self.assert404(res)

    def test_user_cannot_delet_shoppinglists_using_incorrect_password(self):
        self.register_user()
        login_response = self.login_user()

        auth_token = json.loads(login_response.get_data(as_text=True))['data']['auth_token']

        # delete all shopping lists
        res = self.delete_all_shoppinglists(auth_token, 'incorrectpassword')

        # assertions.
        self.assert403(res)
