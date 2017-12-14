from ddt import ddt, data

from flask import json
from app.messages import search_not_found
from .shopping_base import TestSearchAndPaginationBaseCase


@ddt
class TestSearchBaseCase(TestSearchAndPaginationBaseCase):
    @data(1, 2, 3)
    def test_can_limit_returned_shoppinglist_objects(self, limit_no: int):
        try:
            int(limit_no)

        except ValueError:
            self.fail('limit_no value `%(no)s` is not an integer' % dict(no=limit_no))

        token = self.init_shoppinglists()
        res = self.get_shoppinglists(token, limit=limit_no)
        data = json.loads(
            res.get_data(as_text=True))

        self.assert200(res)
        self.assertTrue(len(data['data']) == limit_no)

    @data(1, 2, 3, 4)
    def test_can_limit_and_specify_page_of_shoppinglists(self, page_no: int):
        limit_no = 1
        try:
            int(page_no)

        except ValueError:
            self.fail('page_no value `%(no)s` is not an integer' % dict(no=page_no))

        token = self.init_shoppinglists()
        res = self.get_shoppinglists(token, limit=limit_no, page=page_no)
        data = json.loads(
            res.get_data(as_text=True))

        self.assert200(res)
        self.assertEqual(data['current_page'], page_no)
        self.assertTrue(len(data['data']) == limit_no)

    @data(-1, -2, -3, -4)
    def test_cannot_use_negative_page_query_parameter_in_get_shoppinglists(self, val: int):
        try:
            int(val)

        except ValueError:
            self.fail('value should be an integer')

        token = self.init_shoppinglists()
        res = self.get_shoppinglists(token, limit=1, page=val)
        data = json.loads(
            res.get_data(as_text=True))

        self.assertStatus(res, 422)

    @data(-1, -2, -3, -4)
    def test_cannot_use_negative_limit_query_parameter_in_get_shoppinglists(self, val: int):
        try:
            int(val)

        except ValueError:
            self.fail('value should be an integer')

        token = self.init_shoppinglists()
        res = self.get_shoppinglists(token, limit=val, page=1)
        data = json.loads(
            res.get_data(as_text=True))

        self.assertStatus(res, 422)

    @data(1, 2, 3)
    def test_can_limit_returned_shoppingitems_objects(self, limit_no: int):
        try:
            int(limit_no)

        except ValueError:
            self.fail('limit_no value `%(no)s` is not an integer' % dict(no=limit_no))

        page_no = 1
        token, shl_id = self.init_shoppingitems()
        res = self.get_shoppingitems(token, shl_id, limit_no, page_no)
        data = json.loads(
            res.get_data(as_text=True))

        self.assert200(res)
        self.assertEqual(data['current_page'], page_no)
        self.assertTrue(len(data['shopping_items']) == limit_no)

    @data(1, 2, 3, 4)
    def test_can_limit_and_specify_page_of_shoppingitems(self, page_no: int):
        limit_no = 1
        try:
            int(page_no)

        except ValueError:
            self.fail('page_no value `%(no)s` is not an integer' % dict(no=page_no))

        token, shl_id = self.init_shoppingitems()
        res = self.get_shoppingitems(token, shl_id, limit_no, page_no)
        data = json.loads(
            res.get_data(as_text=True))

        self.assert200(res)
        self.assertEqual(data['current_page'], page_no)
        self.assertTrue(len(data['shopping_items']) == limit_no)

    @data(-1, -2, -3, -4)
    def test_cannot_use__negative_page_query_parameter_in_get_shoppingitems(self, page_no: int):
        try:
            int(page_no)

        except ValueError:
            self.fail('value should be an integer')

        limit_no = 1
        token, shl_id = self.init_shoppingitems()
        res = self.get_shoppingitems(token, shl_id, limit_no, page_no)
        data = json.loads(
            res.get_data(as_text=True))

        self.assertStatus(res, 422)

    @data(-1, -2, -3, -4)
    def test_cannot_use_negative_limit_query_parameter_get_shoppingitems(self, limit_no: int):
        try:
            int(limit_no)

        except ValueError:
            self.fail('value should be an integer')

        page_no = 1
        token, shl_id = self.init_shoppingitems()
        res = self.get_shoppingitems(token, shl_id, limit_no, page_no)
        data = json.loads(
            res.get_data(as_text=True))

        self.assertStatus(res, 422)

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
        results = json.loads(
            search_response.get_data(as_text=True))['shoppinglists']

        self.assert200(search_response)

        for r in results:
            self.assertIn(query, ', '.join(r.keys()))

    def test_limit_results(self):
        """
        Test client can limit the number of results returned.
        """

        # search query.
        query = "B"

        # get token and limit value.
        token = self.init_shoppinglists()

        response = self.search_shoppinglist(token, query, 1)

        response_data = json.loads(
            response.get_data(as_text=True))

        # assertions.
        self.assert200(response)
        self.assertTrue(response_data['items_in_page'] == 1)

    @data(1, 2)
    def test_can_pass_limit_and_page_number(self, page_no):
        """
        Test client can supply both limit and page query arguments to get better results.
        """

        # search query.
        query = "B"

        # limit value
        limit = 1

        # get token and limit value.
        token = self.init_shoppinglists()

        response = self.search_shoppinglist(token, query, limit, page_no)

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