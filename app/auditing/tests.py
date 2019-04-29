import unittest
from datetime import datetime, timedelta
from flask import json
from app import db, app
from mock import patch, Mock
from app.auditing.models import EventFactory, Event, VirtualMachineEvent, NetworkEvent, VolumeEvent, LoadBalancerEvent, \
    ProjectEvent, ServiceOfferingEvent, RouterEvent, VirtualMachineSnapshotEvent, SSVMEvent, ConsoleProxyEvent, \
    TemplateEvent
from app.auditing.event_reader import CloudstackEventReader


class BaseTest(unittest.TestCase):

    def setUp(self):
        db.create_all()
        mock = patch('flask_login.AnonymousUserMixin.is_authenticated').start()
        mock.return_value = True

    def tearDown(self):
        db.drop_all()
        patch.stopall()

    def _create_event(self, region='reg', account='adm', resource_id='1', event_key='USER.LOGIN', date=datetime.now()):
        return Event(
            event_key, resource_id=resource_id, description='User has logged', username='username', account=account,
            date=date, region=region, original_event='{"action":"USER.LOGIN"}'
        )


class EventFactoryTestCase(BaseTest):

    def test_create_generic_event(self):
        event = EventFactory.create_event('USER.LOGIN')
        self.assertEquals(Event, event.__class__)

    def test_create_vm_event(self):
        event = EventFactory.create_event('VM.CREATE')
        self.assertEquals(VirtualMachineEvent, event.__class__)

    def test_create_network_event(self):
        event = EventFactory.create_event('NETWORK.CREATE')
        self.assertEquals(NetworkEvent, event.__class__)

    def test_create_volume_event(self):
        event = EventFactory.create_event('VOLUME.CREATE')
        self.assertEquals(VolumeEvent, event.__class__)

    def test_create_lb_event(self):
        event = EventFactory.create_event('LB.CREATE')
        self.assertEquals(LoadBalancerEvent, event.__class__)

    def test_create_project_event(self):
        event = EventFactory.create_event('PROJECT.CREATE')
        self.assertEquals(ProjectEvent, event.__class__)

    def test_create_service_offering_event(self):
        event = EventFactory.create_event('SERVICE.OFFERING.CREATE')
        self.assertEquals(ServiceOfferingEvent, event.__class__)

    def test_create_router_event(self):
        event = EventFactory.create_event('ROUTER.REBOOT')
        self.assertEquals(RouterEvent, event.__class__)

    def test_create_snapshot_event(self):
        event = EventFactory.create_event('VMSNAPSHOT.CREATE')
        self.assertEquals(VirtualMachineSnapshotEvent, event.__class__)


class EventTestCase(BaseTest):

    def test_create_event(self):
        event = self._create_event()
        self.assertIsNotNone(event.action)
        self.assertIsNotNone(event.resource_id)
        self.assertIsNotNone(event.description)
        self.assertIsNotNone(event.username)
        self.assertIsNotNone(event.account)
        self.assertIsNotNone(event.date)
        self.assertIsNotNone(event.region)
        self.assertIsNotNone(event.original_event)
        self.assertIsNone(event.resource_name)

    def test_get_details(self):
        event = self._create_event()
        self.assertEquals('USER.LOGIN', event.details['action'])

    def test_get_date_time_formatted(self):
        event = self._create_event()
        self.assertIsNotNone(event.date_time)

    def test_get_action(self):
        event = self._create_event()
        self.assertEquals('LOGIN', event.action)

    def test_get_resource_type(self):
        event = self._create_event()
        self.assertEquals('USER', event.resource_type)

    def test_get_resource_name_from_api(self):
        event = self._create_event()
        self.assertIsNone(event._get_resource_name_from_api())

    def test_find_by_region(self):
        db.session.add(self._create_event(region='reg1'))
        db.session.add(self._create_event(region='reg2'))
        self.assertEquals(1, len(Event.find_all_by({'region': 'reg1'}).items))

    def test_find_by_account(self):
        db.session.add(self._create_event(account='account_a'))
        db.session.add(self._create_event(account='account_b'))
        self.assertEquals(1, len(Event.find_all_by({'account': 'account_b'}).items))

    def test_find_by_resource_id(self):
        db.session.add(self._create_event(resource_id='1'))
        db.session.add(self._create_event(resource_id='2'))
        self.assertEquals(1, len(Event.find_all_by({'resource_id': '2'}).items))

    def test_find_by_action(self):
        db.session.add(self._create_event(event_key='LB.CREATE'))
        db.session.add(self._create_event(event_key='LB.DELETE'))
        self.assertEquals(1, len(Event.find_all_by({'action': 'DELETE'}).items))

    def test_find_by_type(self):
        db.session.add(self._create_event(event_key='LB.CREATE'))
        db.session.add(self._create_event(event_key='VM.CREATE'))
        self.assertEquals(1, len(Event.find_all_by({'type': 'VM'}).items))

    def test_find_by_date_interval(self):
        db.session.add(self._create_event(date=datetime.now() + timedelta(days=10)))
        db.session.add(self._create_event(date=datetime.now()))

        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now() + timedelta(days=1)
        self.assertEquals(1, len(Event.find_all_by({'start_date': start_date, 'end_date': end_date}).items))

    def test_find_by_date_interval_given_no_events_on_time_range(self):
        db.session.add(self._create_event(date=datetime.now() + timedelta(days=10)))
        db.session.add(self._create_event(date=datetime.now() - timedelta(days=10)))

        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now() + timedelta(days=1)
        self.assertEquals(0, len(Event.find_all_by({'start_date': start_date, 'end_date': end_date}).items))


class VirtualMachineEventTestCase(BaseTest):

    def test_get_resource_name_from_api(self):
        self.mock_cloudstack_list_vms([{'name': 'myvm'}])
        self.assertEquals('myvm', VirtualMachineEvent('VM.CREATE', resource_id='1').resource_name)

    def test_get_resource_name_from_api_given_entity_not_found(self):
        self.mock_cloudstack_list_vms([])
        self.assertIsNone(VirtualMachineEvent('VM.CREATE', resource_id='1').resource_name)

    def test_get_resource_type(self):
        self.assertEqual('VM', VirtualMachineEvent.get_resource_type(None))

    def mock_cloudstack_list_vms(self, vms):
        list_vms_mock = Mock(
            listVirtualMachines=Mock(return_value={'virtualmachine': vms}),
            listRouters=Mock(return_value={'routers': vms})
        )
        patch('app.auditing.models.CloudstackClientFactory.get_instance').start().return_value = list_vms_mock


class NetworkEventTestCase(BaseTest):

    def test_get_resource_name_from_api(self):
        self.mock_cloudstack_list_networks([{'name': 'mynetwork'}])
        event = NetworkEvent('NETWORK.CREATE', resource_id='1', original_event='{"Project": "1"}')
        self.assertEquals('mynetwork', event.resource_name)

    def test_get_resource_name_from_api_given_entity_not_found(self):
        self.mock_cloudstack_list_networks([])
        self.assertIsNone(NetworkEvent('NETWORK.CREATE', resource_id='1').resource_name)

    def test_get_resource_type(self):
        self.assertEqual('NETWORK', NetworkEvent.get_resource_type(None))

    def mock_cloudstack_list_networks(self, networks):
        list_networks_mock = Mock(listNetworks=Mock(return_value={'network': networks}))
        patch('app.auditing.models.CloudstackClientFactory.get_instance').start().return_value = list_networks_mock


class VolumeEventTestCase(BaseTest):

    def test_get_resource_name_from_api(self):
        self.mock_cloudstack_list_volumes([{'name': 'myvolume'}])
        self.assertEquals('myvolume', VolumeEvent('VOLUME.CREATE', resource_id='1').resource_name)

    def test_get_resource_name_from_api_given_entity_not_found(self):
        self.mock_cloudstack_list_volumes([])
        self.assertIsNone(VolumeEvent('VOLUME.CREATE', resource_id='1').resource_name)

    def test_get_resource_type(self):
        self.assertEqual('VOLUME', VolumeEvent.get_resource_type(None))

    def mock_cloudstack_list_volumes(self, volumes):
        list_volumes_mock = Mock(listVolumes=Mock(return_value={'volume': volumes}))
        patch('app.auditing.models.CloudstackClientFactory.get_instance').start().return_value = list_volumes_mock


class TemplateEventTestCase(BaseTest):

    def test_get_resource_name_from_api(self):
        self.mock_cloudstack_list_templates([{'name': 'template'}])
        self.assertEquals('template', TemplateEvent('TEMPLATE.CREATE', resource_id='1').resource_name)

    def test_get_resource_name_from_api_given_entity_not_found(self):
        self.mock_cloudstack_list_templates([])
        self.assertIsNone(TemplateEvent('TEMPLATE.CREATE', resource_id='1').resource_name)

    def test_get_resource_type(self):
        self.assertEqual('TEMPLATE', TemplateEvent.get_resource_type(None))

    def mock_cloudstack_list_templates(self, templates):
        list_templates_mock = Mock(listTemplates=Mock(return_value={'template': templates}))
        patch('app.auditing.models.CloudstackClientFactory.get_instance').start().return_value = list_templates_mock


class LoadBalancerEventTestCase(BaseTest):

    def test_get_resource_name_from_api(self):
        self.mock_cloudstack_list_load_balancers([{'name': 'myloadbalancer'}])
        self.assertEquals('myloadbalancer', LoadBalancerEvent('LB.CREATE', resource_id='1').resource_name)

    def test_get_resource_name_from_api_given_entity_not_found(self):
        self.mock_cloudstack_list_load_balancers([])
        self.assertIsNone(LoadBalancerEvent('LB.CREATE', resource_id='1').resource_name)

    def test_get_resource_type(self):
        self.assertEqual('LB', LoadBalancerEvent.get_resource_type(None))

    def mock_cloudstack_list_load_balancers(self, load_balancers):
        list_loadbalancers_mock = Mock(listLoadBalancerRules=Mock(return_value={'loadbalancerrule': load_balancers}))
        patch('app.auditing.models.CloudstackClientFactory.get_instance').start().return_value = list_loadbalancers_mock


class ProjectEventTestCase(BaseTest):

    def test_get_resource_name_from_api(self):
        self.mock_cloudstack_list_projects([{'name': 'myproject'}])
        self.assertEquals('myproject', ProjectEvent('PROJECT.CREATE', resource_id='1').resource_name)

    def test_get_resource_name_from_api_given_entity_not_found(self):
        self.mock_cloudstack_list_projects([])
        self.assertIsNone(ProjectEvent('PROJECT.CREATE', resource_id='1').resource_name)

    def test_get_resource_type(self):
        self.assertEqual('PROJECT', ProjectEvent.get_resource_type(None))

    def mock_cloudstack_list_projects(self, projects):
        list_projects_mock = Mock(listProjects=Mock(return_value={'project': projects}))
        patch('app.auditing.models.CloudstackClientFactory.get_instance').start().return_value = list_projects_mock


class ServiceOfferingEventTestCase(BaseTest):

    def test_get_resource_name_from_api(self):
        self.mock_cloudstack_list_service_offerings([{'name': 'myoffering'}])
        self.assertEquals('myoffering', ServiceOfferingEvent('SERVICE.OFFERING.CREATE', resource_id='1').resource_name)

    def test_get_resource_name_from_api_given_entity_not_found(self):
        self.mock_cloudstack_list_service_offerings([])
        self.assertIsNone(ServiceOfferingEvent('SERVICE.OFFERING.CREATE', resource_id='1').resource_name)

    def test_get_action(self):
        self.mock_cloudstack_list_service_offerings([{'name': 'myoffering'}])
        event = ServiceOfferingEvent('SERVICE.OFFERING.CREATE', resource_id='1')
        self.assertEquals('CREATE', event.action)

    def test_get_resource_type(self):
        self.assertEqual('SERVICE.OFFERING', ServiceOfferingEvent.get_resource_type(None))

    def mock_cloudstack_list_service_offerings(self, offerings):
        list_offerings = Mock(listServiceOfferings=Mock(return_value={'serviceoffering': offerings}))
        patch('app.auditing.models.CloudstackClientFactory.get_instance').start().return_value = list_offerings


class RouterEventTestCase(BaseTest):

    def test_get_resource_id(self):
        self.mock_cloudstack_list_routers([])
        event = RouterEvent('ROUTER.REBOOT', resource_id=None, original_event='{"VirtualMachine": "2"}')
        self.assertEquals('2', event.resource_id)

    def test_get_resource_name_from_api(self):
        self.mock_cloudstack_list_routers([{'name': 'router'}])
        self.assertEquals('router',
                          RouterEvent('ROUTER.REBOOT', original_event='{"VirtualMachine": "2"}').resource_name)

    def test_get_resource_name_from_api_given_entity_not_found(self):
        self.mock_cloudstack_list_routers([])
        self.assertIsNone(RouterEvent('ROUTER.REBOOT', resource_id='1').resource_name)

    def test_get_resource_type(self):
        self.assertEqual('ROUTER', RouterEvent.get_resource_type(None))

    def mock_cloudstack_list_routers(self, routers):
        list_routers_mock = Mock(listRouters=Mock(return_value={'router': routers}))
        patch('app.auditing.models.CloudstackClientFactory.get_instance').start().return_value = list_routers_mock


class VirtualMachineSnapshotEventTestCase(BaseTest):

    def test_get_resource_id(self):
        self.mock_cloudstack_list_vms([])
        event = VirtualMachineSnapshotEvent('VMSNAPSHOT.CREATE', resource_id=None,
                                            original_event='{"VirtualMachine": "2"}')
        self.assertEquals('2', event.resource_id)

    def test_get_resource_name_from_api(self):
        self.mock_cloudstack_list_vms([{'name': 'vm-name'}])
        event = VirtualMachineSnapshotEvent('VMSNAPSHOT.CREATE', resource_id='1',
                                            original_event='{"VirtualMachine": "2"}')
        self.assertEquals('vm-name', event.resource_name)

    def test_get_resource_name_from_api_given_entity_not_found(self):
        self.mock_cloudstack_list_vms([])
        event = VirtualMachineSnapshotEvent('VMSNAPSHOT.CREATE', resource_id='1',
                                            original_event='{"VirtualMachine": "2"}')
        self.assertIsNone(event.resource_name)

    def test_get_resource_type(self):
        self.assertEqual('VMSNAPSHOT', VirtualMachineSnapshotEvent.get_resource_type(None))

    def mock_cloudstack_list_vms(self, vms):
        list_vms_mock = Mock(listVirtualMachines=Mock(return_value={'virtualmachine': vms}))
        patch('app.auditing.models.CloudstackClientFactory.get_instance').start().return_value = list_vms_mock


class SSVMEventTestCase(BaseTest):

    def test_get_resource_id(self):
        self.mock_cloudstack_list_systemvms([])
        event = SSVMEvent('SSVM.START', resource_id=None, original_event='{"VirtualMachine": "2"}')
        self.assertEquals('2', event.resource_id)

    def test_get_resource_name_from_api(self):
        self.mock_cloudstack_list_systemvms([{'name': 'vm-name'}])
        event = SSVMEvent('SSVM.START', resource_id='1', original_event='{"VirtualMachine": "2"}')
        self.assertEquals('vm-name', event.resource_name)

    def test_get_resource_name_from_api_given_entity_not_found(self):
        self.mock_cloudstack_list_systemvms([])
        event = SSVMEvent('SSVM.START', resource_id='1', original_event='{"VirtualMachine": "2"}')
        self.assertIsNone(event.resource_name)

    def test_get_resource_type(self):
        self.assertEqual('SSVM', SSVMEvent.get_resource_type(None))

    def mock_cloudstack_list_systemvms(self, system_vms):
        list_sys_vm_mock = Mock(listSystemVms=Mock(return_value={'systemvm': system_vms}))
        patch('app.auditing.models.CloudstackClientFactory.get_instance').start().return_value = list_sys_vm_mock


class ConsoleProxyEventTestCase(BaseTest):

    def test_get_resource_id(self):
        self.mock_cloudstack_list_systemvms([])
        event = ConsoleProxyEvent('PROXY.START', resource_id=None, original_event='{"VirtualMachine": "2"}')
        self.assertEquals('2', event.resource_id)

    def test_get_resource_name_from_api(self):
        self.mock_cloudstack_list_systemvms([{'name': 'vm-name'}])
        event = ConsoleProxyEvent('PROXY.START', resource_id='1', original_event='{"VirtualMachine": "2"}')
        self.assertEquals('vm-name', event.resource_name)

    def test_get_resource_name_from_api_given_entity_not_found(self):
        self.mock_cloudstack_list_systemvms([])
        event = ConsoleProxyEvent('PROXY.START', resource_id='1', original_event='{"VirtualMachine": "2"}')
        self.assertIsNone(event.resource_name)

    def test_get_resource_type(self):
        self.assertEqual('PROXY', ConsoleProxyEvent.get_resource_type(None))

    def mock_cloudstack_list_systemvms(self, system_vms):
        list_sys_vm_mock = Mock(listSystemVms=Mock(return_value={'systemvm': system_vms}))
        patch('app.auditing.models.CloudstackClientFactory.get_instance').start().return_value = list_sys_vm_mock


class StickinessPolicyEventTestCase(BaseTest):

    def test_get_resource_id(self):
        self.mock_cloudstack_list_systemvms([])
        event = ConsoleProxyEvent('PROXY.START', resource_id=None, original_event='{"VirtualMachine": "2"}')
        self.assertEquals('2', event.resource_id)

    def test_get_resource_name_from_api(self):
        self.mock_cloudstack_list_systemvms([{'name': 'vm-name'}])
        event = ConsoleProxyEvent('PROXY.START', resource_id='1', original_event='{"VirtualMachine": "2"}')
        self.assertEquals('vm-name', event.resource_name)

    def test_get_resource_name_from_api_given_entity_not_found(self):
        self.mock_cloudstack_list_systemvms([])
        event = ConsoleProxyEvent('PROXY.START', resource_id='1', original_event='{"VirtualMachine": "2"}')
        self.assertIsNone(event.resource_name)

    def test_get_resource_type(self):
        self.assertEqual('PROXY', ConsoleProxyEvent.get_resource_type(None))

    def mock_cloudstack_list_systemvms(self, system_vms):
        list_sys_vm_mock = Mock(listSystemVms=Mock(return_value={'systemvm': system_vms}))
        patch('app.auditing.models.CloudstackClientFactory.get_instance').start().return_value = list_sys_vm_mock


class AuditingEventResourceTestCase(BaseTest):

    def setUp(self):
        super(AuditingEventResourceTestCase, self).setUp()
        self.app = app.test_client()
        db.session.add(self._create_event())

    def test_get_event(self):
        response = self.app.get('/api/v1/region/auditing_event/1')
        self.assertEquals(200, response.status_code)
        self.assertEquals(1, json.loads(response.data)['id'])

    def test_get_event_given_event_not_found(self):
        response = self.app.get('/api/v1/region/auditing_event/999')
        self.assertEquals(404, response.status_code)


class AuditingEventListResourceTestCase(BaseTest):

    def setUp(self):
        super(AuditingEventListResourceTestCase, self).setUp()
        self.app = app.test_client()
        db.session.add(self._create_event())
        db.session.add(self._create_event())

    def test_list_events(self):
        response = self.app.get('/api/v1/reg/auditing_event/')
        self.assertEquals(200, response.status_code)
        self.assertEquals(2, len(json.loads(response.data)['events']))
        self.assertEquals(2, json.loads(response.data)['count'])

    def test_list_events_filtering_by_date(self):
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now() + timedelta(days=1)
        query = {'start_date': start_date.strftime('%Y-%m-%d'), 'end_date': end_date.strftime('%Y-%m-%d')}

        response = self.app.get('/api/v1/reg/auditing_event/', query_string=query)
        self.assertEquals(200, response.status_code)
        self.assertEquals(2, len(json.loads(response.data)['events']))
        self.assertEquals(2, json.loads(response.data)['count'])

    def test_list_events_given_invalid_date_format(self):
        response = self.app.get('/api/v1/reg/auditing_event/?start_date=2016/01/13')
        self.assertEquals(400, response.status_code)
        self.assertEquals("Not a valid date: '2016/01/13'.", json.loads(response.data)['message'])


class CloudstackEventReaderTestCase(BaseTest):

    def setUp(self):
        super(CloudstackEventReaderTestCase, self).setUp()
        self.mock_cloudstack()
        self.mock_rabbitmq_client()

    def test_save_event(self):
        CloudstackEventReader('reg')._save_event(self._get_event_json_string())
        events = Event.query.all()
        self.assertEquals(1, len(events))

    def test_save_event_given_exception_thrown(self):
        try:
            CloudstackEventReader('reg')._save_event(None)
            self.fail()
        except:
            pass

    def test_save_event_given_not_completed_event(self):
        CloudstackEventReader('reg')._save_event(self._get_event_json_string(status='Scheduled'))
        events = Event.query.all()
        self.assertEquals(0, len(events))

    def _get_event_json_string(self, status='Completed'):
        return (
                    '{"eventDateTime":"2016-07-18 16:08:00 -0300","status":"%s","description":"user has logged i","event":"USER.LOGIN","account":"1","user":"1"}' % status)

    def mock_cloudstack(self):
        acs_mock = Mock(listAccounts=Mock(return_value={'account': []}), listUsers=Mock(return_value={'user': []}))
        patch('app.auditing.models.CloudstackClientFactory.get_instance').start().return_value = acs_mock

    def mock_rabbitmq_client(self):
        patch('app.auditing.event_reader.RabbitMQClient').start()
