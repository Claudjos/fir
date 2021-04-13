from typing import Iterable, Callable
from io import BytesIO
from . import http


def request_to_environ(request: http.Request) -> dict:

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
		"SERVER_NAME": "Fir",
	}

	if body != b'':
		environ["CONTENT_LENGTH"] = len(body)
		if request.headers.get("content-type") is not None:
			environ["CONTENT_TYPE"] = request.headers.get("content-type", "*/*")

	for header_name, value in request.headers.items():
		key = "HTTP_{}".format(header_name.upper().replace("-", "_"))
		environ[key] = value
	
	return environ


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
