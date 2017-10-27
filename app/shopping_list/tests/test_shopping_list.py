from flask import json
from app.messages import shopping_list_created
from .base import TestShoppingListBase
from ...models import ShoppingList


class TestShoppingList(TestShoppingListBase):
    """
    Test all CRUD functionalities of shopping list model.
    """

    def test_app(self):
        """
        Test app configuration is set to testing.
        :return:
        """

        self.assertTrue(self.app.testing)

    def test_create_shopping_list(self):
        """
        Test user can create shopping list.
        """

        # register user
        resgistration_response = self.register_user(
            username=self.user.username,
            password=self.user.password,
            email=self.user.email
        )

        # assert registration response.
        self.assertStatus(resgistration_response, 201)

        # login created user.
        login_response = self.login_user(
            username=self.user.username,
            password=self.user.password
        )

        # assert login response.
        self.assert200(login_response)

        # get auth token
        auth_token = json.loads(login_response.
                                get_data(as_text=True).decode())['auth_token']

        # use auth_token to create shopping list.
        create_shl_response = self.create_shopping_list(
            token=auth_token, name=self.shopping_list.name
        )

        # assert create shopping list response.
        self.assertStatus(create_shl_response, 201)

        # data returned with create shopping list response.
        create_shl_response_data = json.loads(
            create_shl_response.get_data(as_text=True)
        )

        # query created shopping list.
        shl = ShoppingList.query.filter_by(name=self.shopping_list.name).first()

        # assertions.
        self.assertTrue(create_shl_response_data['status'] == 'success')
        self.assertTrue(create_shl_response_data['message'] == shopping_list_created)
        self.assertTrue(create_shl_response_data['data']['name'] == shl.name)
        self.assertTrue(create_shl_response_data['data']['created_on'] == shl.timestamp.strftime('%Y-%m-%d'))
