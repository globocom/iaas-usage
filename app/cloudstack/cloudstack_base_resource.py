from ConfigParser import SafeConfigParser
from functools import wraps
import os
from flask_restful import Resource
from werkzeug.exceptions import HTTPException
from app import app
from app.cloudstack.cloudstack_client import CloudStack


class CloudstackResource(Resource):

    def get_cloudstack(self, region):
        config = self.__get_configs(region)
        return CloudStack(config['api_url'], config['apikey'], config['secretkey'], config['verifysslcert'])

    def __get_configs(self, region):
        parser = SafeConfigParser()
        #TODO: change to read config from system variables
        parser.read(os.path.expanduser('~/.cloudmonkey/config'))

        if parser.has_section(region):
            apikey = parser.get(region, 'apikey')
            api_url = parser.get(region, 'url')
            secretkey = parser.get(region, 'secretkey')
            verifysslcert = parser.getboolean(region, 'verifysslcert')

        return { "apikey": apikey, "api_url": api_url, "secretkey": secretkey, "verifysslcert": verifysslcert }


def handle_errors(view_func):
    def _decorator(*args, **kwargs):
        try:
            response = view_func(*args, **kwargs)
            return response
        except HTTPException:
            raise
        except Exception:
            app.logger.exception("Internal error")
            return {"message": "Internal server error"}, 500
    return wraps(view_func)(_decorator)
