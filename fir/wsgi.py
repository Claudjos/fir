from typing import Iterable, Callable
from io import BytesIO
from . import http


def request_to_environ(request: http.Request, server_name: str = "") -> dict:
	"""
	Converts a HTTP request into a WSGI environ dictionary.

	ARGS:
		- request: a HTTP request.

	RETURNS:
		A WSGI dictionary.

	"""
	if request.headers.get("host") is None:
		request.headers["host"] = ""

	body = request.get_body()
	
	environ = {
		"wsgi.input": BytesIO(body),
		"wsgi.url_scheme": "http",
		"REQUEST_METHOD": request.method,
		"PATH_INFO": request.path,
		"RAW_URI": request.uri,
		"QUERY_STRING": request.query,
		"SERVER_NAME": server_name,
	}

	if body != b'':
		environ["CONTENT_LENGTH"] = len(body)
		if request.headers.get("content-type") is not None:
			environ["CONTENT_TYPE"] = request.headers.get("content-type", "*/*")

	for header_name, value in request.headers.items():
		key = "HTTP_{}".format(header_name.upper().replace("-", "_"))
		environ[key] = value
	
	return environ


def environ_to_request(environ: dict, request_class = None) -> http.Request:
	"""
	Converts a WSGI environ dictionary into a HTTP request.

	ARGS:
		- environ: WSGI environ dictionary;
		- request_class: the class to instantiate to build a request, default
			to fir.http.Request.

	RETURNS:
		A HTTP request.

	"""
	if request_class is None:
		request_class = http.Request

	headers = {}
	for key in environ:
		if key.startswith("HTTP_"):
			headers[key.replace("HTTP_", "").replace("_", "-").lower()] = environ[key]
	try:
		request_body_size = int(environ.get('CONTENT_LENGTH', 0))
	except (ValueError):
		request_body_size = 0

	return request_class(
		method=environ["REQUEST_METHOD"].upper(),
		uri=environ["RAW_URI"],
		headers=headers,
		body=environ['wsgi.input'].read(request_body_size)
	)


def output_to_response(status: str, headers: list, body: Iterable) -> http.Response:
	status_code, status_message = status.split(" ", 1)
	_headers = {k: v for k, v in headers}
	return http.Response(
		status_code=int(status_code),
		status_message=status_message,
		headers=_headers,
		body=b''.join([i for i in body])
	)


class Client:

	def __init__(self, wsgi_app: Callable):
		self.wsgi_app = wsgi_app

	def request(self, req: http.Request) -> http.Response:
		call = WSGICall(self.wsgi_app)
		call.execute(request_to_environ(req))
		return output_to_response(call.status, call.headers, call.body)


class WSGICall:

	def __init__(self, wsgi_app: Callable):
		self.wsgi_app = wsgi_app

	def start_response(self, status: str, headers: dict):
		self.status = status
		self.headers = headers

	def execute(self, environ: dict):
		self.body = self.wsgi_app(environ, self.start_response)
