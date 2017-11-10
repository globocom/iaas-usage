from app import app, cache
from app.cloudstack.cloudstack_base_resource import CloudstackClientFactory


class UsageRecordBuilder:

    def __init__(self, region):
        self.acs = CloudstackClientFactory.get_instance(region)
        self.region = region
        self.projects = self._get_projects()
        self.compute_offerings = self._get_compute_offerings()
        self.disk_offerings = self._get_disk_offerings()

    def build_usage_report(self, aggregations, start, end):
        records = {"usage": []}

        records_grouped_by_type = {'Running VM': [], 'Allocated VM': [], 'Volume': [], 'Volume Snapshot': []}

        for project_bucket in aggregations['by_project']['buckets']:
            project_id = project_bucket['key']
            project = next((x for x in self.projects if x.get('id') == project_id), None)

            for resource_type_bucket in project_bucket['by_type']['buckets']:
                usage_type = resource_type_bucket['key']

                for offering_bucket in resource_type_bucket['by_offering']['buckets']:
                    offering_id = offering_bucket['key']
                    offering_name = self._get_offering_name(self.compute_offerings, self.disk_offerings, offering_id, usage_type)
                    raw_usage = float(offering_bucket['rawusage_sum']['value'])

                    if raw_usage > app.config['USAGE_MINIMUM_TIME'] and project is not None:
                        account = project.get('account', '-')
                        domain = project.get('domain', '-')

                        usage_record = {
                            'project_id': project_id, 'project_name': project.get('name'),
                            'type': usage_type, 'start_date': start, 'end_date': end,
                            "offering_name": offering_name, 'usage': raw_usage, 'account': account, 'domain': domain,
                            'region': self.region.upper()
                        }
                        records['usage'].append(usage_record)
                        records_grouped_by_type[usage_type].append(usage_record)

        self._calculate_allocated_vm_time(records_grouped_by_type, records)

        return records

    def _calculate_allocated_vm_time(self, grouped_usage, result):
        for allocated_vm in grouped_usage['Allocated VM']:
            prj = allocated_vm['project_id']
            offering = allocated_vm['offering_name']
            running_vms = grouped_usage['Running VM']

            running_vm = filter(lambda x: x['project_id'] == prj and x['offering_name'] == offering, running_vms)

            if running_vm:
                allocated_vm_time = allocated_vm['usage'] - running_vm[0]['usage']
                allocated_vm['usage'] = allocated_vm_time
                if allocated_vm_time < app.config['USAGE_MINIMUM_TIME']:
                    result['usage'].remove(allocated_vm)

    def _get_offering_name(self, compute_offerings, disk_offerings, offering_id, type):
        offering_name = ''
        if type == 'Volume':
            offering = next((x for x in disk_offerings if x.get('id') == offering_id), None)
            offering_name = offering.get('name') if offering is not None else '-'

        if type == 'Running VM' or type == 'Allocated VM' or offering_name == '-':
            offering = next((x for x in compute_offerings if x.get('id') == offering_id), None)
            offering_name = offering.get('name') if offering is not None else '-'

        return offering_name

    def _get_projects(self):
        decorator = cache.cached(timeout=app.config['USAGE_CACHE_TIME'], key_prefix='projects_' + self.region)
        params = {'simple': 'true', 'listall': 'true'}
        return decorator(lambda: self.acs.listProjects(params).get('project'))()

    def _get_compute_offerings(self):
        decorator = cache.cached(timeout=app.config['USAGE_CACHE_TIME'], key_prefix='compute_offerings_' + self.region)
        return decorator(lambda: self.acs.listServiceOfferings({}).get('serviceoffering'))()

    def _get_disk_offerings(self):
        decorator = cache.cached(timeout=app.config['USAGE_CACHE_TIME'], key_prefix='disk_offerings_' + self.region)
        return decorator(lambda: self.acs.listDiskOfferings({}).get('diskoffering'))()
