import os
import ssl
from mock import Mock
from serversion.kubernetes import Kubernetes


def mock_is_file(filename):
    if filename == "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt":
        return True
    return os.path.isfile(filename)


def test_set_ssl_context(monkeypatch):
    kubernetes = Kubernetes()
    monkeypatch.setattr(os.path, 'isfile', mock_is_file)
    ssl.create_default_context = Mock(return_value=None)
    kubernetes._set_ssl_context()
