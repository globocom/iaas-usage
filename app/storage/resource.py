from flask import request
from flask_restful import reqparse
from app.auth.utils import required_login
from app.cloudstack.cloudstack_base_resource import CloudstackResource, handle_errors
import app
import re


class StorageResource(CloudstackResource):

    @required_login
    @handle_errors
    def get(self, region):
        self._validate_params()
        storages = dict()

        volumes = self.get_cloudstack(region).listVolumes(self._filter_by())
        if volumes.get('errortext') is not None:
            app.logger.error("Error while retrieving data from cloudstack: %s" % volumes['errortext'])
            return {"message": volumes['errortext']}, 400

        storages['storage'] = self._parse_volumes(volumes)

        snapshots = self.get_cloudstack(region).listSnapshots(self._filter_by())
        if snapshots.get('errortext') is not None:
            app.logger.error("Error while retrieving data from cloudstack: %s" % snapshots['errortext'])
            return {"message": snapshots['errortext']}, 400

        if snapshots:
            storages['storage'].extend(self._parse_snapshots(snapshots))

        templates = self.get_cloudstack(region).listTemplates(self._filter_by())
        if templates.get('errortext') is not None:
            app.logger.error("Error while retrieving data from cloudstack: %s" % templates['errortext'])
            return {"message": templates['errortext']}, 400

        if templates:
            storages['storage'].extend(self._parse_templates(templates))

        return storages

    def _validate_params(self):
        parser = reqparse.RequestParser()
        self.args = parser.parse_args(req=request)

    def _filter_by(self):
        params = {"listall": "true"}
        if request.args.get('project_id') is not None:
            params['projectid'] = request.args['project_id']

        if request.args.get('zone_id') is not None:
            params['zoneid'] = request.args['zone_id']

        params['pagesize'] = '-1'
        params['templatefilter'] = 'self'
        params.update(self.filter_by_tag())

        return params

    def filter_by_tag(self):
        params = {}
        tag_parameter_regex = re.compile('tags\[\d\]\..*')
        for key in request.args.keys():
            if tag_parameter_regex.match(key):
                params[key] = request.args[key]
        return params

    def _parse_volumes(self, volumes):
        if volumes is not None and volumes.get('count') is not None:
            return [
                {
                    "name": volume['name'],
                    "storage_type": 'Volume',
                    "state": volume['state'],
                    "size": volume["size"],
                    "zone_name": volume['zonename'],
                    "zone_id": volume['zoneid'],
                    "created_at": volume['created'],
                    "type": volume['type'],
                    "attached":  volume.get('virtualmachineid') is not None

                }
                for volume in volumes.get('volume')
            ]
        else:
            return []

    def _parse_snapshots(self, snapshots):
        if snapshots is not None and snapshots.get('count') is not None:
            return [
                {
                    "name": snapshot['name'],
                    "storage_type": 'Snapshot',
                    "state": snapshot['state'],
                    "size": snapshot.get("volumesize"),
                    "snapshot_state": 'Attached' if snapshot.get('vmid') is not None else 'Detached',
                    "zone_id": snapshot.get('zoneid'),
                    "zone_name": snapshot.get('zonename'),
                    "created_at": snapshot['created'],
                    "type": snapshot['snapshottype'],
                    "volume_name": snapshot['volumename']
                }
                for snapshot in snapshots.get('snapshot')
            ]
        else:
            return []

    def _parse_templates(self, templates):
        if templates is not None and templates.get('count') is not None:
            return [
                {
                    "name": template['name'],
                    "storage_type": 'Template',
                    "state": template['status'],
                    "size": template.get("size"),
                    "zone_id": template.get('zoneid'),
                    "zone_name": template.get('zonename'),
                    "created_at": template['created'],
                    "type": template['templatetype'],
                }
                for template in templates.get('template')
            ]
        else:
            return []
