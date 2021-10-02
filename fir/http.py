from typing import Union, Any
from urllib.parse import urlparse, parse_qs
from json import loads
from . import wsgi


STATUS_MESSAGES = {
	200: "OK",
	201: "Created",
	204: "No Content",
	301: "Moved Permanently",
	302: "Found",
	304: "Not Modified",
	401: "Unauthorized",
	403: "Forbidden",
	404: "Not Found",
	405: "Method Not Allowed",
	500: "Internal Server Error",
	503: "Service Unavailable"
}


class CaseInsensitiveDict(dict):

	__slots__ = []

	def __init__(self, data: dict):
		if data is None:
			data = {}
		super().__init__({
			k.lower(): ",".join(list(map(lambda x: str(x), v)))
			if isinstance(v, list) else str(v)
			for k, v in data.items()
		})

	def __setitem__(self, key, value):
		super().__setitem__(key.lower(), value)

	def __getitem__(self, key):
		return super().__getitem__(key.lower())

	def get(self, key: str, default: Any = None):
		try:
			return self[key]
		except KeyError:
			return default


class Message:

	__slots__ = ["headers", "body"]

	def __init__(self, headers: dict = None, body: Union[bytes, str] = None):
		self.headers = CaseInsensitiveDict(headers)
		self.set_body(body)

	def set_body(self, value: Union[bytes, str]):
		if value is None:
			value = b''
		elif isinstance(value, str):
			value = value.encode()
		self.body = value

	def get_body(self) -> bytes:
		return self.body

	def get_json(self) -> dict:
		return loads(self.get_body().decode())


class Request(Message):

	__slots__ = ["method", "_path", "route_params", "query_params"]

	def __init__(
		self, 
		method: str,
		path: str = None,
		headers: dict = None,
		route: dict = None,
		query: dict = None,
		body: bytes = None,
		uri: str = None
	):
		super().__init__(headers, body)
		if path is None and uri is None:
			raise ValueError("At least one argument between 'uri' or 'path' is required.")
		if uri is not None:
			parsed_url = urlparse(uri)
			path = parsed_url.path
			query = {k: ",".join(v) for k, v in parse_qs(parsed_url.query).items()}
		self.method = method
		self._path = path
		self.route_params = CaseInsensitiveDict(route)
		self.query_params = CaseInsensitiveDict(query)

	@property
	def path(self):
		return self._path.format(**self.route_params)

	@property
	def uri(self):
		q = self.query
		if q != "":
			q = "?" + q
		return self.path + q

	@property
	def query(self):
		return "&".join(["{}={}".format(k, v) for k, v in self.query_params.items()])

	@classmethod
	def from_wsgi_environ(cls, environ: dict):
		return wsgi.environ_to_request(environ, cls)


class Response(Message):

	__slots__ = ["status_code", "status_message"]

	def __init__(
		self,
		status_code: int = 200,
		status_message: str = None, 
		headers: dict = None,
		body: bytes = None
	):
		super().__init__(headers, body)
		if status_message is None:
			status_message = STATUS_MESSAGES.get(status_code, " ")
		self.status_code = status_code
		self.status_message = status_message
