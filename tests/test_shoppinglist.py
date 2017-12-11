from ddt import ddt, data

from flask import json
from .shopping_base import TestShoppingListBaseCase
from app.messages import *
from app.models import ShoppingList, User


@ddt
class TestShoppingListCase(TestShoppingListBaseCase):
    """
    Test all CRUD functionalities of shopping list model.
    """

    def test_app(self):
        """
        Test app configuration is set to testing.
        """

        self.assertTrue(self.app.testing)

    def test_user_can_create_shopping_list(self):
        # register client.
        self.register_user()

        # login created client.
        login_response = self.login_user()

        # get auth token
        auth_token = json.loads(
            login_response.get_data(as_text=True))['data']['auth_token']

        obj = {
            'name': self.shopping_list.name,
            'description': self.shopping_list.description}

        # use auth_token to create shopping list.
        create_shl_response = self.create_shoppinglist(token=auth_token, details=obj)

        # assert create shopping list response.
        self.assertStatus(create_shl_response, 201)

        # data returned with create shopping list response.
        create_shl_response_data = json.loads(
            create_shl_response.get_data(as_text=True)
        )

        # query user so that we can confirm owner_id
        user = User.query.filter_by(username=self.test_user.username).first()

        # query created shopping list.
        shl = ShoppingList.query.filter_by(name=self.shopping_list.name).first()

        # assertions.
        self.assertStatus(create_shl_response, 201)
        self.assertTrue(create_shl_response_data['status'] == 'success')
        self.assertTrue(create_shl_response_data['message'] == shoppinglist_created)
        self.assertTrue(create_shl_response_data['data']['name'] == shl.name)
        self.assertTrue(create_shl_response_data['data']['created_on'] == shl.timestamp.strftime('%Y-%m-%d %H:%M:%S'))
        self.assertEqual(user.id, shl.owner_id)

    def test_user_cannot_create_shoppinglist_with_duplicate_name(self):
        # register user
        self.register_user()

        # login created user.
        login_response = self.login_user()

        # get auth token
        auth_token = json.loads(
            login_response.get_data(as_text=True))['data']['auth_token']

        obj = {
            'name': self.shopping_list.name,
            'description': self.shopping_list.description}

        # create first shopping list.
        self.create_shoppinglist(
            token=auth_token, details=obj)

        second_create_response = self.create_shoppinglist(
            token=auth_token, details=obj)

        # data returned for second response.
        data = json.loads(
            second_create_response.get_data(as_text=True))

        # assertions.
        self.assertStatus(second_create_response, 409)
        self.assertFalse(data['status'] == 'success')
        self.assertEquals(data['message'], shoppinglist_name_exists)

    @data('  spaces', '12344', 'shop1ngl1st', 'f00d', '""""""#$%^&*&^%$#@')
    def test_cannot_create_shoppinglist_with_invalid_names(self, name):
        # register client.
        self.register_user()

        # login created client.
        login_response = self.login_user()

        # get auth token
        auth_token = json.loads(
            login_response.get_data(as_text=True))['data']['auth_token']

        obj = {
            'name': name,
            'description': self.shopping_list.description}

        # use auth_token to create shopping list.
        create_shl_response = self.create_shoppinglist(token=auth_token, details=obj)

        # data returned with create shopping list response.
        data = json.loads(
            create_shl_response.get_data(as_text=True))

        # query shoppinglist obj.
        shl = ShoppingList.query.filter_by(name=name).first()

        self.assertStatus(create_shl_response, 422)
        self.assertFalse(data['status'] == 'success')
        self.assertTrue(data['status'] == 'fail')
        self.assertIsNone(shl)

    def test_user_can_view_all_shoppinglists(self):
        self.register_user()

        # login created user.
        login_response = self.login_user()

        # get auth token
        auth_token = json.loads(login_response.
                                get_data(as_text=True))['data']['auth_token']

        # shopping list name
        shl_list = {
            'first list': 'first shoppinglist',
            'second list': 'second shoppinglist',
            'third list': 'third shoppinglist'}

        for k, v in shl_list.items():
            det = {'name': k, 'description': v}
            self.create_shoppinglist(token=auth_token, details=det)

        # make a get request to retrieve shopping list.
        res = self.get_shoppinglists(
            token=auth_token)

        # data returned with the response
        data = json.loads(
            res.get_data(as_text=True))

        # assertions
        self.assertEqual(data['status'], 'success')
        self.assertEqual(
            len(data['shopping_lists']),
            len(shl_list))

    def test_user_can_retrieve_specific_shoppinglist_using_id(self):
        # register user.
        self.register_user()

        # login created user.
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
        get_shoppinglists_response = self.get_shoppinglists(token=auth_token)

        # data returned with the response
        get_shoppinglists_response_data = json.loads(
            get_shoppinglists_response.get_data(as_text=True))

        # extract shoppinglist id.
        test_shopping_list_id = get_shoppinglists_response_data['shopping_lists'][0].get('id')

        # query shopping list in db and use it to assert returned response
        shl = ShoppingList.query.filter_by(id=test_shopping_list_id).first()

        # make a GET request to retrieve shoppinglist detail.
        response = self.get_shoppinglist_detail(
            token=auth_token, id=test_shopping_list_id)

        # data returned
        response_data = json.loads(response.get_data(as_text=True))

        # assert responses.
        self.assert200(response)
        self.assertFalse(response_data['status'] == 'fail')
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['data']['id'], shl.id)
        self.assertEqual(response_data['data']['name'], shl.name)
        self.assertEqual(response_data['data']['description'], shl.description)
        self.assertEqual(response_data['data']['created_on'], shl.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        self.assertEqual(response_data['data']['updated_on'], shl.updated.strftime("%Y-%m-%d %H:%M:%S"))

    def test_cannot_retrieve_shoppinglist_with_id_that_does_not_exist(self):
        # register user.
        self.register_user()

        # login created user.
        login_response = self.login_user()

        # get auth token
        auth_token = json.loads(
            login_response.get_data(as_text=True))['data']['auth_token']

        # make a GET request to retrieve shoppinglist detail with non existing ID.
        shoppinglist_detail_response = self.get_shoppinglist_detail(
            token=auth_token, id=2000)

        # data returned
        data = json.loads(
            shoppinglist_detail_response.get_data(as_text=True))

        # query db for the shoppinglist object using the random ID.
        obj = ShoppingList.query.filter_by(id=2000).first()

        # assert responses.
        self.assert404(shoppinglist_detail_response)

        self.assertTrue(
            data['status'] == 'fail')

        self.assertEqual(shoppinglist_not_found, data['message'])
        self.assertIsNone(obj)

    def test_user_can_update_shoppinglist(self):
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
            name='updated first list',
            description='this shoppinglist was updated')

        # use auth_token to create shopping list.
        create_response = self.create_shoppinglist(token=auth_token, details=details)

        # get ID of created shoppinglist from response.
        shl_id = json.loads(
            create_response.get_data(as_text=True))['data']['id']

        update_response = self.update_shoppinglist(token=auth_token, id=shl_id, new_info=new_info)

        # query shoppinglist object from database.
        obj = ShoppingList.query.filter_by(id=shl_id).first()

        # get data from response
        response_data = json.loads(update_response.get_data(as_text=True))

        # assert response
        self.assert200(update_response)
        self.assertTrue(response_data['status'] == 'success')
        self.assertEqual(shoppinglist_updated, response_data['message'])
        self.assertIsNotNone(obj)
        self.assertEqual(
            response_data['data']['name'], obj.name)
        self.assertEqual(
            response_data['data']['description'], obj.description)

    def test_user_can_only_update_shoppinglists_that_he_or_she_created(self):
        # register client.
        self.register_user()

        # login created user.
        login_response = self.login_user()

        # get auth token
        auth_token = json.loads(
            login_response.get_data(as_text=True))['data']['auth_token']

        # use random shoppinglist id that we know it does not exist.
        shl_id = 100009
        new_info = {
            'name': 'invalid',
            'description': 'This will not work'}

        update_response = self.update_shoppinglist(
            token=auth_token,
            id=shl_id,
            new_info=new_info)

        # get data from response
        response_data = json.loads(update_response.get_data(as_text=True))

        # assert response
        self.assert404(update_response)
        self.assertTrue(response_data['status'] == 'fail')
        self.assertTrue(response_data['message'] == shoppinglist_not_found)

    def test_can_update_name_only_in_shoppinglist(self):
        # register user.
        self.register_user()
        login_response = self.login_user()

        # get auth token of first user.
        auth_token = json.loads(
            login_response.get_data(as_text=True))['data']['auth_token']

        # new shoppinglists info.
        details = {
            'name': 'New Shoppinglist',
            'description': 'New Shoppinglist description.'}

        new_details = {
            'name': 'Updated Shoppinglist'}

        r = self.create_shoppinglist(token=auth_token, details=details)

        # get shoppinglist obj id.
        shl_id = json.loads(r.get_data(as_text=True))['data']['id']

        response = self.update_shoppinglist(auth_token, shl_id, new_details)

        data = json.loads(
            response.get_data(as_text=True))

        # query bj from db.
        obj = ShoppingList.query.filter_by(name=new_details.get('name')).first()

        # assert response
        self.assert200(response)
        self.assertTrue(data['status'] == 'success')
        self.assertEqual(shoppinglist_updated, data['message'])
        self.assertIsNotNone(obj)
        self.assertEqual(data['data']['name'], obj.name)
        self.assertEqual(data['data']['description'], obj.description)

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
        r = self.create_shoppinglist(token=auth_token, details=first)
        shl_id = json.loads(
            r.get_data(as_text=True))['data']['id']

        response = self.update_shoppinglist(auth_token, shl_id, duplicate)

        data = json.loads(
            response.get_data(as_text=True))

        # query shoppinglist obj.
        obj = ShoppingList.query.filter_by(name=duplicate.get('name')).all()

        # assert response
        self.assertStatus(response, 409)
        self.assertTrue(data['status'] == 'fail')
        self.assertEqual(len(obj), 1)

        # object from db description should be equal to the details used to
        # create the first shoppinglist.
        self.assertTrue(obj[0].description == first.get('description'))

    def test_shoppinglist_not_modified_if_no_data_is_provided(self):
        self.register_user()
        auth_token = json.loads(
            self.login_user().get_data(as_text=True))['data']['auth_token']

        details = dict(
            name='Breakfast',
            description='Next week breakfast')

        create_res = self.create_shoppinglist(auth_token, details)

        shl_id = json.loads(
            create_res.get_data(as_text=True)
        )['data']['id']

        update_res = self.update_shoppinglist(
            auth_token, shl_id, new_info={})

        obj = ShoppingList.query.filter_by(id=shl_id).first()

        data = json.loads(
            update_res.get_data(as_text=True))

        self.assert200(update_res)
        self.assertTrue(data['message'] == shoppinglist_not_updated)
        self.assertEqual(details['name'], obj.name)
        self.assertEqual(details['description'], obj.description)

    def test_user_can_delete_shoppinglist(self):
        self.register_user()

        login_response = self.login_user()

        auth_token = json.loads(
            login_response.get_data(as_text=True))['data']['auth_token']

        # shoppinglist name
        det = {
            'name': 'School'}

        # use auth_token to create shopping list.
        create_response = self.create_shoppinglist(token=auth_token, details=det)

        # get shoppinglist ID.
        shl_id = json.loads(
            create_response.get_data(as_text=True))['data']['id']

        # make DELETE request to server
        r = self.delete_shoppinglist(token=auth_token, id=shl_id)

        # query obj from db.
        obj = ShoppingList.query.filter_by(name=det.get('name')).first()

        # assertions.
        self.assertStatus(r, 200)
        assert json.loads(r.get_data(as_text=True))['message'] == shoppinglist_deleted
        self.assertIsNone(obj)

    def test_cannot_delete_non_existing_shoppinglist(self):
        self.register_user()

        # login created users.
        login_response = self.login_user()

        # get auth tokens.
        token = json.loads(
            login_response.get_data(as_text=True))['data']['auth_token']

        test_id = 1234567654
        # delete shopping list with a random id that does not exist.
        r = self.delete_shoppinglist(token=token, id=test_id)

        data = json.loads(
            r.get_data(as_text=True))

        # query obj from db.
        obj = ShoppingList.query.filter_by(id=test_id).first()

        # assert response.
        self.assertStatus(r, 404)
        self.assertTrue(shoppinglist_not_found == data['message'])
        self.assertIsNone(obj)
