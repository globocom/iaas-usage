from app.cloudstack.cloudstack_base_resource import CloudstackResource
import app


class UserResource(CloudstackResource):

    def get(self, region, id):
        response = self.get_cloudstack(region).listUsers({"id": id})

        if response.get('errortext') is not None:
            app.logger.error("Error while retrieving data from cloudstack: %s" % response['errortext'])
            return {"message": response['errortext']}, 400

        return self._to_json(response)

    def _to_json(self, response):
        if response is not None and response.get('count') is not None:
            return [
                {
                    "id": user["id"], "username": user["username"],
                    "account_name": user["account"], "domain_id": user["domainid"]
                }
                for user in response['user']
            ]
        else:
            return []
