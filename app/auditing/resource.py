import argparse
from datetime import datetime
from flask import request
from flask_restful import Resource, abort
from flask_restful import reqparse
from app.auth.utils import required_login
from app.cloudstack.cloudstack_base_resource import handle_errors
from app.auditing.models import Event, EventSchema


class AuditingEventResource(Resource):

    @required_login
    @handle_errors
    def get(self, region, id):
        result = Event.query.get(id)
        if not result:
            abort(404)
        return EventSchema().dump(result).data


class AuditingEventListResource(Resource):

    @required_login
    @handle_errors
    def get(self, region):
        args = self._parse_args()
        result = Event.find_all_by(dict(args, **{'region' : region}), args.page, args.page_size)
        return {'count': result.total, 'events': EventSchema(many=True).dump(result.items).data}

    def _parse_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument('page', required=False, type=int)
        parser.add_argument('page_size', required=False, type=int)
        parser.add_argument('start_date', required=False, type=self._is_valid_date)
        parser.add_argument('end_date', required=False, type=self._is_valid_date)
        return parser.parse_args(req=request)

    @staticmethod
    def _is_valid_date(date_str):
        try:
            return datetime.strptime(date_str, '%d/%m/%Y %H:%M:%S')
        except ValueError:
            msg = "Not a valid date: '{0}'.".format(date_str)
            raise argparse.ArgumentTypeError(msg)
