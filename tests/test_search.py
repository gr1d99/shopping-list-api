
from flask import json
from app.messages import search_not_found
from .shopping_base import TestSearchAndPaginationBaseCase


class TestSearchCase(TestSearchAndPaginationBaseCase):
    def test_search(self):
        """
        Test results returned contains query keyword
        """

        # get client auth_token.
        client_token = self.init_shoppinglists()

        # search query.
        query = "B"

        search_response = self.search_shoppinglist(client_token, query)

        # get data.
        results = [
            shl.get('name', None) for shl in json.loads(
                search_response.get_data(as_text=True))['shoppinglists']]

        self.assert200(search_response)

        for res in results:
            assert query in res

    def test_cannot_search_with_empty_query(self):
        """
        Test 400 returned if query value is empty.
        """

        # get client auth_token.
        client_token = self.init_shoppinglists()

        # search query.
        query = ""

        response = self.search_shoppinglist(client_token, query)
        message = json.loads(response.get_data(as_text=True)).get('message', '')

        self.assertStatus(response, 422)
        self.assertEqual(message, 'please provide query value')

    def test_when_results_not_found(self):
        """
        Client should get a message if search did not match any shoppinglist.
        """

        # get client auth_token.
        client_token = self.init_shoppinglists()

        # search query.
        query = "i dont exist"

        search_response = self.search_shoppinglist(client_token, keyword=query)

        # get data.
        results = json.loads(
            search_response.get_data(as_text=True))

        self.assert200(search_response)
        self.assertIn(search_not_found, results['message'])
