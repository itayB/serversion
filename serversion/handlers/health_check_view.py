from aiohttp import web
from aiohttp.abc import Request


class HealthCheckView(web.View):
    def __init__(self, request: Request) -> None:
        """
        This constructor is being fired per request
        :param request:
        """
        super().__init__(request)

    async def get(self):
        return web.json_response({})