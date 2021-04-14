from typing import Union, Any
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

	def __init__(self, headers: dict = None, body: bytes = None):
		self.headers = CaseInsensitiveDict(headers)
		if body is None:
			body = b''
		self.body = body

	def get_body(self) -> bytes:
		return self.body

	def get_json(self) -> dict:
		return loads(self.get_body().decode())


class Request(Message):
	
	def __init__(
		self, 
		method: str,
		path: str,
		headers: dict = None,
		route: dict = None,
		query: dict = None,
		body: bytes = None
	):
		super().__init__(headers, body)
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
