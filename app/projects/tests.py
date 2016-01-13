import unittest
from flask import json
from mock import patch, Mock
from app import app


class ProjectResourceTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_list_projects_given_empty_account_name(self):
        query = dict(domain_id='28f40084-2aed-11e5-8fce-76b2dd27c282')
        response = self.app.get('/api/v1/lab/project/', query_string=query)

        self.assertEquals(400, response.status_code)
        self.assertEquals("account_name must be informed", json.loads(response.data)['message'])

    def test_list_projects_given_empty_domain_id(self):
        response = self.app.get('/api/v1/lab/project/', query_string=dict(account_name='account'))

        self.assertEquals(400, response.status_code)
        self.assertEquals("domain_id must be informed", json.loads(response.data)['message'])

    def test_list_projects_given_cloudstack_api_error(self):
        list_projects_mock = self.mock_cloudstack_list_project({"errortext": "Unable to find account"})

        request = dict(account_name="account", domain_id='28f40084-2aed-11e5-8fce-76b2dd27c282')
        response = self.app.get('/api/v1/lab/project/', query_string=request)

        self.assertEquals(400, response.status_code)
        self.assertEquals("Unable to find account", json.loads(response.data)['message'])
        expected_resp = {'simple': 'true', 'account': request['account_name'],
                         'domainid': request['domain_id'], 'listall': 'true'}
        list_projects_mock.listProjects.assert_called_with(expected_resp)

    def test_list_projects_given_empty_project_list(self):
        list_projects_mock = self.mock_cloudstack_list_project({})

        request = dict(account_name="account", domain_id='28f40084-2aed-11e5-8fce-76b2dd27c282')
        response = self.app.get('/api/v1/lab/project/', query_string=request)

        self.assertEquals(200, response.status_code)
        expected_resp = {'simple': 'true', 'account': request['account_name'],
                         'domainid': request['domain_id'], 'listall': 'true'}
        list_projects_mock.listProjects.assert_called_with(expected_resp)

    def test_list_projects(self):
        mock_resp = {"count": 1, "project": [
             {"id": "28f40084-2aed-11e5-8fce-76b2dd27c282", "name": "project", "vmtotal": 1}]
        }
        list_projects_mock = self.mock_cloudstack_list_project(mock_resp)

        request = dict(account_name="account", domain_id='28f40084-2aed-11e5-8fce-76b2dd27c282')
        response = self.app.get('/api/v1/lab/project/', query_string=request)

        self.assertEquals(200, response.status_code)
        expected_resp = [{"id": "28f40084-2aed-11e5-8fce-76b2dd27c282", "name": "project", "vm_count": 1}]
        self.assertEquals(expected_resp, json.loads(response.data))
        expected_resp = {'simple': 'true', 'account': request['account_name'],
                         'domainid': request['domain_id'], 'listall': 'true'}
        list_projects_mock.listProjects.assert_called_with(expected_resp)

    def mock_cloudstack_list_project(self, projects):
        acs_mock = patch('app.projects.resource.ProjectResource.get_cloudstack').start()
        list_projects_mock = Mock()
        list_projects_mock.listProjects.return_value = projects
        acs_mock.return_value = list_projects_mock
        return list_projects_mock
