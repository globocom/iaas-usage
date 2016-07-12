import socket

from flask_restful import Resource
from sqlalchemy import text
from app import db, app
from app.cloudstack.cloudstack_base_resource import CloudstackClientFactory
from app.usage_record.measure import MeasureClient


class HealthResource(Resource):

    def get(self):
        es_ok = self._test_elasticsearch()
        acs_ok = self._test_cloudstack()
        db_ok = self._test_database()
        response = self._build_health_check(acs_ok, db_ok, es_ok)
        return response, (200 if response.get('healthy') else 500)

    def _build_health_check(self, acs_ok, db_ok, es_ok):
        everything_ok = es_ok and acs_ok and db_ok
        response = {
            'healthy': everything_ok,
            'hostname': socket.getfqdn(),
            'services': {
                'elasticsearch': es_ok,
                'cloudstack': acs_ok,
                'database': db_ok,
            }
        }
        return response

    def _test_elasticsearch(self):
        cluster_status = ''
        try:
            cluster_status = MeasureClient().health().get('status')
            if cluster_status not in ['green', 'yellow']:
                raise Exception()
            else:
                return True
        except:
            app.logger.exception("Error connecting to Elasticsearch: cluster status = %s" % cluster_status)
            return False

    def _test_cloudstack(self):
        for region in app.config['REGION_LIST']:
            try:
                CloudstackClientFactory.get_instance(region).listDomains({'listall': 'true'})
            except:
                app.logger.exception("Error connecting to Cloudstack region %s" % region)
                return False
        return True

    def _test_database(self):
        try:
            db.engine.execute(text('select 1'))
            return True
        except:
            app.logger.exception("Error connecting to database")
            return False

