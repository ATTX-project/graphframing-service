import falcon
import unittest
import httpretty
import json
from falcon import testing
from ldframe.app import init_api
from ldframe.api.healthcheck import healthcheck_response
from mock import patch


class appHealthTest(testing.TestCase):
    """Testing GM prov function and initialize it for that purpose."""

    def setUp(self):
        """Setting the app up."""
        self.app = init_api()

    def tearDown(self):
        """Tearing down the app up."""
        pass


class TestProv(appHealthTest):
    """Testing if there is a health endoint available."""

    def test_create(self):
        """Test GET health message."""
        self.app
        pass

    @httpretty.activate
    def test_health_ok(self):
        """Test GET health is ok."""
        httpretty.register_uri(httpretty.GET, "http://localhost:4303/health", status=200)
        result = self.simulate_get('/health')
        assert(result.status == falcon.HTTP_200)

    @httpretty.activate
    def test_health_response(self):
        """Response to healthcheck endpoint."""
        httpretty.register_uri(httpretty.GET, "http://user:password@localhost:15672/api/aliveness-test/%2F", body='{"status": "ok"}', status=200)
        httpretty.register_uri(httpretty.GET, "http://localhost:4303/health", status=200)
        response = healthcheck_response("Running")
        result = self.simulate_get('/health')
        json_response = {"framingService": "Running", "messageBroker": "Running"}
        assert(json_response == json.loads(response))
        assert(result.content == response)

    @patch('ldframe.api.healthcheck.healthcheck_response')
    def test_actual_health_response(self, mock):
        """Test if json response format."""
        mock.return_value = {"framingService": "Running", "messageBroker": "Not Running"}
        response = healthcheck_response("Running")
        json_response = {"framingService": "Running", "messageBroker": "Not Running"}
        assert(json_response == json.loads(response))


if __name__ == "__main__":
    unittest.main()
