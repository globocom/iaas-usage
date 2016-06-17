from flask import json
from dateutil.parser import parse
from app import db, cache, app
from app.auditing.models import Event
from app.auditing.rabbit_mq_client import RabbitMQClient
from app.cloudstack.cloudstack_base_resource import CloudstackResource


class CloudstackEventReader:

    def __init__(self, region):
        self.region = region
        self.acs = CloudstackResource().get_cloudstack(region)
        self.rabbit_client = RabbitMQClient()

    def read_events(self):
        self.rabbit_client.start_consuming(self._save_event)

    def _save_event(self, event_json_string):
        event_data = json.loads(event_json_string)

        if event_data['status'] == 'Completed' and self.user_is_not_system(event_data.get('user')):
            event = self._create_event(event_data, event_json_string)
            db.session.add(event)
            db.session.commit()

    def _create_event(self, event_data, event_json_string):
        event = Event(
            event_data.get('event'),
            event_data.get('entityuuid'),
            event_data.get('description'),
            self._get_user_name(event_data.get('user')),
            self._get_account_name(event_data.get('account')),
            parse(event_data.get('eventDateTime')).replace(tzinfo=None),
            self.region,
            event_json_string
        )
        return event

    def _get_user_name(self, user_uuid):
        decorator = cache.cached(timeout=app.config['USAGE_CACHE_TIME'], key_prefix='user_' + user_uuid)
        return decorator(lambda: self.acs.listUsers({'id': user_uuid}).get('user'))()[0].get('username')

    def _get_account_name(self, account_uuid):
        decorator = cache.cached(timeout=app.config['USAGE_CACHE_TIME'], key_prefix='account_' + account_uuid)
        return decorator(lambda: self.acs.listAccounts({'id': account_uuid}).get('account'))()[0].get('name')

    def user_is_not_system(self, user_uuid):
        return user_uuid != '49337c3e-9db2-11e5-8fbd-2c40bbe95f1f'  # TODO: refactory system user
