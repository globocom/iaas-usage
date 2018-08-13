import os
from flask import json
from dateutil.parser import parse
from app import db, cache, app
from app.auditing.models import EventFactory
from app.auditing.rabbit_mq_client import RabbitMQClient
from app.cloudstack.cloudstack_base_resource import CloudstackClientFactory


class CloudstackEventReader(object):

    def __init__(self, region):
        self.region = region
        self.acs = CloudstackClientFactory.get_instance(region)
        host = os.getenv(region.upper() + '_EVENT_QUEUE_HOST')
        port = int(os.getenv(region.upper() + '_EVENT_QUEUE_PORT', 5672))
        username = os.getenv(region.upper() + '_EVENT_QUEUE_USER')
        password = os.getenv(region.upper() + '_EVENT_QUEUE_PASSWORD')
        self.rabbit_client = RabbitMQClient(host, port, username, password)

    def read_events(self):
        self.log("Event processing started")
        self.rabbit_client.start_consuming(self._save_event)
        self.log("Event processing ended")

    def _save_event(self, event_json_string):
        try:
            event_data = json.loads(event_json_string)
            if event_data['status'] == 'Completed':
                self.log("Saving event %s" % event_json_string, 'debug')

                if self._verify_eventdata(event_data):
                    event = self._create_event(event_data, event_json_string)
                    db.session.add(event)
                    db.session.commit()
        except Exception, e:
            self.log("Error when trying to save event: %s" % event_json_string,  'error')
            raise e

    def _create_event(self, event_data, event_json_string):

        params = dict(
            resource_id=event_data.get('entityuuid'),
            description=event_data.get('description'),
            username=self._get_user_name(event_data.get('user')),
            account=self._get_account_name(event_data.get('account')),
            date=parse(event_data.get('eventDateTime')).replace(tzinfo=None),
            region=self.region,
            original_event=event_json_string
        )
        return EventFactory.create_event(event_key=event_data.get('event'), **params)

    def _get_user_name(self, user_uuid):
        def get_user_name():
            users = self.acs.listUsers({'id': user_uuid, 'listall': 'true'}).get('user')
            if users:
                return users[0].get('username')

        decorator = cache.cached(timeout=app.config['USAGE_CACHE_TIME'], key_prefix='user_' + user_uuid)
        return decorator(get_user_name)()

    def _get_account_name(self, account_uuid):
        def get_account_name():
            accounts = self.acs.listAccounts({'id': account_uuid, 'listall': 'true'}).get('account')
            if accounts:
                return accounts[0].get('name')

        decorator = cache.cached(timeout=app.config['USAGE_CACHE_TIME'], key_prefix='account_' + account_uuid)
        return decorator(get_account_name)()

    def log(self, message, level='info'):
        getattr(app.logger, level)(('[%s] ' % self.region.upper()) + message)

    def _verify_eventdata(self, event_data):
        if event_data.get('entityuuid') is None:
            return False
        if event_data.get('description') is None:
            return False
        if event_data.get('user') is None:
            return False
        if event_data.get('account') is None:
            return False
        if event_data.get('eventDateTime') is None:
            return False
        return True
