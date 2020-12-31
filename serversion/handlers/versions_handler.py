from typing import Dict
from aiohttp import web, ClientSession
from aiohttp.abc import Request
import base64
import gzip
import json
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

    def _get_pod_name(self, pod_info):
        pod_name = None
        generate_name = pod_info.get("metadata", {}).get("generateName")
        if generate_name is not None:
            pod_name = "-".join(generate_name.split("-")[:-2])
        else:
            pod_name = pod_info.get("metadata", {}).get("name")
        return pod_name

    def _get_versioned_images(self, pod_info):
        versioned_images = {}
        spec = pod_info.get("spec", {})
        containers = spec.get("containers", [])
        for container in containers:
            name = container.get("name")
            image = container.get("image")
            versioned_images[name] = image
        return {
            "containers": versioned_images,
        }

    async def get_helm_data(self, client):
        helm_data = dict()
        response = await client.get(f"{APISERVER}/api/v1/secrets",
                                    headers=self.headers,
                                    ssl=self.sslcontext)
        secrets_info = await response.json()
        items = secrets_info.get("items", [])
        for item in items:
            if item.get("type") == "helm.sh/release.v1":
                release: str = item.get("data", {}).get("release", "")
                compressed_data: bytes = base64.b64decode(base64.b64decode(release))
                uncompressed: str = gzip.decompress(compressed_data).decode()
                chart_data: Dict = json.loads(uncompressed)
                metadata: Dict = chart_data.get("chart", {}).get("metadata", {})
                namespace: str = chart_data.get("namespace")
                name = metadata.get("name")
                if helm_data.get(namespace) is None:
                    helm_data[namespace] = dict()
                helm_data[namespace][name] = {
                    "version": metadata.get("version"),
                    "appVersion": metadata.get("appVersion"),
                }
        return helm_data

    async def get(self):
        app = self.request.app
        token = self._get_token()
        # namespace = self._get_namespace()
        self.headers = {
            "Authorization": f"Bearer {token}",
        }
        #TODO: support compression
        self.sslcontext = ssl.create_default_context(cafile=CACERT)
        cluster_versions = dict()
        async with ClientSession() as client:
            response = await client.get(f"{APISERVER}/api/v1/namespaces",   
                                        headers=self.headers,
                                        ssl=self.sslcontext)
            namespaces_info = await response.json()
            namespaces = self._get_namespaces(namespaces_info)
            versions = dict()
            #TODO: in parallel
            for namespace in namespaces:
                response = await client.get(f"{APISERVER}/api/v1/namespaces/{namespace}/pods",   
                                            headers=self.headers,
                                            ssl=self.sslcontext)
                pods_info = await response.json()
                versions = {self._get_pod_name(item): self._get_versioned_images(item) for item in pods_info.get("items", [])}
                cluster_versions[namespace] = versions
            helm = await self.get_helm_data(client)
            for ns, charts in helm.items():
                for chart, versions in charts.items():
                    cluster_versions[ns][chart].update(versions)
        return web.json_response(cluster_versions)
