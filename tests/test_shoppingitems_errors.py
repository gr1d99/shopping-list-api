from ddt import ddt, data

from flask import json
from app import messages as msg
from .shopping_base import TestShoppingItemsBaseCase


@ddt
class TestShoppingItemsErrorsCase(TestShoppingItemsBaseCase):
    @data('#$$$', '34256543@#$%', '@#$%^&**&^%$')
    def test_cannot_create_shoppingitem_with_invalid_name(self, name):
        self.register_user()
        login_response = self.login_user()

        # get auth token from login
        auth_token = json.loads(login_response.get_data(as_text=True))['data']['auth_token']

        res_data = {'name': 'Breakfast'}

        # create shoppinglist.
        create_response = self.create_shoppinglist(auth_token, res_data)

        # get shoppinglist id.
        shl_id = json.loads(create_response.get_data(as_text=True))['data']['id']

        # create shoppingitem using auth_token and id of shoppinglist.
        res_data = dict(
            name=name, price=self.testdata_1.price,
            quantity_description=self.testdata_1.quantity_description)

        # create shopping item response.
        shoppingitem_response = self.create_shoppingitem(
            token=auth_token, shl_id=shl_id, data=res_data)
        self.assertStatus(shoppingitem_response, 422)

    def test_user_cannot_add_items_in_non_existing_shoppinglist(self):
        self.register_user()
        login_response = self.login_user()

        # get auth token from login
        auth_token = json.loads(login_response.get_data(as_text=True))['data']['auth_token']

        # create shoppingitem using auth_token and id of shoppinglist.
        res_data = dict(
            name=self.testdata_1.name, price=self.testdata_1.price,
            quantity_description=self.testdata_1.quantity_description)

        # use random shoppinglist ID
        shl_id = 67890

        # create shopping item response.
        shoppingitem_response = self.create_shoppingitem(auth_token, shl_id, res_data)
        res_data = json.loads(shoppingitem_response.get_data(as_text=True))

        self.assert404(shoppingitem_response)
        self.assertTrue(res_data['message'], msg.shoppinglist_not_found)

    def test_cannot_add_items_with_name_that_exist(self):
        self.register_user()
        login_response = self.login_user()

        # get auth token from login
        auth_token = json.loads(login_response.get_data(as_text=True))['data']['auth_token']

        # create shoppinglist.
        res_data = {'name': 'Breakfast'}

        create_response = self.create_shoppinglist(auth_token, res_data)

        # get shoppinglist id.
        shl_id = json.loads(create_response.get_data(as_text=True))['data']['id']

        # create shoppingitem using auth_token and id of shoppinglist.
        res_data = dict(
            name=self.testdata_1.name, price=self.testdata_1.price,
            quantity_description=self.testdata_1.quantity_description)

        # create shopping item response.
        self.create_shoppingitem(auth_token, shl_id, res_data)
        res = self.create_shoppingitem(auth_token, shl_id, res_data)
        self.assertStatus(res, 409)

    def test_user_cannot_view_items_in_shoppinglist_that_does_not_exist(self):
        self.register_user()
        login_res = self.login_user()

        auth_token = json.loads(login_res.get_data(as_text=True))['data']['auth_token']

        # shoppinglist ID.
        shl_id = 12344

        shl_response = self.get_shoppingitems(auth_token, shl_id)
        self.assert404(shl_response)

    def test_cannot_view_specific_shoppingitem_detail_if_shoppinglist_id_does_not_exist(self):
        self.register_user()
        login_response = self.login_user()

        # get auth token from login
        auth_token = json.loads(login_response.get_data(as_text=True))['data']['auth_token']

        # shoppinglist ID goes first.
        shl_id = 1234

        # item ID goes next.
        item_id = 1

        retrieve_resp = self.get_shoppingitem_detail(auth_token, shl_id, item_id)
        retrieved_data = json.loads(retrieve_resp.get_data(as_text=True))

        # assertions.
        self.assert404(retrieve_resp)
        self.assertTrue(retrieved_data['message'] == msg.shoppinglist_not_found)

    def test_cannot_view_specific_shoppingitem_detail_if_shoppingitem_does_not_exist(self):
        self.register_user()
        login_response = self.login_user()

        # get auth token from login
        auth_token = json.loads(login_response.get_data(as_text=True))['data']['auth_token']

        res_data = dict(
            name=self.shopping_list.name,
            description=self.shopping_list.description)

        create_response = self.create_shoppinglist(auth_token, res_data)

        # shoppinglist ID goes first.
        shl_id = json.loads(create_response.get_data(as_text=True))['data']['id']

        # item ID goes next.
        item_id = 1234

        retrieve_resp = self.get_shoppingitem_detail(auth_token, shl_id, item_id)
        retrieved_data = json.loads(retrieve_resp.get_data(as_text=True))

        self.assert404(retrieve_resp)
        self.assertTrue(retrieved_data['message'] == msg.shoppingitem_not_found)

    def test_cannot_update_shoppingitem_with_shoppingitem_that_does_not_exist(self):
        self.register_user()
        login_response = self.login_user()

        # get auth token from login
        auth_token = json.loads(login_response.get_data(as_text=True))['data']['auth_token']

        res_data = dict(
            name=self.shopping_list.name,
            description=self.shopping_list.description)

        create_response = self.create_shoppinglist(auth_token, res_data)

        # get shoppinglist ID.
        shl_id = json.loads(create_response.get_data(as_text=True))['data']['id']

        new_data = {"name": "new shopping item"}

        update_response = self.update_shoppingitem(auth_token, shl_id, 2345678, new_data)
        update_res_data = json.loads(update_response.get_data(as_text=True))

        self.assert404(update_response)
        self.assertEqual(update_res_data['message'], msg.shoppingitem_not_found)

    @data('!@#$%', 'item# 1', 'aaaaaaa')
    def test_cannot_update_shoppingitem_with_invalid_names(self, name):
        self.register_user()
        login_response = self.login_user()

        # get auth token from login
        auth_token = json.loads(login_response.get_data(as_text=True))['data']['auth_token']

        res_data = dict(
            name=self.shopping_list.name,
            description=self.shopping_list.description)

        create_response = self.create_shoppinglist(auth_token, res_data)

        # get shoppinglist ID.
        shl_id = json.loads(create_response.get_data(as_text=True))['data']['id']

        # create shoppingitem.
        item_data = dict(
            name=self.testdata_1.name, price=self.testdata_1.price,
            quantity_description=self.testdata_1.quantity_description)

        item_create_response = self.create_shoppingitem(auth_token, shl_id, item_data)

        # get shoppingitem ID.
        item_id = json.loads(item_create_response.get_data(as_text=True))['data']['id']

        new_data = {
            "name": name, "price": 100,
            "quantity_description": "a dozen",
            "bought": True}

        update_response = self.update_shoppingitem(auth_token, shl_id, item_id, new_data)
        self.assertStatus(update_response, 422)

    def test_user_cannot_delete_all_shoppingitems_using_incorrect_password(self):
        self.register_user()
        login_res = self.login_user()
        auth_token = json.loads(login_res.get_data(as_text=True))['data']['auth_token']

        # create shoppinglist.
        shl_data = dict(
            name=self.shopping_list.name,
            description=self.shopping_list.description)

        shl_response = self.create_shoppinglist(auth_token, shl_data)

        # get shoppinglist ID.
        shl_id = json.loads(shl_response.get_data(as_text=True))['data']['id']

        item_1 = dict(
            name=self.testdata_1.name, price=self.testdata_1.price,
            quantity_description=self.testdata_1.quantity_description)

        item_2 = dict(
            name=self.testdata_2.name, price=self.testdata_2.price,
            quantity_description=self.testdata_2.quantity_description)

        item_3 = dict(
            name=self.testdata_3.name, price=self.testdata_3.price,
            quantity_description=self.testdata_3.quantity_description)

        # create items.
        self.create_shoppingitem(auth_token, shl_id, item_1)
        self.create_shoppingitem(auth_token, shl_id, item_2)
        self.create_shoppingitem(auth_token, shl_id, item_3)

        res = self.delete_shoppingitems(auth_token, shl_id, 'incorrect')
        res_data = json.loads(res.get_data(as_text=True))

        self.assert403(res)
        self.assertEqual(res_data['message'], msg.shoppingitems_not_deleted)

    def test_user_cannot_delete_all_shoppingitems_in_a_non_existing_shoppinglist(self):
        self.register_user()
        login_res = self.login_user()
        auth_token = json.loads(login_res.get_data(as_text=True))['data']['auth_token']

        # random shoppinglist ID.
        shl_id = 12345678

        res = self.delete_shoppingitems(auth_token, shl_id, self.test_user.password)
        res_data = json.loads(res.get_data(as_text=True))

        self.assert404(res)
        self.assertEqual(res_data['message'], msg.shoppinglist_not_found)

    def test_user_cannot_delete_all_shoppingitems_in_an_empty_shoppinglist(self):
        self.register_user()
        login_res = self.login_user()
        auth_token = json.loads(login_res.get_data(as_text=True))['data']['auth_token']

        # create shoppinglist.
        shl_data = dict(
            name=self.shopping_list.name,
            description=self.shopping_list.description)

        shl_response = self.create_shoppinglist(auth_token, shl_data)

        # get shoppinglist ID.
        shl_id = json.loads(shl_response.get_data(as_text=True))['data']['id']

        res = self.delete_shoppingitems(auth_token, shl_id, self.test_user.password)
        res_data = json.loads(res.get_data(as_text=True))

        self.assert404(res)
        self.assertEqual(res_data['message'], msg.shoppinglist_empty)

    def test_cannot_delete_item_if_shoppinglist_does_not_exist(self):
        self.register_user()
        login_res = self.login_user()
        auth_token = json.loads(login_res.get_data(as_text=True))['data']['auth_token']

        shl_id = 123454
        item_id = 1

        del_response = self.delete_shoppingitem(auth_token, shl_id, item_id, 'random')
        del_response_data = json.loads(del_response.get_data(as_text=True))

        self.assert404(del_response)
        self.assertTrue(del_response_data['message'] == msg.shoppinglist_not_found)

    def test_cannot_delete_item_in_not_shoppinglist(self):
        self.register_user()
        login_res = self.login_user()
        auth_token = json.loads(login_res.get_data(as_text=True))['data']['auth_token']

        shl_data = dict(
            name=self.shopping_list.name,
            description=self.shopping_list.description)

        shl_res = self.create_shoppinglist(auth_token, shl_data)

        shl_id = json.loads(shl_res.get_data(as_text=True))['data']['id']
        item_id = 6789

        del_response = self.delete_shoppingitem(auth_token, shl_id, item_id, 'random')
        del_response_data = json.loads(del_response.get_data(as_text=True))

        self.assertFalse(del_response.status_code == 200)
        self.assert404(del_response)
        self.assertEqual(del_response_data['message'], msg.shoppingitem_not_found)

    def test_cannot_delete_item_using_incorrect_name(self):
        self.register_user()
        login_res = self.login_user()
        auth_token = json.loads(login_res.get_data(as_text=True))['data']['auth_token']

        shl_data = dict(
            name=self.shopping_list.name,
            description=self.shopping_list.description)

        shl_response = self.create_shoppinglist(auth_token, shl_data)

        # get shoppinglist ID.
        shl_id = json.loads(shl_response.get_data(as_text=True))['data']['id']

        item_data = dict(
            name=self.testdata_1.name, price=self.testdata_1.price,
            quantity_description=self.testdata_1.quantity_description)

        item_response = self.create_shoppingitem(auth_token, shl_id, item_data)
        item_id = json.loads(item_response.get_data(as_text=True))['data']['id']

        del_response = self.delete_shoppingitem(auth_token, shl_id, item_id, 'incorrect')
        self.assert403(del_response)
