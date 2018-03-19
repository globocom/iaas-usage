import unittest
from mock import patch, Mock
from app import cache, db
from app.usage_record.usage_record_builder import UsageRecordBuilder
from app.usage_record.usage_records_samples import full_record_sample, \
    records_with_overlapping_running_and_allocated, record_with_running_time_equals_allocated_time
from app.usage_record.reader import UsageRecordReader


class UsageRecordReaderTestCase(unittest.TestCase):

    def setUp(self):
        db.create_all()
        self.service_offerings = {'name': 'Small', 'id': '8d67bc56-d1dd-4f19-83bd-b3b546a2a4f7'}

    def tearDown(self):
        db.drop_all()
        patch.stopall()

    def test_read_usage_records_given_no_records_found(self):
        acs_mock = self.mock_cloudstack({'project': [{'name': 'name'}]}, {'usagerecord': []}, {'serviceoffering': [self.service_offerings]})
        measure_mock = self.mock_elk()
        reader = UsageRecordReader('region')

        reader.index_usage()

        self.assertEquals(1, measure_mock.delete_usage_records.call_count)
        self.assertEquals(0, measure_mock.create_usage_record.call_count)
        self.assertEquals(1, acs_mock.listUsageRecords.called)

    def test_read_usage_records_given_error(self):
        acs_mock = self.mock_cloudstack({'project': [{'name': 'name'}]}, {'usagerecord': [{
            "enddate": "2016-03-14'T'23:59:59-03:00",
            "offeringid": "8d67bc56-d1dd-4f19-83bd-b3b546a2a4f7",
            "project": "Admin",
            "projectid": "8ea2cf55-2b12-4821-bac7-3c96a4cf1ac2",
            "rawusage": "24",
            "startdate": "2016-03-14'T'00:00:00-03:00",
            "usagetype": 2

        }]}, {'serviceoffering': [self.service_offerings]})
        measure_mock = self.mock_elk(False)
        reader = UsageRecordReader('region')

        reader.index_usage()

        self.assertEquals(2, measure_mock.delete_usage_records.call_count)
        self.assertEquals(1, measure_mock.create_usage_record.call_count)
        self.assertEquals(1, acs_mock.listUsageRecords.call_count)

    def test_read_usage_records(self):
        acs_mock = self.mock_cloudstack({'project': [{'name': 'name'}]}, {'usagerecord': [{
            "enddate": "2016-03-14'T'23:59:59-03:00",
            "offeringid": "8d67bc56-d1dd-4f19-83bd-b3b546a2a4f7",
            "project": "Admin",
            "projectid": "8ea2cf55-2b12-4821-bac7-3c96a4cf1ac2",
            "rawusage": "24",
            "startdate": "2016-03-14'T'00:00:00-03:00",
            "usagetype": 2

        }]}, {'serviceoffering': [self.service_offerings]})
        measure_mock = self.mock_elk()
        reader = UsageRecordReader('region')

        reader.index_usage()

        self.assertEquals(1, measure_mock.delete_usage_records.call_count)
        self.assertEquals(2, measure_mock.create_usage_record.call_count)
        self.assertEquals(4, acs_mock.listUsageRecords.call_count)

    def mock_elk(self, success=True):
        mock = patch('app.usage_record.reader.ELKClient').start()
        elk_mock = Mock()
        if success is not True:
            elk_mock.create_usage_record.side_effect = Exception()
        elk_mock.delete_usage_records.return_value = success
        mock.return_value = elk_mock
        return elk_mock

    def mock_cloudstack(self, projects, records, offerings):
        acs_mock = patch('app.usage_record.reader.CloudstackResource.get_cloudstack').start()
        cloudstack = Mock()
        cloudstack.listProjects.return_value = projects

        def list_record_mock(params):
            if params.get('page') == '1':
                return records
            else:
                return {}

        cloudstack.listUsageRecords.side_effect = list_record_mock
        cloudstack.listServiceOfferings.return_value = offerings
        acs_mock.return_value = cloudstack
        return cloudstack


class UsageRecordBuilderTestCase(unittest.TestCase):

    def setUp(self):
        db.create_all()
        self.projects = [{'account': 'acc', 'domain': 'ROOT', 'name': 'Project', 'id': '1'}]
        self.service_offerings = [{'name': 'Small', 'id': '100'}, {'Large': '20GB', 'id': '200'}]
        self.disk_offerings = [{'name': '10GB', 'id': '1'}, {'name': '20GB', 'id': '2'}]

        self.acs_mock = self.mock_cloudstack(
            {'project': self.projects}, {'serviceoffering': self.service_offerings}, {'diskoffering': self.disk_offerings}
        )

    def tearDown(self):
        cache.clear()
        db.drop_all()
        patch.stopall()

    def test_build_usage_report_given_overlapping_running_and_allocated_vm_offerings(self):
        response = UsageRecordBuilder('region').build_usage_report(records_with_overlapping_running_and_allocated, '2016-01-01', '2016-01-01')

        self.assertEquals(2, len(response['usage']))
        self.assertEquals(24, response['usage'][0].get('usage'))
        self.assertEquals('Allocated VM', response['usage'][0].get('type'))
        self.assertEquals(48, response['usage'][1].get('usage'))
        self.assertEquals('Running VM', response['usage'][1].get('type'))
        self.assert_acs_mocks()

    def test_build_usage_report_given_running_time_equals_allocated_time(self):
        response = UsageRecordBuilder('region').build_usage_report(record_with_running_time_equals_allocated_time, '2016-01-01', '2016-01-01')

        self.assertEquals(1, len(response['usage']))
        self.assertEquals(48, response['usage'][0].get('usage'))
        self.assertEquals('Running VM', response['usage'][0].get('type'))
        self.assert_acs_mocks()

    def test_list_usage_records(self):
        response = UsageRecordBuilder('region').build_usage_report(full_record_sample, '2016-01-01', '2016-01-01')

        self.assertEquals(2, len(response['usage']))
        self.assert_acs_mocks()

    def assert_acs_mocks(self):
        self.assertEquals(1, self.acs_mock.listProjects.call_count)

    def mock_cloudstack(self, projects, compute_offerings, disk_offerings):
        acs_mock = patch('app.usage_record.usage_record_builder.CloudstackClientFactory.get_instance').start()
        cloudstack = Mock()
        cloudstack.listProjects.return_value = projects
        cloudstack.listServiceOfferings.return_value = compute_offerings
        cloudstack.listDiskOfferings.return_value = disk_offerings
        acs_mock.return_value = cloudstack
        return cloudstack
