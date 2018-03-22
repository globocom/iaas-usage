import json
import socket
from elasticsearch_dsl import Search
from elasticsearch_dsl.connections import connections
from app import app
from dateutil.parser import parse


class ELKClient:

    def __init__(self):
        es_url = app.config['ELASTICSEARCH_URL']
        es_port = app.config['ELASTICSEARCH_PORT']
        self.es = connections.create_connection(hosts=[es_url + ':' + es_port])
        self.logstash_host = app.config['LOGSTASH_HOST']
        self.logstash_port = int(app.config['LOGSTASH_PORT'])

    def create_usage_record(self, data):
        message = {
            'client': app.config['ELASTICSEARCH_CLIENT'],
            'metric': app.config['ELASTICSEARCH_TYPE'],
        }
        data.update(message)

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, msg:
            app.logger.error("Error creating socket to logstash: %s" % msg)
            raise Exception("Error sending usage record to Logstash")

        try:
            sock.connect((self.logstash_host, self.logstash_port))
        except socket.error, msg:
            app.logger.error("Error sending TCP message to logstash: %s" % msg)
            raise Exception("Error sending usage record to Logstash")

        sock.send(json.dumps(data).encode('utf-8'))

    def find_usage_records(self, region, account, start, end):
        s = Search(using=self.es, index=app.config['ELASTICSEARCH_INDEX'], doc_type=app.config['ELASTICSEARCH_TYPE'])
        s = s.filter('term', region=region)
        if account is not None:
            s = s.filter('term', account=account)
        s = s.filter('range', date={
            'gte': parse(start).date().isoformat(),
            'lte': parse(end).date().isoformat()
        })[0:0]

        s.aggs.bucket('by_project', 'terms', field='projectid.raw', size=0) \
            .bucket('by_type', 'terms', field='usagetype.raw') \
            .bucket('by_offering', 'terms', field='offering_struct.raw') \
            .metric('rawusage_sum', 'sum', field='rawusage')

        return s.execute().aggregations.to_dict()

    def delete_usage_records(self, region, date):
        index = app.config['ELASTICSEARCH_INDEX']
        doc_type = app.config['ELASTICSEARCH_TYPE']

        s = Search(using=self.es, index=app.config['ELASTICSEARCH_INDEX'], doc_type=doc_type) \
            .filter('term', region=region) \
            .filter('term', date=date)
        self.es.delete_by_query(index=index, doc_type=doc_type, body=s.to_dict())

    def health(self):
        return self.es.cluster.health()
