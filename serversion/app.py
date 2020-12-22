from aiohttp import web


class Webserver:

    @staticmethod
    def run():
        app = web.Application()
        web.run_app(app, host="0.0.0.0", port=80)
