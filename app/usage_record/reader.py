import datetime
from app import app
from app.cloudstack.cloudstack_base_resource import CloudstackResource
from app.usage_record.measure import MeasureClient
from dateutil.parser import parse


class UsageRecordReader:

    USAGE_TYPES = {1: 'Running VM', 2: 'Allocated VM', 6: 'Volume', 9: 'Volume Snapshot'}

    def __init__(self, region):
        self.region = region
        self.acs = CloudstackResource().get_cloudstack(region)
        self.measure = MeasureClient()

    def send_usage(self):
        app.logger.info("Processing usage records for the region: " + self.region)
        date = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

        try:
            self.delete_records(date)

            params = dict()
            params['startdate'] = date
            params['enddate'] = date
            params['pagesize'] = app.config['USAGE_API_BATCH_SIZE']
            record_count = 0

            projects = self.get_projects()

            for usage_type_id, usage_type in self.USAGE_TYPES.iteritems():
                app.logger.info("Processing usage records by type: " + usage_type)
                params['page'] = '1'
                params['type'] = str(usage_type_id)

                records = self.acs.listUsageRecords(params).get('usagerecord')

                while records is not None and len(records) > 0:
                    app.logger.info("Processing  %s usage records " % len(records))

                    for r in records:
                        if r.get('project') is not None:
                            project = next((x for x in projects if x.get('name') == r.get('project')), dict())
                            account = project.get('account')
                            self.measure.create(self.build_usage_record(r, account, usage_type))

                    params['page'] = str(int(params['page']) + 1)
                    record_count += len(records)
                    records = self.acs.listUsageRecords(params).get('usagerecord')

            app.logger.info("Execution ended %s records processed." % record_count)
        except:
            app.logger.exception("Error reading usage data. Date: " + date + " Region: " + self.region)
            self.rollback(date)

    def build_usage_record(self, r, account, usage_type):
        usage_record = dict()
        usage_record['rawusage'] = float(r.get('rawusage'))
        usage_record['offeringid'] = r.get('offeringid', '-')
        usage_record['project'] = r['project']
        usage_record['usagetype'] = usage_type
        usage_record['date'] = parse(r['startdate']).date().isoformat()
        usage_record['account'] = account
        usage_record['region'] = self.region
        return usage_record

    def rollback(self, date):
        app.logger.info("Rolling back operation Date: " + date + " Region: " + self.region)
        self.delete_records(date)

    def delete_records(self, date):
        self.measure.delete(self.region, date)

    def get_projects(self):
        return self.acs.listProjects({'simple': 'true', 'listall': 'true'}).get('project')
