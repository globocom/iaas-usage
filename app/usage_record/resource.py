from flask import request
from flask_restful import reqparse
from flask_restful import Resource
from app.auth.utils import required_login
from app.cloudstack.cloudstack_base_resource import handle_errors
from app.usage_record.measure import MeasureClient
from app.usage_record.usage_record_builder import UsageRecordBuilder


class UsageRecordResource(Resource):

    @required_login
    @handle_errors
    def get(self, region):
        self._validate_params()
        start = self.args.get('start_date')
        end = self.args.get('end_date')
        account = self.args.get('account_name')

        usage_records = MeasureClient().find(region, account, start, end)
        return UsageRecordBuilder(region).build_usage_report(usage_records, start, end)

    def _validate_params(self):
        parser = reqparse.RequestParser()
        parser.add_argument('start_date', required=True, type=str, help='start_date should be informed')
        parser.add_argument('end_date', required=True, type=str, help='end_date should be informed')
        parser.add_argument('account_name')
        self.args = parser.parse_args(req=request)
