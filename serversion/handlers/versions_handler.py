from aiohttp import web, ClientSession
from aiohttp.abc import Request
import ssl


# Point to the internal API server hostname
APISERVER="https://kubernetes.default.svc"

# Path to ServiceAccount token
SERVICEACCOUNT="/var/run/secrets/kubernetes.io/serviceaccount"

# Path to read this Pod's namespace
NAMESPACE=f"{SERVICEACCOUNT}/namespace"

# Path to read the ServiceAccount bearer token
TOKEN=f"{SERVICEACCOUNT}/token"

# Reference the internal certificate authority (CA)
CACERT=f"{SERVICEACCOUNT}/ca.crt"

# Explore the API with TOKEN
# curl --cacert ${CACERT} --header "Authorization: Bearer ${TOKEN}" -X GET ${APISERVER}/api


class VersionsView(web.View):
    def __init__(self, request: Request) -> None:
        """
        This constructor is being fired per request
        :param request:
        """
        super().__init__(request)

    # def _get_namespace(self):
    #     namespace = 'deafult'
    #     try:
    #         with open(NAMESPACE, 'r') as opened_file:
    #             namespace = opened_file.read()
    #     except FileNotFoundError:
    #         print("file not exist")
    #     return namespace

    def _get_token(self):
        token = 'missing token'
        try:
            with open(TOKEN, 'r') as opened_file:
                token = opened_file.read()
        except FileNotFoundError:
            print("file not exist")
        return token

    def _get_namespaces(self, namespaces_info):
        namespaces = set()
        items = namespaces_info.get("items", [])
        for namespace in items:
            metadata = namespace.get("metadata", {})
            name = metadata.get("name")
            namespaces.add(name)
        return namespaces

    def _get_versioned_images(self, pod_info):
        versioned_images = {}
        spec = pod_info.get("spec", {})
        containers = spec.get("containers", [])
        for container in containers:
            name = container.get("name")
            image = container.get("image")
            versioned_images[name] = image
        return versioned_images

    async def get(self):
        app = self.request.app
        token = self._get_token()
        # namespace = self._get_namespace()
        headers = {
            "Authorization": f"Bearer {token}",
        }
        #TODO: support compression
        sslcontext = ssl.create_default_context(cafile=CACERT)
        cluster_versions = dict()
        async with ClientSession() as client:
            response = await client.get(f"{APISERVER}/api/v1/namespaces",   
                                        headers=headers,
                                        ssl=sslcontext)
            namespaces_info = await response.json()
            namespaces = self._get_namespaces(namespaces_info)
            versions = dict()
            #TODO: in parallel
            for namespace in namespaces:
                response = await client.get(f"{APISERVER}/api/v1/namespaces/{namespace}/pods",   
                                            headers=headers,
                                            ssl=sslcontext)
                pods_info = await response.json()
                versions = list(map(lambda item: self._get_versioned_images(item), pods_info.get("items", [])))
                cluster_versions[namespace] = versions
        return web.json_response(cluster_versions)
