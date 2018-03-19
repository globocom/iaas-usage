from flask import request
from flask_restful import reqparse
from flask_restful import Resource
from app.auth.utils import required_login
from app.cloudstack.cloudstack_base_resource import handle_errors
from app.usage_record.elk import ELKClient
from app.usage_record.usage_record_builder import UsageRecordBuilder


class UsageRecordResource(Resource):

    @required_login
    @handle_errors
    def get(self, region):
        parser = reqparse.RequestParser()
        parser.add_argument('start_date', required=True, type=str, help='start_date should be informed')
        parser.add_argument('end_date', required=True, type=str, help='end_date should be informed')
        parser.add_argument('account_name')
        args = parser.parse_args(req=request)

        start = args.get('start_date')
        end = args.get('end_date')
        account = args.get('account_name')

        usage_records = ELKClient().find_usage_records(region, account, start, end)
        return UsageRecordBuilder(region).build_usage_report(usage_records, start, end)