import asyncio
import json
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


async def mock_get(self, url: str, headers, ssl):  # pylint: disable=unused-argument,redefined-outer-name
    class MockJson:
        @classmethod
        def json(cls):
            future = asyncio.Future()
            if url.endswith("pods"):
                result = {
                    "items": [{
                        "metadata": {
                            "generateName": "pod-name-1-1",
                        },
                        "spec": {
                            "containers": [{
                                "name": "container-name",
                                "image": "image-name",
                            }],
                        },
                    }],
                }
            elif url.endswith("secrets"):
                result = {
                    "items": [{
                        "type": "helm.sh/release.v1",
                    }],
                }
            else:
                result = {}
            future.set_result(result)
            return future
    return MockJson()


async def test_get_namespaces(monkeypatch):
    kubernetes = Kubernetes()
    monkeypatch.setattr(ClientSession, 'get', mock_get)
    namespaces = await kubernetes.get_namespaces()
    assert namespaces == set()


def test_set_headers():
    kubernetes = Kubernetes()
    kubernetes._set_headers()
    assert kubernetes.headers == {"Authorization": "Bearer None"}
    kubernetes.token = "test"
    kubernetes._set_headers()
    assert kubernetes.headers == {"Authorization": "Bearer test"}


async def test_get_images_with_tags(monkeypatch):
    kubernetes = Kubernetes()
    namespaces = set(["kube-system"])
    monkeypatch.setattr(ClientSession, 'get', mock_get)
    images_with_tags = await kubernetes.get_images_with_tags(namespaces)
    assert images_with_tags == {
        "kube-system": {
            "pod-name": {
                "containers": {
                    "container-name": "image-name",
                },
            },
        },
    }


async def test_get_helm_data(monkeypatch):
    kubernetes = Kubernetes()
    monkeypatch.setattr(ClientSession, 'get', mock_get)
    monkeypatch.setattr(json, 'loads', lambda _: {
        "chart": {
            "metadata": {
                "name": "release-name",
                "version": "1.0.0",
                "appVersion": "2.0.0",
            },
        },
        "namespace": "kube-system",
    })
    helm_data = await kubernetes.get_helm_data()
    assert helm_data == {
        "kube-system": {
            "release-name": {
                "appVersion": "2.0.0",
                "version": "1.0.0",
            },
        },
    }
