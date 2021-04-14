from typing import Union, Any
from urllib.parse import urlparse, parse_qs
from json import loads


class CaseInsensitiveDict(dict):

	def __init__(self, data: dict):
		if data is None:
			data = {}
		super().__init__({k.lower(): v for k, v in data.items()})

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
		return self.path + "?" + self.query

	@property
	def query(self):
		return "&".join(["{}={}".format(k, v) for k, v in self.query_params.items()])


class Response(Message):

	def __init__(self, status_code: int, status_message: str, headers: dict, body: bytes):
		super().__init__(headers, body)
		self.status_code = status_code
		self.status_message = status_message
