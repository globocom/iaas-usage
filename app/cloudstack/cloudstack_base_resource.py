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

        if os.path.isfile("~/.cloudmonkey/config"):
            app.logger.debug("Loading configs from cloudmonkey/config")
            parser = SafeConfigParser()
            parser.read(os.path.expanduser('~/.cloudmonkey/config'))

            if parser.has_section(region):
                apikey = parser.get(region, 'apikey')
                api_url = parser.get(region, 'url')
                secretkey = parser.get(region, 'secretkey')
                verifysslcert = parser.getboolean(region, 'verifysslcert')
            else:
                raise EnvironmentError("Cloudmonkey config does not have the region " + region)

        else:
            region = region.upper()
            app.logger.debug("Loading from env variables: " + region)

            apikey = os.getenv(region + '_APIKEY', '')
            secretkey = os.getenv(region + '_SECRETKEY', '')
            api_url = os.getenv(region + '_URL', '')
            verifysslcert = os.getenv(region + '_VERIFYSSLCERT', '').upper() == 'TRUE'

            if apikey == '' or secretkey == '' or api_url == '':
                app.logger.exception("Variables values for region " + region + " SIZE APIKEY: " + str(len(apikey)) + ", SIZE SECRETKEY: " + str(len(secretkey)) + ", URL: " + api_url + ", VERIFYSSLCERT: " + str(verifysslcert))
                raise EnvironmentError("Should define env variables for region: {0} ( {0}_APIKEY, {0}_SECRETKEY, {0}_URL, {0}_VERIFYSSLCERT )".format(region))

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
