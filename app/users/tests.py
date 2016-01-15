import unittest
from flask import json
from mock import patch, Mock
from app import app


class UserResourceTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        mock = patch('flask_login.AnonymousUserMixin.is_authenticated').start()
        mock.return_value = True

    def tearDown(self):
        patch.stopall()

    def test_list_users_given_cloudstack_api_error(self):
        list_users_mock = self.mock_cloudstack_list_users({"errortext": "Unable to find user"})

        username = 'test@email.com'
        response = self.app.get('/api/v1/lab/user/' + username)

        self.assertEquals(400, response.status_code)
        self.assertEquals("Unable to find user", json.loads(response.data)['message'])
        list_users_mock.listUsers.assert_called_with({'username': username})

    def test_list_users_given_empty_user_list(self):
        list_users_mock = self.mock_cloudstack_list_users({})

        username = 'test@email.com'
        response = self.app.get('/api/v1/lab/user/' + username)

        self.assertEquals(200, response.status_code)
        self.assertEquals([], json.loads(response.data))
        list_users_mock.listUsers.assert_called_with({'username': username})

    def test_list_users(self):
        users = {"count": 1, "user": [{
                 "id": "28f40084-2aed-11e5-8fce-76b2dd27c282", "username": "user",
                 "domainid": "1", "account": "acc", "firstname": "First", "lastname": "Last"
            }]
        }
        list_users_mock = self.mock_cloudstack_list_users(users)

        username = 'test@email.com'
        response = self.app.get('/api/v1/lab/user/' + username)

        self.assertEquals(200, response.status_code)
        expected = [{
            "id": "28f40084-2aed-11e5-8fce-76b2dd27c282", "username": "user",
            "account_name": "acc", "domain_id": "1","first_name": "First", "last_name": "Last"
        }]
        self.assertEquals(expected, json.loads(response.data))
        list_users_mock.listUsers.assert_called_with({'username': username})

    def mock_cloudstack_list_users(self, users):
        acs_mock = patch('app.users.resource.UserResource.get_cloudstack').start()
        list_users_mock = Mock()
        list_users_mock.listUsers.return_value = users
        acs_mock.return_value = list_users_mock
        return list_users_mock
