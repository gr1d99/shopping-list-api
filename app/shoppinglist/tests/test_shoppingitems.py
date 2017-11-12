from flask import json
from .base import TestShoppingItemsBase
from ...messages import *
from ...models import ShoppingItem, ShoppingList


class TestShoppingItems(TestShoppingItemsBase):

    def test_create_shoppingitem(self):
        """
        Test user can create shopping item and add it to shoppinglist.

        Before creating shoppingitem a client needs to be authenticated.
        """

        # register user.
        reg_response = self.register_user()

        # login user.
        login_response = self.login_user()

        # get auth token from login
        auth_token = json.loads(
            login_response.get_data(as_text=True))['auth_token']

        # create shoppinglist.
        shoppinglist_response = self.create_shoppinglist(
            token=auth_token, name='Breakfast')

        # get shoppinglist id.
        shoppinglistId = json.loads(
            shoppinglist_response.get_data(as_text=True)
        )['data']['id']

        # create shoppingitem using auth_token and id of shoppinglist.
        data = dict(
            name=self.testdata_1.name,
            price=self.testdata_1.price,
            quantity=self.testdata_1.quantity,
            bought=self.testdata_1.bought)

        # shopping item response.
        shoppingitem_response = self.create_shoppingitem(
            token=auth_token, shoppinglistId=shoppinglistId, data=data)

        # shopping item create response data.
        shoppingitem_response_data = json.loads(
            shoppingitem_response.get_data(as_text=True))

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

        # login user.
        login_response = self.login_user()

        # get auth token from login
        auth_token = json.loads(
            login_response.get_data(as_text=True))['auth_token']

        # create shoppinglist.
        shoppinglist_response = self.create_shoppinglist(
            token=auth_token, name='Breakfast')

        # get shoppinglist id.
        shoppinglistId = json.loads(
            shoppinglist_response.get_data(as_text=True)
        )['data']['id']

        # create shoppingitem using auth_token and id of shoppinglist.
        data = dict(
            name=self.testdata_1.name,
            price=self.testdata_1.price,
            quantity=self.testdata_1.quantity,
            bought=self.testdata_1.bought)

        # create first shoppingitem.
        self.create_shoppingitem(
            token=auth_token, shoppinglistId=shoppinglistId, data=data)

        # create second shoppingitem
        shoppingitem_response = self.create_shoppingitem(
            token=auth_token, shoppinglistId=shoppinglistId, data=data)

        # shopping item response data.
        shoppingitem_response_data = json.loads(
            shoppingitem_response.get_data(as_text=True))

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

        # login user.
        login_response = self.login_user()

        # get auth token from login response.
        auth_token = json.loads(
            login_response.get_data(as_text=True))['auth_token']

        # create shoppinglists.
        shoppinglist_response_1 = self.create_shoppinglist(
            token=auth_token, name='Breakfast')

        shoppinglist_response_2 = self.create_shoppinglist(
            token=auth_token, name='Happy Hour')

        # get shoppinglist id.
        shoppinglistId_1 = json.loads(
            shoppinglist_response_1.get_data(as_text=True)
        )['data']['id']

        shoppinglistId_2 = json.loads(
            shoppinglist_response_2.get_data(as_text=True)
        )['data']['id']

        # create shoppingitem using auth_token and id of shoppinglist.
        data = dict(
            name=self.testdata_1.name,
            price=self.testdata_1.price,
            quantity=self.testdata_1.quantity,
            bought=self.testdata_1.bought)

        # create shoppingitems.
        response_1 = self.create_shoppingitem(
            token=auth_token, shoppinglistId=shoppinglistId_1, data=data)

        response_2 = self.create_shoppingitem(
            token=auth_token, shoppinglistId=shoppinglistId_2, data=data)

        # shopping item response data.
        shoppingitem_response_1_data = json.loads(
            response_1.get_data(as_text=True))

        shoppingitem_response_2_data = json.loads(
            response_2.get_data(as_text=True))

        # assertions.
        self.assertStatus(response_1, 201)
        self.assertStatus(response_2, 201)

        self.assertTrue(
            shoppingitem_response_1_data['status'] == 'success')

        self.assertTrue(
            shoppingitem_response_2_data['status'] == 'success')

    def test_view_shoppingitems(self):
        """
        Test that client can view shopping items.
        """

        # register user.
        reg_response = self.register_user()

        # login client.
        login_response = self.login_user()

        # get auth token from login
        auth_token = json.loads(
            login_response.get_data(as_text=True))['auth_token']

        # create shoppinglist.
        shoppinglist_response = self.create_shoppinglist(
            token=auth_token, name='Breakfast')

        # get shoppinglist id.
        shoppinglistId = json.loads(
            shoppinglist_response.get_data(as_text=True)
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
            get_response.get_data(as_text=True))

        # query shoppinglist
        shoppinglist = ShoppingList.query.filter_by(id=shoppinglistId).first()
        shoppingitems_count = shoppinglist.shopping_items.count()

        self.assert200(get_response)
        self.assertTrue(
            get_response_data['status'] == 'success')
        self.assertTrue(
            get_response_data['message']['total_items'] == shoppingitems_count)

    def test_view_shoppingitem_in_non_existing_shoppinglist(self):
        """
        Test 404 is returned if shoppinglist id is not in user shoppinglists.
        """

        # register user.
        self.register_user()

        # login user.
        login_response = self.login_user()

        # get auth token from login
        auth_token = json.loads(
            login_response.get_data(as_text=True))['auth_token']

        # create shoppinglist.
        self.create_shoppinglist(
            token=auth_token, name='Breakfast')

        # get shoppinglist id.
        shoppinglistId = 120

        # retrieve shoppingitems.
        get_response = self.get_shoppingitems(token=auth_token, shoppinglistId=shoppinglistId)

        # assertions.
        self.assert404(get_response)
        self.assertIn(shoppinglist_not_found, get_response.get_data(as_text=True))

    def test_view_specific_shoppingitem_detail(self):
        """
        Test client should be able to view specific shoppingitem detail using its ID.
        """

        # register client.
        self.register_user()

        # login client.
        login_response = self.login_user()

        # get auth token from login
        auth_token = json.loads(
            login_response.get_data(as_text=True))['auth_token']

        # create shoppinglist.
        create_response = self.create_shoppinglist(
            token=auth_token, name='Breakfast')

        # get shoppinglist ID.
        shoppinglistId = json.loads(
            create_response.get_data(as_text=True))['data']['id']

        # create shoppingitem.
        data = dict(name='Cake', price=1000.90, quantity=2, bought=True)

        shoppingitem_create_response = \
            self.create_shoppingitem(auth_token, shoppinglistId, data=data)

        # get shoppingitem ID.
        shoppingitemId = json.loads(
            shoppingitem_create_response.get_data(as_text=True))['data']['id']

        retrieve_resp = self.get_shoppingitem_detail(
            token=auth_token, shoppinglistId=shoppinglistId, shoppingitemId=shoppingitemId)

        # query shoppingitem directly from db.
        shoppingitem = ShoppingItem.query.filter_by(id=shoppingitemId).first()

        retrieved_data = json.loads(retrieve_resp.get_data(as_text=True))

        # assertions.
        self.assert200(retrieve_resp)
        self.assertTrue(
            retrieved_data['message']['name'] == shoppingitem.name)

    def test_error_if_shoppingitem_does_not_exist(self):
        """
        Test 404 is raised if shoppingitem does not exist in shoppinglist.
        """

        # register client.
        self.register_user()

        # login client.
        login_response = self.login_user()

        # get auth token from login
        auth_token = json.loads(
            login_response.get_data(as_text=True))['auth_token']

        # create shoppinglist.
        create_response = self.create_shoppinglist(
            token=auth_token, name='Breakfast')

        # get shoppinglist ID.
        shoppinglistId = json.loads(
            create_response.get_data(as_text=True))['data']['id']

        # retrieve random shoppingitem.
        shoppingitemId = 1234567

        retrieve_resp = self.get_shoppingitem_detail(
            token=auth_token, shoppinglistId=shoppinglistId, shoppingitemId=shoppingitemId)

        self.assert404(retrieve_resp)

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
        self.register_user()

        # login user.
        login_response = self.login_user()

        # get auth token from login
        auth_token = json.loads(
            login_response.get_data(as_text=True))['auth_token']

        # create shoppinglist.
        shoppinglist_response = self.create_shoppinglist(
            token=auth_token, name='Breakfast')

        # get shoppinglist id.
        shoppinglistId = json.loads(
            shoppinglist_response.get_data(as_text=True)
        )['data']['id']

        # create shoppingitem using auth_token and id of shoppinglist.
        data = dict(
            name=self.testdata_1.name,
            price=self.testdata_1.price,
            quantity=self.testdata_1.quantity,
            bought=self.testdata_1.bought)

        # create shoppingitem.
        create_response = self.create_shoppingitem(
            token=auth_token, shoppinglistId=shoppinglistId, data=data)

        # get shoppingitem id.
        shoppingitemId = json.loads(
            create_response.get_data(as_text=True))['data']['id']

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
            update_response.get_data(as_text=True))

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

        # register client.
        self.register_user()

        # login user.
        login_response = self.login_user()

        # get auth token from login
        auth_token = json.loads(
            login_response.get_data(as_text=True))['auth_token']

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
            token=auth_token, shoppinglistId=shoppinglistId,
            shoppingitemId=shoppingitemId, data=new_data)

        # response data.
        update_response_data = json.loads(update_response.get_data(as_text=True))

        self.assert404(update_response)
        self.assertTrue(update_response_data['status'] == 'fail')
        self.assertTrue(update_response_data['message'] == shoppinglist_not_found)

    def test_cannot_update_not_owned_shoppingitem(self):
        """
        Test client cannot update shoppingitem that is not in owned shoppinglist.
        """

        # register user.
        self.register_user()

        # login user.
        login_response = self.login_user()

        # get auth token from login
        auth_token = json.loads(
            login_response.get_data(as_text=True))['auth_token']

        # create shoppinglist.
        shoppinglist_response = self.create_shoppinglist(
            token=auth_token, name='Breakfast')

        # get shoppinglist id.
        shoppinglistId = json.loads(
            shoppinglist_response.get_data(as_text=True)
        )['data']['id']

        # create shoppingitem using auth_token and ID of shoppinglist.
        data = dict(
            name=self.testdata_1.name,
            price=self.testdata_1.price,
            bought=self.testdata_1.bought)

        # create shoppingitem.
        create_response = self.create_shoppingitem(
            token=auth_token, shoppinglistId=shoppinglistId, data=data)

        # use random shoppingitem ID
        shoppingitemId = 100

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
            update_response.get_data(as_text=True))

        self.assert404(update_response)
        self.assertTrue(update_response_data['status'] == 'fail')
        self.assertTrue(
            update_response_data['message'] == shoppingitem_not_found)

    def test_cannot_update_shoppingitem_with_existing_name(self):
        """
        Test client should not update shopping item name that is used by another shoppingitem.
        """

        # register client.
        self.register_user()

        # login client.
        login_response = self.login_user()

        # get auth token from login
        auth_token = json.loads(
            login_response.get_data(as_text=True))['auth_token']

        # create shoppinglist.
        shoppinglist_response = self.create_shoppinglist(
            token=auth_token, name='Breakfast')

        # get shoppinglist id.
        shoppinglistId = json.loads(
            shoppinglist_response.get_data(as_text=True)
        )['data']['id']

        # create shoppingitems using auth_token and id of shoppinglist.
        data_1 = dict(
            name=self.testdata_1.name,
            price=self.testdata_1.price,
            quantity=self.testdata_1.quantity,
            bought=self.testdata_1.bought)

        data_2 = dict(
            name=self.testdata_2.name,
            price=self.testdata_2.price,
            quantity=self.testdata_2.quantity,
            bought=self.testdata_2.bought)

        # create shoppingitems.
        self.create_shoppingitem(
            token=auth_token, shoppinglistId=shoppinglistId, data=data_1)

        # create another shoppingitem.
        item_2_response = self.create_shoppingitem(
            token=auth_token, shoppinglistId=shoppinglistId, data=data_2)

        # get shoppingitem id of item 2.
        shoppingitemId = json.loads(
            item_2_response.get_data(as_text=True))['data']['id']

        # update shoppingitem using item 1 name.
        new_data = dict(
            name=self.testdata_1.name,
            price=1000.00,
            quantity=12,
            bought=True)

        # get response.
        update_response = self.update_shoppingitem(
            token=auth_token, shoppinglistId=shoppinglistId,
            shoppingitemId=shoppingitemId, data=new_data)

        # response data.
        update_response_data = json.loads(
            update_response.get_data(as_text=True))

        # assertions.
        self.assert400(update_response)
        self.assertTrue(update_response_data['status'] == 'fail')
        self.assertTrue(update_response_data['message'] == shoppingitem_exists)

    def test_cannot_update_shoppingitem_name_with_characters_less_than_three(self):
        """
        Test client should not update shoppingitem name with a name that
        has a minimum of three characters.
        """

        # register client.
        self.register_user()

        # login user.
        login_response = self.login_user()

        # get auth token from login
        auth_token = json.loads(
            login_response.get_data(as_text=True))['auth_token']

        # create shoppinglist.
        shoppinglist_response = self.create_shoppinglist(
            token=auth_token, name='Breakfast')

        # get shoppinglist id.
        shoppinglistId = json.loads(
            shoppinglist_response.get_data(as_text=True)
        )['data']['id']

        # create shoppingitem using auth_token and id of shoppinglist.
        data = dict(
            name=self.testdata_1.name,
            price=self.testdata_1.price,
            quantity=self.testdata_1.quantity,
            bought=self.testdata_1.bought)

        # create shoppingitem.
        create_response = self.create_shoppingitem(
            token=auth_token, shoppinglistId=shoppinglistId, data=data)

        # get shoppingitem id.
        shoppingitemId = json.loads(
            create_response.get_data(as_text=True))['data']['id']

        # update shoppingitem with a short name.
        new_data = dict(
            name='nw',  # <- short name
            price=1000.00,
            quantity=12,
            bought=True)

        # get response.
        update_response = self.update_shoppingitem(
            token=auth_token, shoppinglistId=shoppinglistId,
            shoppingitemId=shoppingitemId, data=new_data)

        # response data.
        update_response_data = json.loads(
            update_response.get_data(as_text=True))

        self.assertStatus(update_response, 422)
        self.assertTrue(
            update_response_data['status'] == 'fail')
        self.assertIn('Shorter than minimum length 3.', update_response_data['message']['name'])

    def test_delete_shoppingitem(self):
        """
        Test client should delete shoppingitem successfully.
        """

        # register client.
        self.register_user()

        # login client.
        login_response = self.login_user()

        # get auth token from login
        auth_token = json.loads(
            login_response.get_data(as_text=True))['auth_token']

        # create shoppinglist.
        shoppinglist_response = self.create_shoppinglist(
            token=auth_token, name='Breakfast')

        # get shoppinglist id.
        shoppinglistId = json.loads(
            shoppinglist_response.get_data(as_text=True)
        )['data']['id']

        # create shoppingitem using auth_token and id of shoppinglist.
        data = dict(
            name=self.testdata_1.name,
            price=self.testdata_1.price,
            quantity=self.testdata_1.quantity,
            bought=self.testdata_1.bought)

        # create shoppingitem.
        create_response = self.create_shoppingitem(
            token=auth_token, shoppinglistId=shoppinglistId, data=data)

        # get shoppingitem id.
        shoppingitemId = json.loads(
            create_response.get_data(as_text=True))['data']['id']

        # make delete request.
        delete_response = self.delete_shoppingitem(token=auth_token,
                                                   shoppinglistId=shoppinglistId,
                                                   shoppingitemId=shoppingitemId)

        # assertions.
        self.assertStatus(delete_response, 204)

    def test_cannot_delete_item_if_shoppinglist_does_not_exist(self):
        """
        Test client should get 404 error if shoppinglist does not exist in
        his/her shoppinglists.
        """

        # register client.
        self.register_user()

        # login user.
        login_response = self.login_user()

        # get auth token from login
        auth_token = json.loads(
            login_response.get_data(as_text=True))['auth_token']

        # use random id that does not exist in client shopping lists.

        # make delete request.
        delete_response = self.delete_shoppingitem(token=auth_token,
                                                   shoppinglistId=134,
                                                   shoppingitemId=1)

        # assertions.
        self.assert404(delete_response)
        self.assertIn(shoppinglist_not_found, delete_response.get_data(as_text=True))

    def test_cannot_delete_item_in_not_shoppinglist(self):
        """
        Test client should get 404 error if shoppingitem id does not exist in
        his/her shoppinglists.
        """

        # register client.
        reg_response = self.register_user()

        # login client.
        login_response = self.login_user()

        # get auth token from login
        auth_token = json.loads(
            login_response.get_data(as_text=True))['auth_token']

        # create shoppinglist.
        shoppinglist_response = self.create_shoppinglist(
            token=auth_token, name='Breakfast')

        # get shoppinglist id.
        shoppinglistId = json.loads(
            shoppinglist_response.get_data(as_text=True)
        )['data']['id']

        # make delete request.
        delete_response = self.delete_shoppingitem(token=auth_token,
                                                   shoppinglistId=shoppinglistId,
                                                   shoppingitemId=807)

        # assertions.
        self.assert404(delete_response)
        self.assertIn(shoppingitem_not_found, delete_response.get_data(as_text=True))
