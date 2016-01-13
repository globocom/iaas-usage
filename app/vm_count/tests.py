import unittest
from flask import json
from mock import patch, Mock
from app import app


class VmCountResourceTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        pass

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
        self.assertEquals(1, vm_count['serviceofferingname']['Small'])
        self.assertEquals(1, vm_count['serviceofferingname']['Large'])
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
        self.assertEquals(2, vm_count['serviceofferingname']['Small'])
        self.assertEquals(2, vm_count['hostname']['host_a'])
        self.assertEquals(2, vm_count['zonename']['zone_a'])
        self.assertEquals(2, vm_count['haenable']['true'])

    def mock_cloudstack_list_vms(self, vms):
        acs_mock = patch('app.vm_count.resource.VmCountResource.get_cloudstack').start()
        list_vms_mock = Mock()
        list_vms_mock.listVirtualMachines.return_value = vms
        acs_mock.return_value = list_vms_mock
        return list_vms_mock