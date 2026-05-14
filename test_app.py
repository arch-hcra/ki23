import unittest
from app import app  

class TestHealthEndpoint(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_health_endpoint_returns_ok(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), "OK")

    def test_health_endpoint_method_not_allowed(self):
        response = self.app.post('/health')
        self.assertEqual(response.status_code, 405)

    def test_nonexistent_endpoint_returns_404(self):
        response = self.app.get('/nonexistent')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()