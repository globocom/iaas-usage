import unittest
from flask import json
from mock import patch, Mock
from app import app


class VirtualMachinesResourceTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_list_users_given_cloudstack_api_error(self):
        list_users_mock = self.mock_cloudstack_list_vms({"errortext": "Unable to find vms"})

        response = self.app.get('/api/v1/lab/virtual_machine/')

        self.assertEquals(400, response.status_code)
        self.assertEquals("Unable to find vms", json.loads(response.data)['message'])
        list_users_mock.listVirtualMachines.assert_called_with({"listall": "true", "pagesize": "10", "page": "1"})

    def test_list_users_given_custom_paging(self):
        list_users_mock = self.mock_cloudstack_list_vms({"count": 0, "virtualmachine": []})

        response = self.app.get('/api/v1/lab/virtual_machine/', query_string=dict(page_size="5", page="2"))

        self.assertEquals(200, response.status_code)
        list_users_mock.listVirtualMachines.assert_called_with({"listall": "true", "pagesize": "5", "page": "2"})

    def test_list_users_given_invalid_page_size(self):
        response = self.app.get('/api/v1/lab/virtual_machine/', query_string=dict(page_size="invalid", page="2"))

        self.assertEquals(400, response.status_code)
        self.assertEquals("page_size should be an integer", json.loads(response.data)['message'])

    def test_list_users_given_invalid_page(self):
        response = self.app.get('/api/v1/lab/virtual_machine/', query_string=dict(page_size="10", page="invalid"))

        self.assertEquals(400, response.status_code)
        self.assertEquals("page should be an integer", json.loads(response.data)['message'])

    def test_list_users_given_filters_passed(self):
        list_users_mock = self.mock_cloudstack_list_vms({"count": 0, "virtualmachine": []})

        filters = dict(project_id="1", zone_id="1", host_id="1", service_offering_id="1", state="Running")
        response = self.app.get('/api/v1/lab/virtual_machine/', query_string=filters)

        self.assertEquals(200, response.status_code)
        expected_params = {"listall": "true", "pagesize": "10", "page": "1", "projectid": "1",
                           "zoneid": "1", "hostid": "1","serviceofferingid": "1", "state": "Running"}
        list_users_mock.listVirtualMachines.assert_called_with(expected_params)

    def mock_cloudstack_list_vms(self, vms):
        acs_mock = patch('app.resources.virtualmachines.resource.VirtualMachineResource.get_cloudstack').start()
        list_vms_mock = Mock()
        list_vms_mock.listVirtualMachines.return_value = vms
        acs_mock.return_value = list_vms_mock
        return list_vms_mock



