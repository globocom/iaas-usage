from app import app, cache
from app.cloudstack.cloudstack_base_resource import CloudstackClientFactory


class UsageRecordBuilder:

    def __init__(self, region):
        self.acs = CloudstackClientFactory.get_instance(region)
        self.region = region
        self.projects = self._get_projects()

    def build_usage_report(self, aggregations, start, end):
        records = {"usage": []}

        records_grouped_by_type = {'Running VM': [], 'Allocated VM': []}

        for project_bucket in aggregations['by_project']['buckets']:
            project_id = project_bucket['key']
            project = next((x for x in self.projects if x.get('id') == project_id), None)

            for resource_type_bucket in project_bucket['by_type']['buckets']:
                usage_type = resource_type_bucket['key']

                for offering_bucket in resource_type_bucket['by_offering']['buckets']:
                    offering_struct = offering_bucket['key'].split('|')
                    offering_id = offering_struct[0] or None
                    offering_name = offering_struct[1] or None
                    offering_cpu = offering_struct[2] or None
                    offering_ram = offering_struct[3] or None
                    raw_usage = float(offering_bucket['rawusage_sum']['value'])

                    if raw_usage > app.config['USAGE_MINIMUM_TIME'] and project is not None:
                        account = project.get('account', '-')
                        domain = project.get('domain', '-')

                        usage_record = {
                            'project_id': project_id,
                            'project_name': project.get('name'),
                            'type': usage_type,
                            'start_date': start,
                            'end_date': end,
                            'offering_id': offering_id,
                            'offering_name': offering_name,
                            'offering_cpu': offering_cpu,
                            'offering_ram': offering_ram,
                            'usage': raw_usage,
                            'account': account,
                            'domain': domain,
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

    def _get_projects(self):
        decorator = cache.cached(timeout=app.config['USAGE_CACHE_TIME'], key_prefix='projects_' + self.region)
        params = {'simple': 'true', 'listall': 'true'}
        return decorator(lambda: self.acs.listProjects(params).get('project'))()
