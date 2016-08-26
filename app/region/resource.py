from flask_restful import Resource
from app.auth.utils import required_login
from app.cloudstack.cloudstack_base_resource import handle_errors
from app.region.service import RegionService


class RegionResource(Resource):

    def __init__(self):
        self.region_service = RegionService()

    @required_login
    @handle_errors
    def get(self):
        return self.region_service.get_regions()
