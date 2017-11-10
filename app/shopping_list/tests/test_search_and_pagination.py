from flask import json
from app.messages import search_not_found
from .base import TestSearchAndPagination


class TestSearch(TestSearchAndPagination):
    def test_search(self):
        """
        Test results returned contains query keyword
        """

        # get client auth_token.
        client_token = self.init()

        # search query.
        query = "B"

        search_response = self.search_shoppinglist(
            token=client_token, keyword=query)

        # get data.
        results = json.loads(
            search_response.get_data(as_text=True))['results']

        self.assert200(search_response)

        for r in results:
            self.assertIn(query, r)

    def test_limit_results(self):
        """
        Test client can limit the number of results returned.
        """

        # search query.
        query = "B"

        # get token and limit value.
        token, limit = self.init(use_limit=True, limit=1)

        response = self.search_shoppinglist(
            token=token, keyword=query, limit=limit)

        response_data = json.loads(
            response.get_data(as_text=True))

        # assertions.
        self.assert200(response)
        self.assertTrue(response_data['items_in_page'] == limit)

    def test_can_pass_limit_and_page_number(self):
        """
        Test client can supply both limit and page query arguments to get better results.
        """

        # search query.
        query = "B"

        # get token and limit value.
        token, limit, page = self.init(use_limit=True, limit=1, per_page=True, page=2)

        response = self.search_shoppinglist(
            token=token, keyword=query, limit=limit, page=page)

        response_data = json.loads(
            response.get_data(as_text=True))

        # assertions.
        self.assert200(response)
        self.assertTrue(response_data['items_in_page'] == limit)

    def test_cannot_search_with_empty_query(self):
        """
        Test 400 returned if query value is empty.
        """

        # get client auth_token.
        client_token = self.init()

        # search query.
        query = ""

        search_response = self.search_shoppinglist(
            token=client_token, keyword=query)

        self.assert400(search_response)

    def test_when_results_not_found(self):
        """
        Client should get a message if search did not match any shoppinglist.
        """

        # get client auth_token.
        client_token = self.init()

        # search query.
        query = "i dont exist"

        search_response = self.search_shoppinglist(
            token=client_token, keyword=query)

        # get data.
        results = json.loads(
            search_response.get_data(as_text=True))

        self.assert200(search_response)
        self.assertIn(search_not_found, results['message'])