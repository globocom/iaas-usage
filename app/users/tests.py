import unittest
from flask import json
from mock import patch, Mock
from app import app


class UserResourceTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_list_users_given_cloudstack_api_error(self):
        list_users_mock = self.mock_cloudstack_list_users({"errortext": "Unable to find user"})

        id = '28f40084-2aed-11e5-8fce-76b2dd27c282'
        response = self.app.get('/api/v1/lab/user/' + id)

        self.assertEquals(400, response.status_code)
        self.assertEquals("Unable to find user", json.loads(response.data)['message'])
        list_users_mock.listUsers.assert_called_with({'id': id})

    def test_list_users_given_empty_user_list(self):
        list_users_mock = self.mock_cloudstack_list_users({})

        id = '28f40084-2aed-11e5-8fce-76b2dd27c282'
        response = self.app.get('/api/v1/lab/user/' + id)

        self.assertEquals(200, response.status_code)
        self.assertEquals([], json.loads(response.data))
        list_users_mock.listUsers.assert_called_with({'id': id})

    def test_list_users(self):
        users = {"count": 1, "user": [{"id": "28f40084-2aed-11e5-8fce-76b2dd27c282", "username": "user", "domainid": "1", "account" : "acc"}]}
        list_users_mock = self.mock_cloudstack_list_users(users)

        id = '28f40084-2aed-11e5-8fce-76b2dd27c282'
        response = self.app.get('/api/v1/lab/user/' + id)

        self.assertEquals(200, response.status_code)
        self.assertEquals([{"id":"28f40084-2aed-11e5-8fce-76b2dd27c282", "username":"user", "account_name": "acc", "domain_id": "1"}], json.loads(response.data))
        list_users_mock.listUsers.assert_called_with({'id': id})

    def mock_cloudstack_list_users(self, users):
        acs_mock = patch('app.users.resource.UserResource.get_cloudstack').start()
        list_users_mock = Mock()
        list_users_mock.listUsers.return_value = users
        acs_mock.return_value = list_users_mock
        return list_users_mock


