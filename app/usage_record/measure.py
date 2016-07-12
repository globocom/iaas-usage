from elasticsearch_dsl import Search
from elasticsearch_dsl.connections import connections
from app import app
from dateutil.parser import parse
from measures import Measure


class MeasureClient:

    def __init__(self):
        es_url = app.config['ELASTICSEARCH_URL']
        es_port = app.config['ELASTICSEARCH_PORT']
        logstash_host = app.config['LOGSTASH_HOST']
        logstash_port = int(app.config['LOGSTASH_PORT'])

        self.measure = Measure(app.config['ELASTICSEARCH_CLIENT'], (logstash_host, logstash_port))
        self.es = connections.create_connection(hosts=[es_url + ':' + es_port])

    def create(self, data):
        self.measure.count(app.config['ELASTICSEARCH_TYPE'], dimensions=data)

    def find(self, region, account, start, end):
        s = Search(using=self.es, index=app.config['ELASTICSEARCH_INDEX'], doc_type=app.config['ELASTICSEARCH_TYPE'])
        s = s.filter('term', region=region)
        if account is not None:
            s = s.filter('term', account=account)
        s = s.filter('range', date={
            'gte': parse(start).date().isoformat(),
            'lte': parse(end).date().isoformat()
        })[0:0]

        s.aggs.bucket('by_project', 'terms', field='project.raw', size=0) \
            .bucket('by_type', 'terms', field='usagetype.raw') \
            .bucket('by_offering', 'terms', field='offeringid.raw') \
            .metric('rawusage_sum', 'sum', field='rawusage')

        return s.execute().aggregations.to_dict()

    def delete(self, region, date):
        index = app.config['ELASTICSEARCH_INDEX']
        doc_type = app.config['ELASTICSEARCH_TYPE']

        s = Search(using=self.es, index=app.config['ELASTICSEARCH_INDEX'], doc_type=doc_type) \
            .filter('term', region=region) \
            .filter('term', date=date)
        self.es.delete_by_query(index=index, doc_type=doc_type, body=s.to_dict())

    def health(self):
        return self.es.cluster.health()
