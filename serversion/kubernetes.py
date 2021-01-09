import base64
import gzip
import json
import os
import ssl
from typing import Dict, Optional, Set

from aiohttp.client import ClientSession


class Kubernetes:
    def __init__(self, api_server_url: Optional[str] = None) -> None:
        super().__init__()
        if api_server_url is None:
            self.api_server = "https://kubernetes.default.svc"
        self.service_account_path = "/var/run/secrets/kubernetes.io/serviceaccount"
        self.headers = None
        self.token = None
        self.ssl_context = None
        self._set_ssl_context()

    def _set_ssl_context(self):
        ca_file = f"{self.service_account_path}/ca.crt"
        if os.path.isfile(ca_file):
            self.ssl_context = ssl.create_default_context(cafile=ca_file)

    def _set_headers(self):
        if self.token is None:
            self.token = self._get_token()
        self.headers = {
            "Authorization": f"Bearer {self.token}",
        }

    def _get_token(self):
        token_path = f"{self.service_account_path}/token"
        token = None
        try:
            with open(token_path, 'r') as opened_file:
                token = opened_file.read()
        except FileNotFoundError:
            # TODO: switch print to logger
            print("file not exist")
        return token

    @classmethod
    def _extract_namespaces(cls, namespaces_info):
        namespaces = set()
        items = namespaces_info.get("items", [])
        for namespace in items:
            metadata = namespace.get("metadata", {})
            name = metadata.get("name")
            namespaces.add(name)
        return namespaces

    async def get_namespaces(self) -> Set[str]:
        if self.headers is None:
            self._set_headers()
        namespaces = set()
        async with ClientSession() as session:
            response = await session.get(
                f"{self.api_server}/api/v1/namespaces",
                headers=self.headers,
                ssl=self.ssl_context)
            namespaces_info = await response.json()
            namespaces = self._extract_namespaces(namespaces_info)
        return namespaces

    @classmethod
    def _get_pod_name(cls, pod_info):
        pod_name = None
        generate_name = pod_info.get("metadata", {}).get("generateName")
        if generate_name is not None:
            pod_name = "-".join(generate_name.split("-")[:-2])
        else:
            pod_name = pod_info.get("metadata", {}).get("name")
        return pod_name

    @classmethod
    def _get_versioned_images(cls, pod_info):
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

    async def get_images_with_tags(self, namespaces):
        images_with_tags = dict()
        if self.headers is None:
            self._set_headers()
        # TODO: in parallel
        async with ClientSession() as session:
            for namespace in namespaces:
                response = await session.get(
                    f"{self.api_server}/api/v1/namespaces/{namespace}/pods",
                    headers=self.headers,
                    ssl=self.ssl_context)
                pods_info = await response.json()
                versions = {
                    self._get_pod_name(item): self._get_versioned_images(item) for item in pods_info.get("items", [])
                }
                images_with_tags[namespace] = versions
        return images_with_tags

    async def get_helm_data(self):
        helm_data = dict()
        async with ClientSession() as session:
            response = await session.get(
                f"{self.api_server}/api/v1/secrets",
                headers=self.headers,
                ssl=self.ssl_context)
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
