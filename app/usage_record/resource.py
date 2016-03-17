from flask import request
from flask_restful import reqparse
import functools
from app.auth.utils import required_login
from app.cloudstack.cloudstack_base_resource import CloudstackResource, handle_errors
from app.usage_record.measure import MeasureClient
from app import app, cache


class UsageRecordResource(CloudstackResource):

    @required_login
    @handle_errors
    def get(self, region):
        self._validate_params()
        start = self.args.get('start_date')
        end = self.args.get('end_date')
        account = self.args.get('account_name')

        aggregations = self.get_usage_records(region, account, start, end)
        usage_records = self.build_usage_report(region, aggregations, start, end)

        return usage_records

    def build_usage_report(self, region, aggregations, start, end):
        projects = self.get_projects(region)
        compute_offerings = self.get_compute_offerings(region)
        disk_offerings = self.get_disk_offerings(region)

        records = {"usage": []}

        records_grouped_by_type = {'Running VM': [], 'Allocated VM' : [], 'Volume' : [], 'Volume Snapshot': []}

        for project_bucket in aggregations['by_project']['buckets']:
            project_name = project_bucket['key']
            project = next((x for x in projects if x.get('name') == project_name), None)

            for resource_type_bucket in project_bucket['by_type']['buckets']:
                usage_type = resource_type_bucket['key']

                for offering_bucket in resource_type_bucket['by_offering']['buckets']:
                    offering_id = offering_bucket['key']
                    offering_name = self.get_offering_name(compute_offerings, disk_offerings, offering_id, usage_type)
                    raw_usage = float(offering_bucket['rawusage_sum']['value'])

                    if raw_usage > app.config['USAGE_MINIMUM_TIME'] and project is not None:
                        account = project.get('account', '-')
                        domain = project.get('domain', '-')

                        usage_record = {
                            'project': project_name, 'type': usage_type, 'start_date': start, 'end_date': end,
                            "offering_name": offering_name, 'usage': raw_usage, 'account': account, 'domain': domain,
                            'region': region.upper()
                        }
                        records['usage'].append(usage_record)
                        records_grouped_by_type[usage_type].append(usage_record)

        self.calculate_allocated_vm_time(records_grouped_by_type, records)

        return records

    def calculate_allocated_vm_time(self, grouped_usage, result):
        for allocated_vm in grouped_usage['Allocated VM']:
            prj = allocated_vm['project']
            offering = allocated_vm['offering_name']
            running_vms = grouped_usage['Running VM']

            running_vm = filter(lambda x: x['project'] == prj and x['offering_name'] == offering, running_vms)

            if running_vm:
                allocated_vm_time = allocated_vm['usage'] - running_vm[0]['usage']
                allocated_vm['usage'] = allocated_vm_time
                if allocated_vm_time < app.config['USAGE_MINIMUM_TIME']:
                    result['usage'].remove(allocated_vm)

    def get_usage_records(self, region, account, start, end):
        return MeasureClient().find(region, account, start, end)

    def get_offering_name(self, compute_offerings, disk_offerings, offering_id, type):
        offering_name = ''
        if type == 'Volume':
            offering = next((x for x in disk_offerings if x.get('id') == offering_id), None)
            offering_name = offering.get('name') if offering is not None else '-'

        if type == 'Running VM' or type == 'Allocated VM' or offering_name == '-':
            offering = next((x for x in compute_offerings if x.get('id') == offering_id), None)
            offering_name = offering.get('name') if offering is not None else '-'

        return offering_name

    def get_projects(self, region):
        decorator = cache.cached(timeout=app.config['USAGE_CACHE_TIME'], key_prefix='projects_' + region)
        params = {'simple': 'true', 'listall': 'true'}
        return decorator(lambda: self.get_cloudstack(region).listProjects(params).get('project'))()

    def get_compute_offerings(self, region):
        decorator = cache.cached(timeout=app.config['USAGE_CACHE_TIME'], key_prefix='compute_offerings_' + region)
        return decorator(lambda: self.get_cloudstack(region).listServiceOfferings({}).get('serviceoffering'))()

    def get_disk_offerings(self, region):
        decorator = cache.cached(timeout=app.config['USAGE_CACHE_TIME'], key_prefix='disk_offerings_' + region)
        return decorator(lambda: self.get_cloudstack(region).listDiskOfferings({}).get('diskoffering'))()

    def _validate_params(self):
        parser = reqparse.RequestParser()
        parser.add_argument('start_date', required=True, type=str, help='start_date should be informed')
        parser.add_argument('end_date', required=True, type=str, help='end_date should be informed')
        parser.add_argument('account_name')
        self.args = parser.parse_args(req=request)
