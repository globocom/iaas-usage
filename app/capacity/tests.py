import unittest
from flask import json
from mock import patch, Mock
from app import app


class CloudCapacityResourceTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        mock = patch('flask_login.AnonymousUserMixin.is_authenticated').start()
        mock.return_value = True

    def tearDown(self):
        patch.stopall()

    def test_list_capacity_given_empty_response(self):
        list_capacity_mock = self.mock_cloudstack_list_storages({"capacity": []})
        response = self.app.get('/api/v1/lab/cloud_capacity/')

        self.assertEquals(200, response.status_code)
        self.assertEquals({}, json.loads(response.data))
        list_capacity_mock.listCapacity.assert_called_with({'pagesize':'-1'})

    def test_list_capacity(self):
        list_capacity_mock = self.mock_cloudstack_list_storages({"capacity": [
             {"capacitytotal": 100, "capacityused": 10, "percentused": "10.0", "type": 0, "zoneid": "1", "zonename": "zone_a"}
        ]})
        response = self.app.get('/api/v1/lab/cloud_capacity/')
        capacity = json.loads(response.data).get('zone_a')[0]

        self.assertEquals(200, response.status_code)
        self.assertEquals('Memory', capacity.get('type'))
        self.assertEquals(10, capacity.get('capacity_used'))
        self.assertEquals(100, capacity.get('capacity_total'))
        self.assertEquals(10.0, capacity.get('percent_used'))
        self.assertEquals('1', capacity.get('zone_id'))
        self.assertEquals('zone_a', capacity.get('zone_name'))
        list_capacity_mock.listCapacity.assert_called_with({'pagesize':'-1'})

    def mock_cloudstack_list_storages(self, capacity):
        acs_mock = patch('app.capacity.resource.CloudCapacityResource.get_cloudstack').start()
        list_capacity = Mock()
        list_capacity.listCapacity.return_value = capacity
        acs_mock.return_value = list_capacity
        return list_capacity