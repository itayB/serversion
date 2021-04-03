import os

from aiohttp import web

from serversion.handlers.health_check_view import HealthCheckView
from serversion.handlers.versions_handler import VersionsView
from serversion.kubernetes import Kubernetes


class Webserver:
    @staticmethod
    def get_web_application():
        app = web.Application()
        app.add_routes([
            web.view('/', HealthCheckView),
            web.view('/api/v1/versions', VersionsView),
        ])
        app['kubernetes'] = Kubernetes()
        return app

    @staticmethod
    def run():
        app = Webserver.get_web_application()
        host = os.getenv("LISTENING_HOST")
        port = int(os.getenv("LISTENING_PORT", "80"))
        web.run_app(app, host=host, port=port)
