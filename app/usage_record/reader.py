import datetime
from app import app, db, cache
from app.cloudstack.cloudstack_base_resource import CloudstackResource
from app.usage_record.elk import ELKClient
from app.projects.models import Project
from dateutil.parser import parse


class UsageRecordReader:

    USAGE_TYPES = {1: 'Running VM', 2: 'Allocated VM'}
    DEFAULT_CPU_SIZE = app.config['USAGE_DEFAULT_OFFERING_CPU']
    DEFAULT_MEMORY_SIZE = app.config['USAGE_DEFAULT_OFFERING_MEMORY']

    def __init__(self, region):
        self.region = region
        self.acs = CloudstackResource().get_cloudstack(region)
        self.compute_offerings = self.get_offerings()
        self.elk_client = ELKClient()

    def index_usage(self, date=None):
        if date is None:
            date = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

        self.log("Starting usage processing. Date: " + date)

        try:
            self.delete_records(date)

            params = dict()
            params['startdate'] = date
            params['enddate'] = date
            params['pagesize'] = app.config['USAGE_API_BATCH_SIZE']
            record_count = 0

            projects = self.get_projects()

            for usage_type_id, usage_type in self.USAGE_TYPES.iteritems():
                self.log("Processing usage records by type: " + usage_type)
                params['page'] = '1'
                params['type'] = str(usage_type_id)

                records = self.acs.listUsageRecords(params).get('usagerecord')

                while records is not None and len(records) > 0:
                    self.log("Processing  %s usage records " % len(records))

                    for r in records:
                        project = next((x for x in projects if x.get('id') == r.get('projectid')), dict())
                        account = project.get('account')
                        project = self.save_project(projects, project.get('id', app.config['USAGE_DEFAULT_PROJECT_ID']), self.region)
                        self.elk_client.create_usage_record(self.build_usage_record(project, r, account, usage_type))

                    params['page'] = str(int(params['page']) + 1)
                    record_count += len(records)
                    records = self.acs.listUsageRecords(params).get('usagerecord')

            db.session.commit()
            self.log("Execution ended %s records processed." % record_count)
        except:
            self.log("Error reading usage data. Date: %s" % date, level='exception')
            self.rollback(date)

    def build_usage_record(self, project, r, account, usage_type):
        usage_record = dict()
        if str(r.get('rawusage')).find(','):
            usage_record['rawusage'] = float(str(r.get('rawusage')).replace(',', '.'))
        else:
            usage_record['rawusage'] = float(r.get('rawusage'))

        usage_record['projectid'] = project.uuid
        usage_record['usagetype'] = usage_type
        usage_record['date'] = parse(r['startdate']).date().isoformat()
        usage_record['account'] = account
        usage_record['region'] = self.region

        compute_offering = self.find_compute_offering(r.get('offeringid')) or dict()

        default_offering_name = 'Deprecated or Deleted'
        usage_record['offering_struct'] = "%s|%s|%s|%s" % (
            compute_offering.get('id', 'default'),
            compute_offering.get('name', default_offering_name),
            compute_offering.get('cpunumber', self.DEFAULT_CPU_SIZE),
            compute_offering.get('memory', self.DEFAULT_MEMORY_SIZE)
        )
        usage_record['offeringid'] = compute_offering.get('id', 'default')
        usage_record['offering_name'] = compute_offering.get('name', default_offering_name)
        usage_record['cpu_cores'] = compute_offering.get('cpunumber', self.DEFAULT_CPU_SIZE)
        usage_record['memory'] = compute_offering.get('memory', self.DEFAULT_MEMORY_SIZE)

        return usage_record

    def log(self, message, level='info'):
        getattr(app.logger, level)('[%s] %s' % (self.region.upper(), message))

    def rollback(self, date):
        self.log("Rolling back operation Date: " + date)
        self.delete_records(date)

    def delete_records(self, date):
        self.elk_client.delete_usage_records(self.region, date)

    def get_projects(self):
        return self.acs.listProjects({'simple': 'true', 'listall': 'true'}).get('project')

    def save_project(self, projects, project_id, region):
        decorator = cache.cached(timeout=300, key_prefix='projects_' + project_id)
        return decorator(lambda: self._save_project(projects, project_id, region))()

    def _save_project(self, projects, project_id, region):
        acs_project = self.find_project(projects, project_id)
        if acs_project:
            local_project = self.find_local_project(project_id)

            if not local_project:
                local_project = Project()

            local_project.uuid = acs_project['id']
            local_project.name = acs_project['name']

            if region == 'dev' or region == 'rjdev':
                local_project.process_id = app.config['USAGE_DEFAULT_PROCESS_ID_DEV']
            else:
                local_project.process_id = app.config['USAGE_DEFAULT_PROCESS_ID']

            if acs_project.get('businessserviceid'):
                local_project.business_service_id = acs_project.get('businessserviceid')
            else:
                local_project.business_service_id = app.config['USAGE_NOT_CLASSIFIED_BUSINESS_SERVICE_ID']

            if acs_project.get('clientid'):
                local_project.client_id = acs_project.get('clientid')
            else:
                local_project.business_service_id = app.config['USAGE_DEFAULT_CLIENT_ID']

            local_project.component_id = acs_project.get('componentid', None)
            local_project.sub_component_id = acs_project.get('subcomponentid')
            local_project.product_id = acs_project.get('productid', None)
            local_project.detailed_usage = acs_project.get('detailedusage', False)

            db.session.add(local_project)
            return local_project
        else:
            local_project = self.find_local_project(project_id)

            if not local_project:
                local_project = Project()

            local_project.uuid = app.config['USAGE_DEFAULT_PROJECT_ID']
            local_project.name = app.config['USAGE_DEFAULT_PROJECT_NAME']
            local_project.process_id = app.config['USAGE_DEFAULT_PROCESS_ID']
            local_project.business_service_id = app.config['USAGE_DEFAULT_BUSINESS_SERVICE_ID']
            local_project.client_id = app.config['USAGE_DEFAULT_CLIENT_ID']
            local_project.component_id = app.config['USAGE_DEFAULT_COMPONENT_ID']
            local_project.sub_component_id = app.config['USAGE_DEFAULT_SUB_COMPONENT_ID']
            local_project.detailed_usage = False

            db.session.add(local_project)
            return local_project

    def find_local_project(self, id):
        return Project.find_by_uuid(id)

    def get_offerings(self):
        return self.acs.listServiceOfferings({}).get('serviceoffering')

    def find_compute_offering(self, id):
        return next((x for x in self.compute_offerings if x.get('id') == id), None)

    def find_project(self, projects, id):
        return next((x for x in projects if x.get('id') == id), None)
