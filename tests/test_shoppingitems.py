from flask import json
from app import messages as msg
from app.models import ShoppingItem, ShoppingList
from .shopping_base import TestShoppingItemsBaseCase


class TestShoppingItemsCase(TestShoppingItemsBaseCase):
    def test_user_can_add_shoppingitem(self):
        self.register_user()

        # login user.
        login_response = self.login_user()

        # get auth token from login
        auth_token = json.loads(login_response.get_data(as_text=True))['data']['auth_token']

        # create shoppinglist.
        data = {'name': 'Breakfast'}

        create_response = self.create_shoppinglist(token=auth_token, details=data)

        # get shoppinglist id.
        shl_id = json.loads(
            create_response.get_data(as_text=True))['data']['id']

        # create shoppingitem using auth_token and id of shoppinglist.
        data = dict(
            name=self.testdata_1.name, price=self.testdata_1.price,
            quantity_description=self.testdata_1.quantity_description)

        # create shopping item response.
        shoppingitem_response = self.create_shoppingitem(
            token=auth_token, shl_id=shl_id, data=data)

        # create shoppingitem response data.
        shoppingitem_response_data = json.loads(shoppingitem_response.get_data(as_text=True))

        # query shoppinglist and shoppingitem from db.
        shoppinglist = ShoppingList.query.filter_by(id=shl_id).first()
        item = ShoppingItem.query.filter_by(name=self.testdata_1.name).first()

        self.assertStatus(shoppingitem_response, 201)
        self.assertTrue(shoppingitem_response_data['message'] == msg.shoppingitem_created)

        # assert shoppinglist id with associated shopping list id in shopping item.
        self.assertTrue(shoppinglist.id == item.shoppinglist_id)

    def test_can_view_all_shoppingitems(self):
        self.register_user()
        login_res = self.login_user()

        auth_token = json.loads(login_res.get_data(as_text=True))['data']['auth_token']

        data = {
            'name': 'Lunch',
            'description': 'Lunch shoppinglist'}

        r = self.create_shoppinglist(auth_token, data)

        # shoppinglist ID.
        shl_id = json.loads(r.get_data(as_text=True))['data']['id']

        for item in self.shoppingitems:
            item_det = {
                'name': item.name, 'price': item.price,
                'quantity_description': item.quantity_description}
            self.create_shoppingitem(auth_token, shl_id, item_det)

        shl_response = self.get_shoppingitems(auth_token, shl_id)
        data = json.loads(shl_response.get_data(as_text=True))

        self.assert200(shl_response)

        # same number of items should be equal to test data items.
        self.assertEqual(len(data['shopping_items']), len(self.shoppingitems))

    def test_view_specific_shoppingitem_detail(self):
        self.register_user()
        login_response = self.login_user()

        # get auth token from login
        auth_token = json.loads(login_response.get_data(as_text=True))['data']['auth_token']

        data = dict(
            name=self.shopping_list.name,
            description=self.shopping_list.description)

        create_response = self.create_shoppinglist(auth_token, data)

        # get shoppinglist ID.
        shl_id = json.loads(create_response.get_data(as_text=True))['data']['id']

        # create shoppingitem.
        item_data = dict(
            name=self.testdata_1.name, price=self.testdata_1.price,
            quantity_description=self.testdata_1.quantity_description)

        item_create_response = self.create_shoppingitem(auth_token, shl_id, item_data)

        # get shoppingitem ID.
        item_id = json.loads(item_create_response.get_data(as_text=True))['data']['id']

        retrieve_resp = self.get_shoppingitem_detail(auth_token, shl_id, item_id)

        # query shoppingitem directly from db.
        shoppingitem = ShoppingItem.query.filter_by(id=item_id).first()

        retrieved_data = json.loads(retrieve_resp.get_data(as_text=True))

        # assertions.
        self.assert200(retrieve_resp)
        self.assertEqual(retrieved_data['data']['id'], shoppingitem.id)
        self.assertEqual(retrieved_data['data']['name'], shoppingitem.name)

    def test_can_update_shoppingitem(self):
        self.register_user()
        login_response = self.login_user()

        # get auth token from login
        auth_token = json.loads(login_response.get_data(as_text=True))['data']['auth_token']

        data = dict(
            name=self.shopping_list.name,
            description=self.shopping_list.description)

        create_response = self.create_shoppinglist(auth_token, data)

        # get shoppinglist ID.
        shl_id = json.loads(create_response.get_data(as_text=True))['data']['id']

        # create shoppingitem.
        item_data = dict(
            name=self.testdata_1.name, price=self.testdata_1.price,
            quantity_description=self.testdata_1.quantity_description)

        item_create_response = self.create_shoppingitem(auth_token, shl_id, item_data)

        # get shoppingitem ID.
        item_id = json.loads(
            item_create_response.get_data(as_text=True))['data']['id']

        new_data = {
            "name": "new shopping item", "price": 100,
            "quantity_description": "a dozen",
            "bought": 1}

        update_response = self.update_shoppingitem(auth_token, shl_id, item_id, new_data)
        update_res_data = json.loads(update_response.get_data(as_text=True))

        item = ShoppingItem.query.filter_by(id=item_id).first()

        self.assert200(update_response)
        self.assertIn(msg.shoppingitem_updated, update_response.get_data(as_text=True))
        self.assertIsNotNone(item)
        self.assertIs(item.id, update_res_data['data']['id'])
        self.assertEqual(new_data['name'], update_res_data['data']['name'])
        self.assertFalse(new_data['name'] == self.testdata_1.name)
        self.assertTrue(update_res_data['data']['price'] == new_data['price'])
        self.assertTrue(update_res_data['data']['quantity_description']
                        == new_data['quantity_description'])
        self.assertTrue(update_res_data['data']['bought'] == new_data['bought'])

    def test_update_shoppingitem_with_shoppinglist_id_that_does_not_exist(self):
        self.register_user()
        login_response = self.login_user()

        # get auth token from login
        auth_token = json.loads(login_response.get_data(as_text=True))['data']['auth_token']

        item_data = dict(
            name=self.testdata_1.name, price=self.testdata_1.price,
            quantity_description=self.testdata_1.quantity_description)

        res = self.update_shoppingitem(auth_token, 12345, 1, item_data)
        response_data = json.loads(res.get_data(as_text=True))

        self.assert404(res)
        self.assertEqual(response_data['message'], msg.shoppinglist_not_found)

    def test_user_can_delete_all_shoppingitems(self):
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

        res = self.delete_shoppingitems(auth_token, shl_id, self.test_user.password)
        res_data = json.loads(res.get_data(as_text=True))

        self.assert200(res)
        self.assertEqual(res_data['message'], msg.shoppingitems_deleted)

    def test_delete_shoppingitem(self):
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

        del_response = self.delete_shoppingitem(auth_token, shl_id, item_id, self.testdata_1.name)
        del_response_data = json.loads(del_response.get_data(as_text=True))

        self.assert200(del_response)
        self.assertTrue(del_response_data['message'] == msg.shoppingitem_deleted)
