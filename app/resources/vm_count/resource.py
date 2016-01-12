from flask import request
from flask_restful import reqparse
from app.cloudstack.cloudstack_base_resource import CloudstackResource


class VmCountResource(CloudstackResource):

    FEATURE_NAMES = ['state', 'serviceofferingname', 'hostname', 'zonename', 'haenable']


    def get(self, region):
        self._validate_params()
        params = {"listall": "true", "projectid": self.args['project_id']}
        response = self.get_cloudstack(region).listVirtualMachines(params)

        vm_count = {}
        for vm in response["virtualmachine"]:
            for ft_name in self.FEATURE_NAMES:
                vm_count[ft_name] = vm_count.get(ft_name, {})
                ft_value = vm.get(ft_name)
                if ft_value is not None:
                    vm_count[ft_name][ft_value] = (vm_count[ft_name].get(ft_value, 0) + 1)

        return vm_count

    def _validate_params(self):
        parser = reqparse.RequestParser()
        parser.add_argument('project_id', required=True, type=str, help='project_id must be informed')
        self.args = parser.parse_args(req=request)
