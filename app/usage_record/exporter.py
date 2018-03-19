import datetime
import json
import requests

from app import app
from app.projects.models import Project
from app.usage_record.elk import ELKClient
from app.usage_record.usage_record_builder import UsageRecordBuilder


class UsageRecordExporter(object):

    def __init__(self, region, date):
        self.region = region
        self.date = date
        if self.date is None:
            self.date = (datetime.date.today() - datetime.timedelta(days=1))
        self.elk_client = ELKClient()

    def export(self):
        try:
            self.log("Starting usage export. Date: " + str(self.date))

            date_str = self.date.isoformat()
            usage_records = ELKClient().find_usage_records(self.region, None, date_str, date_str)
            records = UsageRecordBuilder(self.region).build_usage_report(usage_records, date_str, date_str)

            base_document = self.create_base_document()
            records_grouped_by_project = dict()
            for record in records['usage']:
                record_list = records_grouped_by_project.get(record['project_id'], [])
                if not record_list:
                    records_grouped_by_project[record['project_id']] = record_list
                record_list.append(record)

            for project_id, record_list in records_grouped_by_project.iteritems():
                project = Project.find_by_uuid(project_id)
                base_document['distribuicao'].append(self.create_distribution(project, record_list))

            self._send(base_document)
        except:
            self.log("Error", 'exception')

    def create_base_document(self):
        return {
            "origem": {
            "abertura": self.date.strftime('%Y-%m-%d-00:00:00'),
            "fechamento": self.date.strftime('%Y-%m-%d-23:59:59'),
            "provedor-de-cloud": "cloudstack",
            "ambiente": app.config['REGIONS'].get(self.region),
                "dominio": "ROOT"
            },
            "distribuicao": list()
        }

    def create_distribution(self, project, records):
        distribution = {
            'projeto': {"id": project.uuid, "nome": project.name},
            'processo': {"id": project.process_id},
            'consumo-detalhado': project.detailed_usage,
            'utilizacao': list()
        }

        if project:
            defaul_business_service = app.config['USAGE_NOT_CLASSIFIED_BUSINESS_SERVICE_ID']
            if project.business_service_id:
                distribution['servico-de-negocio'] = {"id": project.business_service_id}
            else:
                distribution['servico-de-negocio'] = {"id": defaul_business_service}

            if project.component_id:
                distribution['componente'] = {"id": project.component_id}

            if project.sub_component_id:
                distribution['sub-componente'] = {"id": project.sub_component_id}

            if project.product_id:
                distribution['produto'] = {"id": project.product_id}

            if project.client_id:
                distribution['cliente'] = {"id": project.client_id}

        for record in records:
            ram = int(record.get('offering_ram'))
            cores = int(record.get('offering_cpu'))
            vm_count = record['usage'] / 24

            utilization = self.find_utilization(distribution['utilizacao'], cores, ram)
            if utilization:
                utilization["quantidade"] += vm_count
            else:
                distribution['utilizacao'].append({
                    "cpu-cores": cores,
                    "memoria": ram,
                    "quantidade": vm_count,
                })
        return distribution

    def find_utilization(self, utilization_list, cores, ram):
        for utilization in utilization_list:
            if utilization["cpu-cores"] == cores and utilization["memoria"] == ram:
                return utilization

    def _send(self, payload, retry_count=0):
        json_payload = json.dumps(payload)
        headers = {'Content-type': 'application/json'}
        response = requests.post(app.config['BILLING_COLLECTOR_ENDPOINT'], data=json_payload, headers=headers)
        if response.status_code == 201 or response.status_code == 200:
            self.log("Usage report sent successfully: %s " % response.content)
            return
        else:
            self.log('Error sending data to enpoint', 'error')
            self.log('Status: %s' % response.status_code, 'error')
            app.logger.error('Request: {}'.format(json_payload))
            app.logger.error('Response: {}'.format(response.content))
            if retry_count < 3:
                self._send(payload, retry_count + 1)

    def log(self, message, level='info'):
        getattr(app.logger, level)('[%s] %s' % (self.region.upper(), message))
