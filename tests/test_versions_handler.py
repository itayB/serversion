import copy
import unittest
from aiohttp.abc import Application
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from mock import AsyncMock
from serversion.app import Webserver


async def test_api_v1_versions_with_images(aiohttp_client):
    app = app = Webserver.get_web_application()
    helm_data = {
        "my-nc": {
            "serversion": {
                "version": "0.1.0",
                "appVersion": "1.16.0",
            },
        },
    }
    images_with_tags = {
        "my-nc": {
            "serversion": {
                "containers": {
                    "serversion": "serversion:latest"
                },
            },
        },
    }
    app["kubernetes"].get_namespaces = AsyncMock(return_value=set(["kube-system"]))
    app["kubernetes"].get_images_with_tags = AsyncMock(return_value=copy.deepcopy(images_with_tags))
    app["kubernetes"].get_helm_data = AsyncMock(return_value=helm_data)
    client = await aiohttp_client(app)
    response = await client.get("/api/v1/versions")
    assert response.status == 200
    images_with_tags["my-nc"]["serversion"].update(helm_data.get("my-nc").get("serversion"))
    assert await response.json() == images_with_tags


async def test_api_v1_versions_without_images(aiohttp_client):
    app = app = Webserver.get_web_application()
    helm_data = {
        "my-nc": {
            "serversion": {
                "version": "0.1.0",
                "appVersion": "1.16.0",
            },
        },
    }
    images_with_tags = {
        "my-nc": {
        },
    }
    app["kubernetes"].get_namespaces = AsyncMock(return_value=set(["kube-system"]))
    app["kubernetes"].get_images_with_tags = AsyncMock(return_value=copy.deepcopy(images_with_tags))
    app["kubernetes"].get_helm_data = AsyncMock(return_value=helm_data)
    client = await aiohttp_client(app)
    response = await client.get("/api/v1/versions")
    assert response.status == 200
    assert await response.json() == helm_data


class TestVersionsHandlerView(AioHTTPTestCase):
    async def get_application(self) -> Application:
        return Webserver.get_web_application()

    @unittest.skip("temoprary")
    @unittest_run_loop
    async def test_health_check(self):
        resp = await self.client.get("/api/v1/versions", data=None)
        assert resp.status == 200
