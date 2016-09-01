from app import app


class RegionService(object):

    def get_regions(self):
        return app.config['REGIONS']
