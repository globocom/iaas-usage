import unittest
from flask import json
from mock import patch, Mock
from app import app


class ServiceOfferingResourceTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        mock = patch('flask_login.AnonymousUserMixin.is_authenticated').start()
        mock.return_value = True

    def tearDown(self):
        patch.stopall()

    def test_list_service_offerings_given_emtpy_list(self):
        list_offering_mock = self.mock_cloudstack_list_service_offerings({"serviceoffering": []})
        response = self.app.get('/api/v1/lab/service_offering/')

        self.assertEquals(200, response.status_code)
        self.assertEquals([], json.loads(response.data))
        list_offering_mock.listServiceOfferings.assert_called_with({'pagesize':'-1'})

    def test_list_service_offering(self):
        list_offering_mock = self.mock_cloudstack_list_service_offerings({"serviceoffering": [
             {"name": 'Small',"displaytext": '512Mb1000Mhz',"memory": '512',"cpunumber": '1',"cpuspeed": '1000'}
        ]})
        response = self.app.get('/api/v1/lab/service_offering/')
        offering = json.loads(response.data)[0]

        self.assertEquals(200, response.status_code)
        self.assertEquals('Small', offering["name"])
        self.assertEquals('512Mb1000Mhz', offering["description"])
        self.assertEquals('512', offering["memory"])
        self.assertEquals('1', offering["cpu_number"])
        self.assertEquals('1000', offering["cpu_speed"])
        list_offering_mock.listServiceOfferings.assert_called_with({'pagesize':'-1'})

    def mock_cloudstack_list_service_offerings(self, offering):
        acs_mock = patch('app.service_offering.resource.ServiceOfferingResource.get_cloudstack').start()
        list_offering = Mock()
        list_offering.listServiceOfferings.return_value = offering
        acs_mock.return_value = list_offering
        return list_offering