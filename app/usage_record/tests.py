import unittest
from mock import patch, Mock
from app import UsageRecordReader


class UsageRecordReaderTestCase(unittest.TestCase):

    def test_read_usage_records_given_no_records_found(self):
        acs_mock = self.mock_cloudstack({'project': [{'name': 'name'}]}, {'usagerecord': []})
        measure_mock = self.mock_measure()
        reader = UsageRecordReader('region')

        reader.send_usage()

        self.assertEquals(1, measure_mock.delete.call_count)
        self.assertEquals(0, measure_mock.create.call_count)
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

        }]})
        measure_mock = self.mock_measure(False)
        reader = UsageRecordReader('region')

        reader.send_usage()

        self.assertEquals(2, measure_mock.delete.call_count)
        self.assertEquals(1, measure_mock.create.call_count)
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

        }]})
        measure_mock = self.mock_measure()
        reader = UsageRecordReader('region')

        reader.send_usage()

        self.assertEquals(1, measure_mock.delete.call_count)
        self.assertEquals(4, measure_mock.create.call_count)
        self.assertEquals(8, acs_mock.listUsageRecords.call_count)

    def mock_measure(self, success=True):
        measure_mock = patch('app.usage_record.reader.MeasureClient').start()
        measure = Mock()
        if success is not True:
            measure.create.side_effect = Exception()
        measure.delete.return_value = success
        measure_mock.return_value = measure
        return measure

    def mock_cloudstack(self, projects, records):
        acs_mock = patch('app.usage_record.reader.CloudstackResource.get_cloudstack').start()
        cloudstack = Mock()
        cloudstack.listProjects.return_value = projects

        def list_record_mock(params):
            if params.get('page') == '1':
                return records
            else:
                return {}

        cloudstack.listUsageRecords.side_effect = list_record_mock

        acs_mock.return_value = cloudstack
        return cloudstack
