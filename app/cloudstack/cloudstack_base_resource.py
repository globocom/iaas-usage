from ConfigParser import SafeConfigParser
import os
from flask_restful import Resource
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