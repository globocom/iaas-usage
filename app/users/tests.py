import unittest
from flask import json
from mock import patch, Mock
from app import app


class UserResourceTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        mock = patch('flask_login.AnonymousUserMixin.is_authenticated').start()
        mock.return_value = True
        mock = patch('flask_login._get_user').start()
        mock.return_value = Mock(username='test@email.com', name='test', picture="gravatar.com/picture.jpg")

    def tearDown(self):
        patch.stopall()

    def test_get_current_user_given_cloudstack_api_error(self):
        list_users_mock = self.mock_cloudstack_list_users({"errortext": "Unable to find user"})

        response = self.app.get('/api/v1/lab/current_user/')

        self.assertEquals(400, response.status_code)
        self.assertEquals("Unable to find user", json.loads(response.data)['message'])
        list_users_mock.listUsers.assert_called_with({'username': 'test@email.com', 'listall': 'true'})

    def test_get_current_user_given_user_not_found(self):
        list_users_mock = self.mock_cloudstack_list_users({})

        response = self.app.get('/api/v1/lab/current_user/')

        self.assertEquals(400, response.status_code)
        self.assertEquals("No user returned for the username test@email.com", json.loads(response.data)['message'])
        list_users_mock.listUsers.assert_called_with({'username': 'test@email.com', 'listall': 'true'})

    def test_get_current_user(self):
        users = {"count": 1, "user": [{
                 "id": "28f40084-2aed-11e5-8fce-76b2dd27c282", "username": "user","accounttype": 1,
                 "domainid": "1", "account": "acc", "firstname": "First", "lastname": "Last"
            }]
        }
        list_users_mock = self.mock_cloudstack_list_users(users)

        response = self.app.get('/api/v1/lab/current_user/')

        self.assertEquals(200, response.status_code)
        expected = {
            "id": "28f40084-2aed-11e5-8fce-76b2dd27c282", "username": "user", "is_admin": True,
            "account_name": "acc", "domain_id": "1","first_name": "First", "last_name": "Last",
            "picture": "gravatar.com/picture.jpg"
        }
        self.assertEquals(expected, json.loads(response.data))
        list_users_mock.listUsers.assert_called_with({'username': 'test@email.com', 'listall': 'true'})

    def mock_cloudstack_list_users(self, users):
        acs_mock = patch('app.users.resource.UserResource.get_cloudstack').start()
        list_users_mock = Mock()
        list_users_mock.listUsers.return_value = users
        acs_mock.return_value = list_users_mock
        return list_users_mock
