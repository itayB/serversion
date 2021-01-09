from serversion.kubernetes import Kubernetes
from aiohttp import web
from aiohttp.abc import Request


# Path to ServiceAccount token
SERVICEACCOUNT = "/var/run/secrets/kubernetes.io/serviceaccount"

# Path to read this Pod's namespace
NAMESPACE = f"{SERVICEACCOUNT}/namespace"


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

    async def get(self):
        app = self.request.app
        kubernetes: Kubernetes = app['kubernetes']
        # namespace = self._get_namespace()
        # TODO: support compression
        cluster_versions = dict()
        namespaces = await kubernetes.get_namespaces()
        cluster_versions = await kubernetes.get_images_with_tags(namespaces)
        helm = await kubernetes.get_helm_data()
        versions = dict()
        for ns, charts in helm.items():
            for chart, versions in charts.items():
                if cluster_versions[ns].get(chart) is None:
                    cluster_versions[ns][chart] = dict()
                cluster_versions[ns][chart].update(versions)
        return web.json_response(cluster_versions)
