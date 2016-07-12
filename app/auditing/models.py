from flask import json
from app import db
from marshmallow import Schema, fields
from app.cloudstack.cloudstack_base_resource import CloudstackClientFactory


class AbstractEvent(db.Model):

    __tablename__ = 'event'
    __table_args__ = {'useexisting': True}

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(30), nullable=False)
    resource_type = db.Column(db.String(30), nullable=False)
    resource_id = db.Column(db.String(50))
    resource_name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    username = db.Column(db.String(80))
    account = db.Column(db.String(80))
    date = db.Column(db.DateTime, nullable=False)
    region = db.Column(db.String(5), nullable=False)
    original_event = db.Column(db.String(3000), nullable=False)

    def __init__(self, event_key, **kwargs):
        super(AbstractEvent, self).__init__(**kwargs)
        self.action = self._get_action(event_key)
        self.resource_type = self.get_resource_type(event_key)
        self.resource_id = self._get_resource_id()
        self.resource_name = self._get_resource_name()

    @property
    def date_time(self):
        return self.date.strftime('%d/%m/%Y %H:%M:%S')

    @property
    def details(self):
        if self.original_event:
            return json.loads(self.original_event)
        else:
            return dict()

    @staticmethod
    def find_all_by(params, page=1, page_size=10):
        query = AbstractEvent.query

        if params.get('start_date') and params.get('end_date'):
            query = query.filter(Event.date >= params.get('start_date'))
            query = query.filter(Event.date <= params.get('end_date'))

        if params.get('region'):
            query = query.filter(Event.region == params.get('region'))

        if params.get('account'):
            query = query.filter(Event.account == params.get('account'))

        if params.get('type'):
            query = query.filter(Event.resource_type == params.get('type'))

        if params.get('action'):
            query = query.filter(Event.action == params.get('action'))

        if params.get('resource_id'):
            query = query.filter(Event.resource_id == params.get('resource_id'))

        return query.order_by(Event.date.desc()).paginate(1 if page is None else page, min(page_size, 100))

    @staticmethod
    def get_resource_type(event_key):
        raise NotImplementedError()

    def _get_resource_id(self):
        return self.resource_id

    def _get_resource_name(self):
        if self.resource_id:
            name = self._get_resource_name_from_api()
            if name:
                return name
            else:
                query = AbstractEvent.query.filter_by(resource_id=self.resource_id, resource_type=self.resource_type)
                event = query.filter(Event.resource_name.isnot(None)).first()
                return event.resource_name if event else None

    def _get_action(self, event_key):
        raise NotImplementedError()

    def _get_resource_name_from_api(self):
        raise NotImplementedError()

    @property
    def acs(self):
        return CloudstackClientFactory.get_instance(self.region)


class Event(AbstractEvent):

    @staticmethod
    def get_resource_type(event_key):
        return event_key.split('.', 1)[0]

    def _get_action(self, event_key):
        return event_key.split(self.get_resource_type(event_key) + ".")[1]

    def _get_resource_name_from_api(self):
        return None


class NetworkEvent(Event):

    def _get_resource_name_from_api(self):
        project_id = self.details.get('Project')
        if project_id:
            params = {'id': self.resource_id, 'listall': 'true', 'projectid': project_id}
            networks = self.acs.listNetworks(params).get('network')
            return networks[0].get('name') if networks else None

    @staticmethod
    def get_resource_type(event_key):
        return 'NETWORK'


class VirtualMachineEvent(Event):

    def _get_resource_name_from_api(self):
        vms = self.acs.listVirtualMachines({'id': self.resource_id, 'listall': 'true'}).get('virtualmachine')
        if not vms:
            # fallback for getting VM data when operating on VM that is a router.
            # This case is used only when a router is migrated and the resulted event is a VM.MIGRATE
            # but the VM is not accessible from the listVirtualmachines command
            vms = self.acs.listRouters({'id': self.resource_id, 'listall': 'true'}).get('router')
        return vms[0].get('name') if vms else None

    @staticmethod
    def get_resource_type(event_key):
        return 'VM'


class VirtualMachineSnapshotEvent(Event):

    def _get_resource_id(self):
        if self.action == 'DELETE':
            return self.details.get("VMSnapshot")
        else:
            return self.details.get("VirtualMachine")

    def _get_resource_name_from_api(self):
        vms = self.acs.listVirtualMachines({'id': self.resource_id, 'listall': 'true'}).get('virtualmachine')
        return vms[0].get('name') if vms else None

    @staticmethod
    def get_resource_type(event_key):
        return 'VMSNAPSHOT'


class VolumeEvent(Event):

    def _get_resource_name_from_api(self):
        volumes = self.acs.listVolumes({'id': self.resource_id, 'listall': 'true'}).get('volume')
        return volumes[0].get('name') if volumes else None

    @staticmethod
    def get_resource_type(event_key):
        return 'VOLUME'


class LoadBalancerEvent(Event):

    def _get_resource_id(self):
        if self.action == 'STICKINESSPOLICY.CREATE':
            return self.details.get("FirewallRule")
        return super(LoadBalancerEvent, self)._get_resource_id()

    def _get_resource_name_from_api(self):
        lbs = self.acs.listLoadBalancerRules({'id': self.resource_id, 'listall': 'true'}).get('loadbalancerrule')
        return lbs[0].get('name') if lbs else None

    @staticmethod
    def get_resource_type(event_key):
        return 'LB'


class ProjectEvent(Event):

    def _get_resource_name_from_api(self):
        projects = self.acs.listProjects({'id': self.resource_id, 'listall': 'true'}).get('project')
        return projects[0].get('name') if projects else None

    @staticmethod
    def get_resource_type(event_key):
        return 'PROJECT'


class ServiceOfferingEvent(Event):

    def _get_resource_name_from_api(self):
        offerings = self.acs.listServiceOfferings({'id': self.resource_id, 'listall': 'true'}).get('serviceoffering')
        return offerings[0].get('name') if offerings else None

    @staticmethod
    def get_resource_type(event_key):
        return 'SERVICE.OFFERING'


class RouterEvent(Event):

    def _get_resource_id(self):
        return self.details.get("VirtualMachine")

    def _get_resource_name_from_api(self):
        routers = self.acs.listRouters({'id': self.resource_id, 'listall': 'true'}).get('router')
        return routers[0].get('name') if routers else None

    @staticmethod
    def get_resource_type(event_key):
        return 'ROUTER'


class SSVMEvent(Event):

    def _get_resource_id(self):
        return self.details.get("VirtualMachine")

    def _get_resource_name_from_api(self):
        routers = self.acs.listSystemVms({'id': self.resource_id, 'listall': 'true'}).get('systemvm')
        return routers[0].get('name') if routers else None

    @staticmethod
    def get_resource_type(event_key):
        return 'SSVM'


class ConsoleProxyEvent(SSVMEvent):

    @staticmethod
    def get_resource_type(event_key):
        return 'PROXY'


class EventFactory(object):

    @staticmethod
    def create_event(event_key, **kwargs):
        for cls in EventFactory._get_all_subclasses(Event):
            if event_key.startswith(cls.get_resource_type(event_key) + "."):
                return cls(event_key, **kwargs)
        return Event(event_key, **kwargs)

    @staticmethod
    def _get_all_subclasses(cls):
        all_subclasses = []
        for subclass in cls.__subclasses__():
            all_subclasses.append(subclass)
            all_subclasses.extend(EventFactory._get_all_subclasses(subclass))
        return all_subclasses


class EventSchema(Schema):

    details = fields.Dict()

    class Meta:
        fields = (
            "id", "action", "resource_type", "resource_id", "resource_name",
            "description", "username", "account", "date_time", "region", "details"
        )
