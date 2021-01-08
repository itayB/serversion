import unittest
from unittest import mock
from unittest.mock import ANY

from serversion.app import Webserver


class TestApp(unittest.TestCase):

    @classmethod
    @mock.patch("aiohttp.web.run_app")
    def test_app_run(cls, run_app_mock):
        Webserver.run()
        run_app_mock.assert_called_with(ANY, host="0.0.0.0", port=80)
