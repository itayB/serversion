import asyncio
import os
import ssl
from mock import Mock
from aiohttp.client import ClientSession
from serversion.kubernetes import Kubernetes


def mock_is_file(filename):
    if filename == "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt":
        return True
    return os.path.isfile(filename)


def test_api_server_url():
    unique_api_server_url = "https://unique-kubernetes.default.svc"
    kubernetes = Kubernetes(unique_api_server_url)
    assert kubernetes.api_server == unique_api_server_url


def test_set_ssl_context(monkeypatch):
    kubernetes = Kubernetes()
    monkeypatch.setattr(os.path, 'isfile', mock_is_file)
    ssl.create_default_context = Mock(return_value=None)
    kubernetes._set_ssl_context()


async def mock_get(self, url, headers, ssl):  # pylint: disable=unused-argument,redefined-outer-name
    class MockJson:
        @classmethod
        def json(cls):
            future = asyncio.Future()
            future.set_result({})
            return future
    return MockJson()


async def test_get_namespaces(monkeypatch):
    kubernetes = Kubernetes()
    monkeypatch.setattr(ClientSession, 'get', mock_get)
    namespaces = await kubernetes.get_namespaces()
    assert namespaces == set()
