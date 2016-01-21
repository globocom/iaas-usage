import unittest
from flask import json
from mock import patch, Mock
from app import app


class VirtualMachinesResourceTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        mock = patch('flask_login.AnonymousUserMixin.is_authenticated').start()
        mock.return_value = True

    def tearDown(self):
        patch.stopall()

    def test_list_users_given_cloudstack_api_error(self):
        list_users_mock = self.mock_cloudstack_list_vms({"errortext": "Unable to find vms"})

        response = self.app.get('/api/v1/lab/virtual_machine/')

        self.assertEquals(400, response.status_code)
        self.assertEquals("Unable to find vms", json.loads(response.data)['message'])
        list_users_mock.listVirtualMachines.assert_called_with({"listall": "true", "simple": "true", "pagesize": "10", "page": "1"})

    def test_list_users_given_custom_paging(self):
        list_users_mock = self.mock_cloudstack_list_vms({"count": 0, "virtualmachine": []})

        response = self.app.get('/api/v1/lab/virtual_machine/', query_string=dict(page_size="5", page="2"))

        self.assertEquals(200, response.status_code)
        list_users_mock.listVirtualMachines.assert_called_with({"listall": "true", "simple": "true", "pagesize": "5", "page": "2"})

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
        expected_params = {"listall": "true", "simple": "true", "pagesize": "10", "page": "1", "projectid": "1",
                           "zoneid": "1", "hostid": "1","serviceofferingid": "1", "state": "Running"}
        list_users_mock.listVirtualMachines.assert_called_with(expected_params)

    def mock_cloudstack_list_vms(self, vms):
        acs_mock = patch('app.virtualmachines.resource.VirtualMachineResource.get_cloudstack').start()
        list_vms_mock = Mock()
        list_vms_mock.listVirtualMachines.return_value = vms
        acs_mock.return_value = list_vms_mock
        return list_vms_mock


class VmCountResourceTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        mock = patch('flask_login.AnonymousUserMixin.is_authenticated').start()
        mock.return_value = True

    def tearDown(self):
        patch.stopall()

    def test_list_vm_count_without_project_id(self):
        response = self.app.get('/api/v1/lab/vm_count/')

        self.assertEquals(400, response.status_code)
        self.assertEquals("project_id must be informed", json.loads(response.data)['message'])

    def test_list_vm_count_given_different_vms(self):
        vm1 = {'state': 'Stopped', 'serviceofferingname': 'Small', 'hostname': 'host_a', 'zonename': 'zone_a', 'haenable': 'true'}
        vm2 = {'state': 'Running', 'serviceofferingname': 'Large', 'hostname': 'host_b', 'zonename': 'zone_b', 'haenable': 'false'}
        self.mock_cloudstack_list_vms({"count": 0, "virtualmachine": [vm1, vm2]})

        response = self.app.get('/api/v1/lab/vm_count/', query_string=dict(project_id='28f40084'))
        vm_count = json.loads(response.data)
        self.assertEquals(200, response.status_code)
        self.assertEquals(1, vm_count['state']['Stopped'])
        self.assertEquals(1, vm_count['state']['Running'])
        self.assertEquals(1, vm_count['serviceofferingname']['small'])
        self.assertEquals(1, vm_count['serviceofferingname']['large'])
        self.assertEquals(1, vm_count['hostname']['host_a'])
        self.assertEquals(1, vm_count['hostname']['host_b'])
        self.assertEquals(1, vm_count['zonename']['zone_a'])
        self.assertEquals(1, vm_count['zonename']['zone_b'])
        self.assertEquals(1, vm_count['haenable']['true'])
        self.assertEquals(1, vm_count['haenable']['false'])

    def test_list_vm_count_given_two_equal_vms(self):
        vm1 = {'state': 'Stopped', 'serviceofferingname': 'Small', 'hostname': 'host_a', 'zonename': 'zone_a', 'haenable': 'true'}
        self.mock_cloudstack_list_vms({"count": 0, "virtualmachine": [vm1, vm1]})

        response = self.app.get('/api/v1/lab/vm_count/', query_string=dict(project_id='28f40084'))
        vm_count = json.loads(response.data)
        self.assertEquals(200, response.status_code)
        self.assertEquals(2, vm_count['state']['Stopped'])
        self.assertEquals(2, vm_count['serviceofferingname']['small'])
        self.assertEquals(2, vm_count['hostname']['host_a'])
        self.assertEquals(2, vm_count['zonename']['zone_a'])
        self.assertEquals(2, vm_count['haenable']['true'])

    def mock_cloudstack_list_vms(self, vms):
        acs_mock = patch('app.virtualmachines.resource.VmCountResource.get_cloudstack').start()
        list_vms_mock = Mock()
        list_vms_mock.listVirtualMachines.return_value = vms
        acs_mock.return_value = list_vms_mock
        return list_vms_mock
