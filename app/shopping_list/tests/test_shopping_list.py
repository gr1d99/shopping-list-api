from flask import json
from .base import TestShoppingListBase
from ...messages import \
    (shoppinglist_created, shoppinglist_not_found, shoppinglist_updated, valid_integer_required)
from ...models import ShoppingList, User


class TestShoppingList(TestShoppingListBase):
    """
    Test all CRUD functionalities of shopping list model.
    """

    def test_app(self):
        """
        Test app configuration is set to testing.
        """

        self.assertTrue(self.app.testing)

    def test_create_shopping_list(self):
        """
        Test user can create shopping list.
        """

        # register user
        resgistration_response = self.register_user()

        # assert registration response.
        self.assertStatus(resgistration_response, 201)

        # login created user.
        login_response = self.login_user()

        # assert login response.
        self.assert200(login_response)

        # get auth token
        auth_token = json.loads(login_response.
                                get_data(as_text=True).decode())['auth_token']

        # use auth_token to create shopping list.
        create_shl_response = self.create_shoppinglist(
            token=auth_token, name=self.shopping_list.name
        )

        # assert create shopping list response.
        self.assertStatus(create_shl_response, 201)

        # data returned with create shopping list response.
        create_shl_response_data = json.loads(
            create_shl_response.get_data(as_text=True)
        )

        # query user so that we can confirm owner_id
        user = User.query.filter_by(username=self.user.username).first()

        # query created shopping list.
        shl = ShoppingList.query.filter_by(name=self.shopping_list.name).first()

        # assertions.
        self.assertTrue(create_shl_response_data['status'] == 'success')
        self.assertTrue(create_shl_response_data['message'] == shoppinglist_created)
        self.assertTrue(create_shl_response_data['data']['name'] == shl.name)
        self.assertTrue(create_shl_response_data['data']['created_on'] == shl.timestamp.strftime('%Y-%m-%d %H:%M:%S'))
        self.assertEqual(user.id, shl.owner_id)

    def test_cannot_create_shopping_list_without_authentication(self):
        """
        Test user cannot create shopping list object without auth token.
        """

        create_shl_response = self.create_shoppinglist(
            token='', name=self.shopping_list.name
        )

        self.assertStatus(create_shl_response, 422)

    def test_user_can_view_owned_shopping_lists(self):
        """
        Test user can view his/her own created shopping list.
        """

        # register user
        resgistration_response = self.register_user()

        # assert registration response.
        self.assertStatus(resgistration_response, 201)

        # login created user.
        login_response = self.login_user()

        # assert login response.
        self.assert200(login_response)

        # get auth token
        auth_token = json.loads(login_response.
                                get_data(as_text=True).decode())['auth_token']

        # shopping list name
        shl_list = [
            'first_list', 'second_list', 'third_list'
        ]

        for shl in shl_list:
            # use auth_token to create shopping list.
            self.create_shoppinglist(
                token=auth_token, name=shl
            )

        # make a get request to retrieve shopping list.
        get_shopping_lists_response = self.get_user_shoppinglists(
            token=auth_token
        )

        # data returned with the response
        get_shopping_lists_response_data = json.loads(
            get_shopping_lists_response.get_data(as_text=True).decode()
        )

        # assertions
        self.assertEqual(get_shopping_lists_response_data['status'], 'success')
        self.assertEqual(
            len(get_shopping_lists_response_data['message']['shopping_lists']),
            len(shl_list))

    def test_user_can_get_specific_shopping_list(self):
        """
        Test user can get specific shopping list using its specific id.
        """

        # register user
        resgistration_response = self.register_user()

        # assert registration response.
        self.assertStatus(resgistration_response, 201)

        # login created user.
        login_response = self.login_user()

        # assert login response.
        self.assert200(login_response)

        # get auth token
        auth_token = json.loads(login_response.
                                get_data(as_text=True).decode())['auth_token']

        # shopping list name
        shl_list = [
            'first_list', 'second_list', 'third_list'
        ]

        for shl in shl_list:
            # use auth_token to create shopping list.
            self.create_shoppinglist(
                token=auth_token, name=shl
            )

        # make a get request to retrieve shopping list.
        get_shopping_lists_response = self.get_user_shoppinglists(
            token=auth_token
        )

        # data returned with the response
        get_shopping_lists_response_data = json.loads(
            get_shopping_lists_response.get_data(as_text=True).decode()
        )

        # assertions
        self.assertEqual(get_shopping_lists_response_data['status'], 'success')
        self.assertEqual(
            len(get_shopping_lists_response_data['message']['shopping_lists']),
            len(shl_list))

        # extract shopping list id.
        test_shopping_list_id = get_shopping_lists_response_data['message']['shopping_lists'][0].get('id')

        # query shopping list in db and use it to assert returned response
        shl = ShoppingList.query.filter_by(id=test_shopping_list_id).first()

        # make a GET request to retrieve shopping list detail
        shopping_list_detail_response = self.get_user_shoppinglist_detail(
            token=auth_token, id=test_shopping_list_id)

        # assert responses.
        self.assert200(shopping_list_detail_response)

        # data returned
        shopping_list_detail_response_data = json.loads(
            shopping_list_detail_response.get_data(as_text=True).decode())

        self.assertTrue(
            shopping_list_detail_response_data['status'] == 'success')

        self.assertTrue(
            shopping_list_detail_response_data['message'].get('id') == shl.id
        )

        self.assertTrue(
            shopping_list_detail_response_data['message'].get('owner_id') == shl.owner_id
        )

        self.assertTrue(
            shopping_list_detail_response_data['message'].get('name') == shl.name
        )

        self.assertTrue(
            shopping_list_detail_response_data['message']['created_on'] == shl.timestamp.strftime("%Y-%m-%d %H:%M:%S"))

        self.assertTrue(
            shopping_list_detail_response_data['message']['updated_on'] == shl.updated.strftime("%Y-%m-%d %H:%M:%S"))

    def test_query_with_non_id_that_does_not_exist(self):
        """
        Test error 404 is returned if id used does not exist in user list,
        """

        # register user
        resgistration_response = self.register_user()

        # assert registration response.
        self.assertStatus(resgistration_response, 201)

        # login created user.
        login_response = self.login_user()

        # assert login response.
        self.assert200(login_response)

        # get auth token
        auth_token = json.loads(login_response.
                                get_data(as_text=True).decode())['auth_token']

        # shopping list name
        shl_list = [
            'first_list', 'second_list', 'third_list'
        ]

        for shl in shl_list:
            # use auth_token to create shopping list.
            self.create_shoppinglist(
                token=auth_token, name=shl
            )

        # make a get request to retrieve shopping list.
        get_shopping_lists_response = self.get_user_shoppinglists(
            token=auth_token
        )

        # data returned with the response
        get_shopping_lists_response_data = json.loads(
            get_shopping_lists_response.get_data(as_text=True).decode()
        )

        # assertions
        self.assertEqual(get_shopping_lists_response_data['status'], 'success')
        self.assertEqual(
            len(get_shopping_lists_response_data['message']['shopping_lists']),
            len(shl_list))

        # extract shopping list id.
        test_shoppinglist_id = get_shopping_lists_response_data['message']['shopping_lists'][0].get('id')

        # query shopping list in db and use it to assert returned response
        shl = ShoppingList.query.filter_by(id=test_shoppinglist_id).first()

        # make a GET request to retrieve shopping list detail
        shopping_list_detail_response = self.get_user_shoppinglist_detail(
            token=auth_token, id=20)

        # assert responses.
        self.assert404(shopping_list_detail_response)

        # data returned
        shopping_list_detail_response_data = json.loads(
            shopping_list_detail_response.get_data(as_text=True).decode())

        self.assertTrue(
            shopping_list_detail_response_data['status'] == 'fail')

        self.assertIn(shoppinglist_not_found, shopping_list_detail_response_data['message'])

    def test_user_can_update_shoppinglist(self):

        # register user
        resgistration_response = self.register_user()

        # assert registration response.
        self.assertStatus(resgistration_response, 201)

        # login created user.
        login_response = self.login_user()

        # assert login response.
        self.assert200(login_response)

        # get auth token
        auth_token = json.loads(login_response.
                                get_data(as_text=True).decode())['auth_token']

        # shopping list name
        name = 'myfirst_list'

        # new info
        new_info = dict(
            new_name='updated_first_list'
        )

        # use auth_token to create shopping list.
        create_shoppinglist_response = self.create_shoppinglist(
            token=auth_token, name=name
        )

        # get id of created shoppinglist from response.
        id = json.loads(create_shoppinglist_response.get_data(as_text=True).decode())['data']['id']

        update_shoppinglist_response = self.update_user_shoppinglist\
            (token=auth_token, id=id, new_info=new_info)

        # get data from response
        update_shoppinglist_response_data = json.loads(
            update_shoppinglist_response.get_data(as_text=True).decode()
        )

        # assert response
        self.assert200(update_shoppinglist_response)
        self.assertTrue(
            update_shoppinglist_response_data['status'] == 'success'
        )
        self.assertIn(
            shoppinglist_updated, update_shoppinglist_response_data['message']
        )