from flask import json
from .base import TestShoppingItemsBase
from ...messages import \
    (shoppingitem_created, shoppingitem_exists, shoppingitem_updated, shoppinglist_not_found)
from ...models import ShoppingItem, ShoppingList


class TestShoppingItems(TestShoppingItemsBase):

    def test_create_shoppingitem(self):
        """
        Test user can create shopping item and add it to shoppinglist.

        Before creating shoppingitem a client needs to be authenticated.
        """

        # register user.
        reg_response = self.register_user()

        # assert registration response.
        self.assertStatus(reg_response, 201)  # created.

        # login user.
        login_response = self.login_user()

        # assert login response.
        self.assertStatus(login_response, 200)

        # get auth token from login
        auth_token = json.loads(
            login_response.get_data(as_text=True).decode())['auth_token']

        # create shoppinglist.
        shoppinglist_response = self.create_shoppinglist(
            token=auth_token, name='Breakfast')

        # assert shoppinglist response.
        self.assertStatus(shoppinglist_response, 201)

        # get shoppinglist id.
        shoppinglistId = json.loads(
            shoppinglist_response.get_data(as_text=True).decode()
        )['data']['id']

        # create shoppingitem using auth_token and id of shoppinglist.
        data = dict(
            name=self.testdata_1.name,
            price=self.testdata_1.price,
            bought=self.testdata_1.bought)

        # shopping item response.
        shoppingitem_response = self.create_shoppingitem(
            token=auth_token, shoppinglistId=shoppinglistId, data=data)

        # shopping item response data.
        shoppingitem_response_data = json.loads(
            shoppingitem_response.get_data(as_text=True).decode())

        # query shoppinglist and shoppingitem from db.
        shoppinglist = ShoppingList.query.filter_by(id=shoppinglistId).first()
        item = ShoppingItem.query.filter_by(name=self.testdata_1.name).first()

        self.assertStatus(shoppingitem_response, 201)
        self.assertTrue(shoppingitem_response_data['status'] == 'success')
        self.assertTrue(shoppingitem_response_data['message'] == shoppingitem_created)

        # assert shoppinglist id with associated shopping list id in shopping item.
        self.assertTrue(shoppinglist.id == item.shoppinglist_id)

    def test_cannot_add_duplicate_shoppingitems(self):
        """
        Test client cannot add two shopping items in the same shoppinglist.
        """

        # register user.
        reg_response = self.register_user()

        # assert registration response.
        self.assertStatus(reg_response, 201)  # created.

        # login user.
        login_response = self.login_user()

        # assert login response.
        self.assertStatus(login_response, 200)

        # get auth token from login
        auth_token = json.loads(
            login_response.get_data(as_text=True).decode())['auth_token']

        # create shoppinglist.
        shoppinglist_response = self.create_shoppinglist(
            token=auth_token, name='Breakfast')

        # get shoppinglist id.
        shoppinglistId = json.loads(
            shoppinglist_response.get_data(as_text=True).decode()
        )['data']['id']

        # create shoppingitem using auth_token and id of shoppinglist.
        data = dict(
            name=self.testdata_1.name,
            price=self.testdata_1.price,
            bought=self.testdata_1.bought)

        # create first shoppingitem.
        self.create_shoppingitem(
            token=auth_token, shoppinglistId=shoppinglistId, data=data)

        # create second shoppingitem
        shoppingitem_response = self.create_shoppingitem(
            token=auth_token, shoppinglistId=shoppinglistId, data=data)

        # shopping item response data.
        shoppingitem_response_data = json.loads(
            shoppingitem_response.get_data(as_text=True).decode())

        # assertions.
        self.assert400(shoppingitem_response)
        self.assertTrue(
            shoppingitem_response_data['status'] == 'fail')

        self.assertTrue(
            shoppingitem_response_data['message'] == shoppingitem_exists)

    def test_shoppingitems_with_similar_names_in_diffent_shoppinglists(self):
        """
        Test different shopping lists can have similar shopping item names.
        """

        # register user.
        reg_response = self.register_user()

        # assert registration response.
        self.assertStatus(reg_response, 201)  # created.

        # login user.
        login_response = self.login_user()

        # assert login response.
        self.assertStatus(login_response, 200)

        # get auth token from login
        auth_token = json.loads(
            login_response.get_data(as_text=True).decode())['auth_token']

        # create shoppinglists.
        shoppinglist_response_1 = self.create_shoppinglist(
            token=auth_token, name='Breakfast')

        shoppinglist_response_2 = self.create_shoppinglist(
            token=auth_token, name='Happy Hour')

        # get shoppinglist id.
        shoppinglistId_1 = json.loads(
            shoppinglist_response_1.get_data(as_text=True).decode()
        )['data']['id']

        shoppinglistId_2 = json.loads(
            shoppinglist_response_2.get_data(as_text=True).decode()
        )['data']['id']

        # create shoppingitem using auth_token and id of shoppinglist.
        data = dict(
            name=self.testdata_1.name,
            price=self.testdata_1.price,
            bought=self.testdata_1.bought)

        # create shoppingitems.
        response_1 = self.create_shoppingitem(
            token=auth_token, shoppinglistId=shoppinglistId_1, data=data)

        response_2 = self.create_shoppingitem(
            token=auth_token, shoppinglistId=shoppinglistId_2, data=data)

        # shopping item response data.
        shoppingitem_response_1_data = json.loads(
            response_1.get_data(as_text=True).decode())

        shoppingitem_response_2_data = json.loads(
            response_2.get_data(as_text=True).decode())

        # assertions.
        self.assertStatus(response_1, 201)
        self.assertStatus(response_2, 201)

        self.assertTrue(
            shoppingitem_response_1_data['status'] == 'success')

        self.assertTrue(
            shoppingitem_response_2_data['status'] == 'success')

    def test_view_shoppingitem(self):
        """
        Test that client can view shopping items.
        :return:
        """

        # register user.
        reg_response = self.register_user()

        # assert registration response.
        self.assertStatus(reg_response, 201)  # created.

        # login user.
        login_response = self.login_user()

        # assert login response.
        self.assertStatus(login_response, 200)

        # get auth token from login
        auth_token = json.loads(
            login_response.get_data(as_text=True).decode())['auth_token']

        # create shoppinglist.
        shoppinglist_response = self.create_shoppinglist(
            token=auth_token, name='Breakfast')

        # get shoppinglist id.
        shoppinglistId = json.loads(
            shoppinglist_response.get_data(as_text=True).decode()
        )['data']['id']

        # create shoppingitem using auth_token and id of shoppinglist.
        data = dict(
            name=self.testdata_1.name,
            price=self.testdata_1.price,
            bought=self.testdata_1.bought)

        data_2 = dict(
            name=self.testdata_2.name,
            price=self.testdata_2.price,
            bought=self.testdata_2.bought)

        self.create_shoppingitem(
            token=auth_token, shoppinglistId=shoppinglistId, data=data)

        self.create_shoppingitem(
            token=auth_token, shoppinglistId=shoppinglistId, data=data_2)

        # retrieve shoppingitems.
        get_response = self.get_shoppingitems(token=auth_token, shoppinglistId=shoppinglistId)

        # response data.
        get_response_data = json.loads(
            get_response.get_data(as_text=True).decode())

        # query shoppinglist
        shoppinglist = ShoppingList.query.filter_by(id=shoppinglistId).first()
        shoppingitems_count = len(shoppinglist.shopping_items.all())

        self.assert200(get_response)
        self.assertTrue(
            get_response_data['status'] == 'success')

        self.assertIn(
            str(shoppingitems_count),  get_response_data['message'])

    def test_update_shoppingitems(self):
        """
        Test client can update shoppingitems.

        For a client to update shoppingitems, he/she will be required to
        use.
            1. Authentication token.
            2. ShoppinglistId.
            3. Shoppingitem Id.
        """

        # register user.
        reg_response = self.register_user()

        # assert registration response.
        self.assertStatus(reg_response, 201)  # created.

        # login user.
        login_response = self.login_user()

        # assert login response.
        self.assertStatus(login_response, 200)

        # get auth token from login
        auth_token = json.loads(
            login_response.get_data(as_text=True).decode())['auth_token']

        # create shoppinglist.
        shoppinglist_response = self.create_shoppinglist(
            token=auth_token, name='Breakfast')

        # get shoppinglist id.
        shoppinglistId = json.loads(
            shoppinglist_response.get_data(as_text=True).decode()
        )['data']['id']

        # create shoppingitem using auth_token and id of shoppinglist.
        data = dict(
            name=self.testdata_1.name,
            price=self.testdata_1.price,
            bought=self.testdata_1.bought)

        # create shoppingitem.
        create_response = self.create_shoppingitem(
            token=auth_token, shoppinglistId=shoppinglistId, data=data)

        # get shoppingitem id.
        shoppingitemId = json.loads(
            create_response.get_data(as_text=True).decode())['data']['id']

        # update shoppingitem.
        new_data = dict(
            name='new shopping item',
            price=1000.00,
            bought=True)

        # get response.
        update_response = self.update_shoppingitem(
            token=auth_token, shoppinglistId=shoppinglistId, shoppingitemId=shoppingitemId, data=new_data)

        # response data.
        update_response_data = json.loads(
            update_response.get_data(as_text=True).decode())

        self.assert200(update_response)
        self.assertTrue(
            update_response_data['status'] == 'success')
        self.assertTrue(
            update_response_data['message'] == shoppingitem_updated)
        self.assertTrue(
            update_response_data['data']['price'] == new_data.get('price'))
        self.assertTrue(
            update_response_data['data']['name'] == new_data.get('name'))

    def test_cannot_update_shoppingitem_in_non_existing_shoppinglist(self):
        """
        Test client cannot update shoppingitem in a non-existing shoppinglist.

        That is if the client should not be allowed to update shoppinglist that
        he/she does not own.
        """

        # register user.
        reg_response = self.register_user()

        # assert registration response.
        self.assertStatus(reg_response, 201)  # created.

        # login user.
        login_response = self.login_user()

        # assert login response.
        self.assertStatus(login_response, 200)

        # get auth token from login
        auth_token = json.loads(
            login_response.get_data(as_text=True).decode())['auth_token']

        # update shoppingitem.
        new_data = dict(
            name='new shopping item',
            price=1000.00,
            bought=True)

        # random shoppinglist id and shoppingitem id
        shoppinglistId = 23
        shoppingitemId = 100

        # get response.
        update_response = self.update_shoppingitem(
            token=auth_token, shoppinglistId=shoppinglistId, shoppingitemId=shoppingitemId, data=new_data)

        # response data.
        update_response_data = json.loads(
            update_response.get_data(as_text=True).decode())

        self.assert404(update_response)
        self.assertTrue(
            update_response_data['status'] == 'fail')
        self.assertTrue(
            update_response_data['message'] == shoppinglist_not_found)