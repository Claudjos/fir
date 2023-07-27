import unittest
from ddt import ddt, file_data
from fir import http, wsgi


@ddt
class FirTestCases(unittest.TestCase):

	@file_data("./data.yaml")
	def test_wsgi_conversion(self, request: dict, result: dict):
		"""
		Creates a HTTP request from an input dictionary, then converts it
		to WSGI environ and back to HTTP. Tests the new request against the
		expected result.
		"""
		req = http.Request(**request)
		env = wsgi.request_to_environ(req)
		parsed_req = wsgi.environ_to_request(env)

		if "method" in result:
			self.assertEqual(result["method"], parsed_req.method, "method mismatch")
		if "uri" in result:
			self.assertEqual(result["uri"], parsed_req.uri, "uri mismatch")
		if "path" in result:
			self.assertEqual(result["path"], parsed_req.path, "path mismatch")
		if "query" in result:
			self.assertEqual(result["query"], parsed_req.query_params, "query mismatch")
		if "headers" in result:
			self.assertEqual(result["headers"], parsed_req.headers, "headers mismatch")
		if "body" in result:
			self.assertEqual(result["body"], parsed_req.get_body().decode(), "body mismatch")
		if "length" in result:
			self.assertEqual(result["length"], len(parsed_req.get_body().decode()), "content-length mismatch")
