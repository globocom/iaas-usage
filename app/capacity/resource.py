from app.auth.utils import required_login
from app.cloudstack.cloudstack_base_resource import handle_errors, CloudstackResource


class CloudCapacityResource(CloudstackResource):

    capacity_type = { 0: 'Memory', 1: 'CPU', 3: 'Primary Storage', 6: 'Secondary Storage'}

    @required_login
    @handle_errors
    def get(self, region):
        capacity_response = self.get_cloudstack(region).listCapacity({'pagesize': '-1'})
        return self.parse_response(capacity_response)

    def parse_response(self, capacity_response):
        cloud_capacity = {}
        for c in capacity_response.get('capacity'):
            type = self.capacity_type.get(c['type'])
            if type:
                zone_name = c.get('zonename')
                resource_type = {
                    "type": type,
                    "capacity_total": c.get('capacitytotal'),
                    "capacity_used": c.get('capacityused'),
                    "percent_used": c.get('percentused'),
                    "zone_name": zone_name,
                    "zone_id": c.get('zoneid')
                }
                zone_capacity = cloud_capacity.get(zone_name, [])
                zone_capacity.append(resource_type)
                cloud_capacity[zone_name] = zone_capacity

        return cloud_capacity
