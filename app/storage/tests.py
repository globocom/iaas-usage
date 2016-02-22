import unittest
from flask import json
from mock import patch, Mock
from app import app


class StorageResourceTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        mock = patch('flask_login.AnonymousUserMixin.is_authenticated').start()
        mock.return_value = True

    def tearDown(self):
        patch.stopall()

    def test_list_storages_given_volume_api_error(self):
        list_storage_mock = self.mock_cloudstack_list_volumes_and_snapshots({"errortext": "Unable to find project"})
        query = dict(project_id='28f40084-2aed-11e5-8fce-76b2dd27c282')
        response = self.app.get('/api/v1/lab/storage/', query_string=query)

        self.assertEquals(400, response.status_code)
        self.assertEquals("Unable to find project", json.loads(response.data)['message'])
        expect_resp = {'projectid': '28f40084-2aed-11e5-8fce-76b2dd27c282', 'pagesize': '-1', 'listall': 'true'}
        list_storage_mock.listVolumes.assert_called_with(expect_resp)

    def test_list_storages_given_snapshot_api_error(self):
        list_storage_mock = self.mock_cloudstack_list_volumes_and_snapshots(
            {"count": 1, "volume":[{
                "name": 'ROOT-3145', "state": 'Ready',"size": '1287589', "zonename": 'zone', 'zoneid': 1,
                "created": "2015-09-18T14:08:30-0300", "type": 'ROOT', 'virtualmachineid': 1
            }]},
            {"errortext": "Unable to find project"}
        )
        query = dict(project_id='28f40084-2aed-11e5-8fce-76b2dd27c282')
        response = self.app.get('/api/v1/lab/storage/', query_string=query)

        self.assertEquals(400, response.status_code)
        self.assertEquals("Unable to find project", json.loads(response.data)['message'])

        expect_resp = {'projectid': '28f40084-2aed-11e5-8fce-76b2dd27c282', 'pagesize': '-1', 'listall': 'true'}
        list_storage_mock.listVolumes.assert_called_with(expect_resp)
        list_storage_mock.listSnapshots.assert_called_with(expect_resp)

    def test_list_storages_given_empty_data(self):
        list_storage_mock = self.mock_cloudstack_list_volumes_and_snapshots({},{})
        query = dict(project_id='28f40084-2aed-11e5-8fce-76b2dd27c282')
        response = self.app.get('/api/v1/lab/storage/', query_string=query)

        self.assertEquals(200, response.status_code)
        self.assertEquals([], json.loads(response.data)['storage'])

        expect_resp = {'projectid': '28f40084-2aed-11e5-8fce-76b2dd27c282', 'pagesize': '-1', 'listall': 'true'}
        list_storage_mock.listVolumes.assert_called_with(expect_resp)
        list_storage_mock.listSnapshots.assert_called_with(expect_resp)

    def test_list_storages(self):
        list_storage_mock = self.mock_cloudstack_list_volumes_and_snapshots(
            {"count": 1, "volume":[{
                "name": 'ROOT-3145', "state": 'Ready',"size": '1287589', "zonename": 'zone', 'zoneid': 1,
                "created": "2015-09-18T14:08:30-0300", "type": 'ROOT', 'virtualmachineid': 1
            }]},
            {"count": 1, "snapshot":[{
                "name": 'Snapshot-3145', "state": 'BackedUp',"size": '1287589', 'zoneid': 1,
                "created": "2015-09-18T14:08:30-0300", "snapshottype": 'MANUAL', 'vmid': 1, "volumename": "name"
            }]}
        )
        query = dict(project_id='28f40084-2aed-11e5-8fce-76b2dd27c282')
        response = self.app.get('/api/v1/lab/storage/', query_string=query)

        self.assertEquals(200, response.status_code)
        self.assertEquals(2, len(json.loads(response.data)['storage']))

        expect_resp = {'projectid': '28f40084-2aed-11e5-8fce-76b2dd27c282', 'pagesize': '-1', 'listall': 'true'}
        list_storage_mock.listVolumes.assert_called_with(expect_resp)
        list_storage_mock.listSnapshots.assert_called_with(expect_resp)


    def mock_cloudstack_list_volumes_and_snapshots(self, volumes=None, snapshots=None):
        acs_mock = patch('app.storage.resource.StorageResource.get_cloudstack').start()
        list_storage = Mock()
        if volumes is not None:
            list_storage.listVolumes.return_value = volumes
        if snapshots is not None:
            list_storage.listSnapshots.return_value = snapshots
        acs_mock.return_value = list_storage
        return list_storage
