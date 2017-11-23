import falcon
import unittest
import httpretty
import json
from falcon import testing
from ldframe.app import init_api
from ldframe.api.healthcheck import healthcheck_response


class appHealthTest(testing.TestCase):
    """Testing Frame API health."""

    def setUp(self):
        """Setting the app up."""
        self.app = init_api()

    def tearDown(self):
        """Tearing down the app up."""
        pass


class TestFrame(appHealthTest):
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
        httpretty.disable()
        httpretty.reset()

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
        httpretty.disable()
        httpretty.reset()


if __name__ == "__main__":
    unittest.main()
