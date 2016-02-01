from flask import request
from flask_restful import reqparse
from app.auth.utils import required_login
from app.cloudstack.cloudstack_base_resource import CloudstackResource, handle_errors
import app
import re


class VirtualMachineResource(CloudstackResource):

    FEATURE_NAMES = ['state', 'serviceofferingname', 'hostname', 'zonename', 'haenable', 'ostypename']

    @required_login
    @handle_errors
    def get(self, region):
        self._validate_params()
        response = self.get_cloudstack(region).listGloboVirtualMachines(self._filter_by())

        if response.get('errortext') is not None:
            app.logger.error("Error while retrieving data from cloudstack: %s" % response['errortext'])
            return {"message": response['errortext']}, 400

        virtual_machines = dict()
        virtual_machines['summary'] = self._get_vm_summary(response)
        virtual_machines['vms'] = self._vms_to_json(response)
        return virtual_machines

    def _get_vm_summary(self, response):
        vm_count = dict()
        for vm in response.get("virtualmachine", []):
            for ft_name in self.FEATURE_NAMES:
                vm_count[ft_name] = vm_count.get(ft_name, {})
                ft_value = vm.get(ft_name)
                if ft_value is not None:
                    if (ft_name == "zonename") or (ft_name == "serviceofferingname"):
                        ft_value = ft_value.lower()
                    vm_count[ft_name][ft_value] = (vm_count[ft_name].get(ft_value, 0) + 1)
        return vm_count

    def _validate_params(self):
        parser = reqparse.RequestParser()
        self.args = parser.parse_args(req=request)

    def _filter_by(self):
        params = {"listall": "true", "simple": "true"}
        if request.args.get('project_id') is not None:
            params['projectid'] = request.args['project_id']

        if request.args.get('zone_id') is not None:
            params['zoneid'] = request.args['zone_id']

        if request.args.get('host_id') is not None:
            params['hostid'] = request.args['host_id']

        if request.args.get('os_type_id') is not None:
            params['ostypeid'] = request.args['os_type_id']

        if request.args.get('service_offering_id') is not None:
            params['serviceofferingid'] = request.args['service_offering_id']

        if request.args.get('state') is not None:
            params['state'] = request.args['state']

        params.update(self.filter_by_tag())

        return params

    def _vms_to_json(self, response):
        json = {}
        if response is not None and response.get('count') is not None:
            json["count"] = response["count"]
            json["virtual_machines"] = [
                {
                    "id": vm["id"],
                    "name": vm.get("name", vm["instancename"]),
                    "state": vm["state"],
                    "instance_name": vm["instancename"],
                    "zone_name": vm["zonename"],
                    "zone_id": vm["zoneid"],
                    "host_name": vm.get("hostname", None),
                    "host_id": vm.get("hostid", None),
                    "os_type_name": vm.get("ostypename", None),
                    "os_type_id": vm.get("ostypeid", None),
                    "service_offering_name": vm.get("serviceofferingname", ""),
                    "service_offering_id": vm.get("service_offering_id", ""),
                    "ha_enabled": vm["haenable"]
                }
                for vm in response['virtualmachine']
            ]
        else:
            json["count"] = 0
            json["virtual_machines"] = []
        return json

    def filter_by_tag(self):
        params = {}
        tag_parameter_regex = re.compile('tags\[\d\]\..*')
        for key in request.args.keys():
            if tag_parameter_regex.match(key):
                params[key] = request.args[key]
        return params