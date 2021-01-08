from aiohttp import web
from serversion.handlers.health_check_view import HealthCheckView
from serversion.handlers.versions_handler import VersionsView


class Webserver:
    @staticmethod
    def get_web_application():
        app = web.Application()
        app.add_routes([
            web.view('/', HealthCheckView),
            web.view('/api/v1/versions', VersionsView),
        ])
        return app

    @staticmethod
    def run():
        app = Webserver.get_web_application()
        web.run_app(app, host="0.0.0.0", port=80)
