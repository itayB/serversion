import unittest

from aiohttp.abc import Application
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from serversion.app import Webserver


class TestVersionsHandlerView(AioHTTPTestCase):
    async def get_application(self) -> Application:
        return Webserver.get_web_application()

    @unittest.skip("temoprary")
    @unittest_run_loop
    async def test_health_check(self):
        resp = await self.client.get("/api/v1/versions", data=None)
        assert resp.status == 200
