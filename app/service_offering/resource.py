from app.auth.utils import required_login
from app.cloudstack.cloudstack_base_resource import handle_errors, CloudstackResource


class ServiceOfferingResource(CloudstackResource):

    @required_login
    @handle_errors
    def get(self, region):
        compute_offerings = self.get_cloudstack(region).listServiceOfferings({'pagesize': '-1'})
        return self.parse_compute_offerings(compute_offerings)

    def parse_compute_offerings(self, compute_offerings):
        return [
            {
                "name": offering.get("name"),
                "description": offering.get("displaytext"),
                "memory": offering.get("memory"),
                "cpu_number": offering.get("cpunumber"),
                "cpu_speed": offering.get("cpuspeed"),
            }
            for offering in compute_offerings.get('serviceoffering')
        ]
