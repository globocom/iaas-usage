from flask import request
from flask_restful import reqparse
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

        aggregations = self.get_usage_records(region, start, end)
        usage_records = self.build_usage_report(region, aggregations, start, end)

        return usage_records

    def build_usage_report(self, region, aggregations, start, end):
        projects = self.get_projects(region)
        compute_offerings = self.get_compute_offerings(region)
        disk_offerings = self.get_disk_offerings(region)

        result = {"usage": []}
        for project_bucket in aggregations['by_project']['buckets']:
            project_name = project_bucket['key']
            project = next((x for x in projects if x.get('name') == project_name), None)

            for resource_type_bucket in project_bucket['by_type']['buckets']:
                usage_type = resource_type_bucket['key']

                for offering_bucket in resource_type_bucket['by_offering']['buckets']:
                    offering_id = offering_bucket['key']
                    offering_name = self.get_offering_name(compute_offerings, disk_offerings, offering_id, usage_type)
                    raw_usage = offering_bucket['rawusage_sum']['value']

                    account = project.get('account') if project is not None else '-'
                    domain = project.get('domain') if project is not None else '-'
                    result['usage'].append({
                        'project': project_name, 'type': usage_type, 'start_date': start,
                        'end_date': end, "offering_name": offering_name, 'usage': raw_usage,
                        'account': account, 'domain': domain,
                        'region': region.upper()
                    })
        return result

    def get_usage_records(self, region, start, end):
        return MeasureClient().find(region, start, end)

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
        self.args = parser.parse_args(req=request)
